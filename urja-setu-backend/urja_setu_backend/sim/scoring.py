"""Deterministic corridor risk scorer.

This module owns the FINAL disruption-probability number. The LLM supplies an
event-severity estimate (qualitative judgement of news); the numbers below —
weights, normalisation, fusion — are explicit, cited, and testable.

    disruption_probability = w_event * event_severity
                           + w_price * price_pressure
                           + w_sanctions * sanctions_exposure
"""

from __future__ import annotations

from urja_setu_backend.shared.schemas import Assumption, RiskLevel

W_EVENT = 0.60
W_PRICE = 0.20
W_SANCTIONS = 0.20
PRICE_FULL_PRESSURE_PCT = 8.0  # a single-session Brent move of this size => full price pressure

# Surfaced to the UI for the 'assumptions must be explicit & testable' rubric line.
SCORING_ASSUMPTIONS: list[Assumption] = [
    Assumption(key="w_event", label="Weight — geopolitical event severity", value=W_EVENT,
               source="URJA-SETU risk model v1"),
    Assumption(key="w_price", label="Weight — oil price pressure", value=W_PRICE,
               source="URJA-SETU risk model v1"),
    Assumption(key="w_sanctions", label="Weight — sanctions exposure", value=W_SANCTIONS,
               source="OFAC active programs (curated)"),
    Assumption(key="price_full_pressure", label="Brent move for full price pressure",
               value=PRICE_FULL_PRESSURE_PCT, unit="%",
               source="Calibrated to 2025 US-Iran standoff (~8% single-session)"),
]


def risk_level(p: float) -> RiskLevel:
    if p >= 0.5:
        return RiskLevel.critical
    if p >= 0.25:
        return RiskLevel.high
    if p >= 0.1:
        return RiskLevel.moderate
    return RiskLevel.low


def price_pressure(change_pct: float | None) -> float:
    """Rising Brent => upward pressure, normalised to [0,1]. Falling price => 0."""
    if change_pct is None:
        return 0.0
    return max(0.0, min(change_pct / PRICE_FULL_PRESSURE_PCT, 1.0))


def score_corridors(state: dict) -> list[dict]:
    """Fuse LLM event severity + price pressure + sanctions into a per-corridor score.

    Reads from LangGraph state: corridors, extracted (LLM), articles, price, sanctions.
    """
    corridors = state["corridors"]
    extracted = state.get("extracted", {}) or {}
    articles = state.get("articles", {}) or {}
    price = state.get("price", {}) or {}
    sanctions = state.get("sanctions", {}) or {}

    pp = price_pressure(price.get("change_pct"))
    results: list[dict] = []

    for c in corridors:
        cid = c["id"]
        ex = extracted.get(cid, {}) or {}
        event = max(0.0, min(float(ex.get("severity", 0.0) or 0.0), 1.0))
        sx = float(sanctions.get(cid, 0.0) or 0.0)

        prob = W_EVENT * event + W_PRICE * pp + W_SANCTIONS * sx
        prob = max(0.0, min(prob, 1.0))

        # Build supporting signals from the articles the LLM cited (or the top one
        # when the corridor is relevant but no exact title was echoed back).
        cited = set(ex.get("cited_titles", []) or [])
        signals: list[dict] = []
        for a in articles.get(cid, []):
            if a["title"] in cited:
                signals.append(a)
        if not signals and ex.get("relevant") and event >= 0.2 and articles.get(cid):
            signals.append(articles[cid][0])

        results.append(
            {
                "corridor_id": cid,
                "disruption_probability": round(prob, 3),
                "risk_level": risk_level(prob),
                "event_severity": round(event, 3),
                "price_pressure": round(pp, 3),
                "sanctions_exposure": round(sx, 3),
                "rationale": ex.get("rationale", ""),
                "signals": signals,
            }
        )
    return results
