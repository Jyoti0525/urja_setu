"""Live risk service — wires real ingestion + the Risk Agent + the deterministic scorer.

This is the backend's orchestration seam: it injects real implementations into the
(decoupled) agent graph and assembles the API response.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone

from urja_setu_agents.llm import LLMClient
from urja_setu_agents.risk_agent import build_risk_graph

from urja_setu_backend.config import settings
from urja_setu_backend.ingestion import gdelt, prices, sanctions
from urja_setu_backend.shared import demo_data
from urja_setu_backend.shared.schemas import (
    Citation,
    Corridor,
    LiveMapResponse,
    LiveMeta,
    Mode,
    RiskSignal,
)
from urja_setu_backend.sim import scoring

_graph = None


def _fetch(corridors: list[dict]) -> dict:
    # One broad GDELT query, then bucket locally (rate-limit-safe).
    buckets = gdelt.bucket_by_corridor(gdelt.fetch_all())
    return {
        "articles": {c["id"]: buckets.get(c["id"], []) for c in corridors},
        "price": prices.brent_snapshot(),
        "sanctions": sanctions.corridor_exposure(),
    }


def _get_graph():
    global _graph
    if _graph is None:
        llm = LLMClient(
            groq_api_key=settings.groq_api_key,
            gemini_api_key=settings.gemini_api_key,
            ollama_base_url=settings.ollama_base_url,
        )
        _graph = build_risk_graph(llm, _fetch, scoring.score_corridors)
    return _graph


def _iso(seendate: str | None) -> str:
    if seendate and len(seendate) >= 15:
        s = seendate
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}T{s[9:11]}:{s[11:13]}:{s[13:15]}Z"
    return datetime.now(timezone.utc).isoformat()


def _date(seendate: str | None) -> str | None:
    if seendate and len(seendate) >= 8:
        return f"{seendate[0:4]}-{seendate[4:6]}-{seendate[6:8]}"
    return None


def run_live_risk() -> LiveMapResponse:
    t0 = time.perf_counter()
    base = {c.id: c for c in demo_data.CORRIDORS}
    corridors = [c.model_dump() for c in demo_data.CORRIDORS]

    result = _get_graph().invoke({"corridors": corridors})

    scored = result.get("scored", []) or []
    articles = result.get("articles", {}) or {}
    price = result.get("price", {}) or {}
    scanned = sum(len(v) for v in articles.values())

    out_corridors: list[Corridor] = []
    signals: list[RiskSignal] = []
    for s in scored:
        b = base[s["corridor_id"]]
        out_corridors.append(
            Corridor(
                id=b.id,
                name=b.name,
                path=b.path,
                throughput_share=b.throughput_share,
                disruption_probability=s["disruption_probability"],
                risk_level=s["risk_level"],
            )
        )
        for sig in s["signals"][:2]:
            signals.append(
                RiskSignal(
                    id=f"{b.id}-{len(signals)}",
                    corridor_id=b.id,
                    headline=sig["title"],
                    severity=s["event_severity"],
                    detected_at=_iso(sig.get("seendate")),
                    citations=[
                        Citation(
                            source=sig.get("domain") or "news",
                            title=sig["title"],
                            url=sig.get("url"),
                            published=_date(sig.get("seendate")),
                        )
                    ],
                )
            )
    signals.sort(key=lambda x: x.severity, reverse=True)

    meta = LiveMeta(
        brent_usd=price.get("price"),
        brent_change_pct=price.get("change_pct"),
        articles_scanned=scanned,
        response_time_ms=round((time.perf_counter() - t0) * 1000, 1),
        generated_at=datetime.now(timezone.utc).isoformat(),
        assumptions=scoring.SCORING_ASSUMPTIONS,
        mode=Mode.live,
    )
    return LiveMapResponse(
        corridors=out_corridors,
        refineries=demo_data.REFINERIES,
        sources=demo_data.SOURCES,
        signals=signals,
        meta=meta,
    )
