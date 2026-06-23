"""Demo-Mode seeded story (Sprint 0 stub).

This hard-codes a deterministic, reliable hero narrative so the frontend can
render the full signal -> simulate -> reroute flow before the real engine,
agents, and live feeds exist. From Sprint 3 the cascade numbers here get
replaced by urja_setu_backend.sim output; the *shape* of the data stays identical.

Values are approximate and illustrative; real cited figures land with the
deterministic engine. Geography is real.
"""

from __future__ import annotations

import time

from urja_setu_backend.shared.schemas import (
    Assumption,
    CascadeResult,
    Citation,
    Coordinate,
    Corridor,
    CrudeSource,
    MapState,
    Mode,
    ProcurementOption,
    Refinery,
    RiskLevel,
    RiskSignal,
    ScenarioInput,
    ScenarioResponse,
)

# --- Real geography: India's crude lifelines ------------------------------------

CORRIDORS: list[Corridor] = [
    Corridor(
        id="hormuz",
        name="Strait of Hormuz",
        path=[
            Coordinate(lat=26.57, lon=56.25), Coordinate(lat=25.5, lon=57.6),
            Coordinate(lat=24.8, lon=60.2), Coordinate(lat=24.0, lon=63.2),
            Coordinate(lat=23.2, lon=66.4), Coordinate(lat=22.7, lon=68.8),
            Coordinate(lat=22.47, lon=70.06),
        ],
        throughput_share=0.42,
        disruption_probability=0.12,
        risk_level=RiskLevel.moderate,
    ),
    Corridor(
        id="bab-el-mandeb",
        name="Bab-el-Mandeb / Red Sea",
        path=[
            Coordinate(lat=12.6, lon=43.3), Coordinate(lat=14.6, lon=42.2),
            Coordinate(lat=17.2, lon=40.4), Coordinate(lat=20.2, lon=38.2),
            Coordinate(lat=23.2, lon=36.4), Coordinate(lat=26.2, lon=34.7),
        ],
        throughput_share=0.10,
        disruption_probability=0.34,
        risk_level=RiskLevel.high,
    ),
    Corridor(
        id="cape-good-hope",
        name="Cape of Good Hope",
        path=[
            Coordinate(lat=-34.35, lon=18.47), Coordinate(lat=-30.0, lon=27.0),
            Coordinate(lat=-22.0, lon=38.0), Coordinate(lat=-12.0, lon=46.0),
            Coordinate(lat=0.0, lon=54.0), Coordinate(lat=10.0, lon=62.0),
            Coordinate(lat=18.0, lon=67.5), Coordinate(lat=22.28, lon=69.73),
        ],
        throughput_share=0.05,
        disruption_probability=0.02,
        risk_level=RiskLevel.low,
    ),
    Corridor(
        id="malacca",
        name="Strait of Malacca",
        path=[
            Coordinate(lat=2.5, lon=101.0), Coordinate(lat=5.5, lon=97.0),
            Coordinate(lat=7.5, lon=93.0), Coordinate(lat=10.0, lon=88.0),
            Coordinate(lat=13.5, lon=84.5), Coordinate(lat=17.69, lon=83.22),
        ],
        throughput_share=0.08,
        disruption_probability=0.05,
        risk_level=RiskLevel.low,
    ),
]

REFINERIES: list[Refinery] = [
    Refinery(id="jamnagar", name="Jamnagar", operator="Reliance", location=Coordinate(lat=22.47, lon=70.06),
             capacity_kbd=1240, grade_slate=["Arab Heavy", "Basrah", "Urals", "WTI Midland"]),
    Refinery(id="vadinar", name="Vadinar", operator="Nayara", location=Coordinate(lat=22.28, lon=69.73),
             capacity_kbd=405, grade_slate=["Arab Medium", "Urals", "Basrah"]),
    Refinery(id="mangalore", name="Mangalore (MRPL)", operator="MRPL", location=Coordinate(lat=12.92, lon=74.86),
             capacity_kbd=300, grade_slate=["Arab Light", "Arab Heavy"]),
    Refinery(id="paradip", name="Paradip", operator="IOCL", location=Coordinate(lat=20.27, lon=86.61),
             capacity_kbd=300, grade_slate=["Basrah Heavy", "Arab Heavy", "Urals"]),
    Refinery(id="visakh", name="Visakhapatnam", operator="HPCL", location=Coordinate(lat=17.69, lon=83.22),
             capacity_kbd=300, grade_slate=["Arab Light", "Urals"]),
]

SOURCES: list[CrudeSource] = [
    CrudeSource(id="iraq-basrah", country="Iraq", grade="Basrah", location=Coordinate(lat=29.5, lon=48.5), spot_price_usd=80.1),
    CrudeSource(id="saudi-arabheavy", country="Saudi Arabia", grade="Arab Heavy", location=Coordinate(lat=26.0, lon=50.0), spot_price_usd=81.4),
    CrudeSource(id="russia-urals", country="Russia", grade="Urals", location=Coordinate(lat=43.3, lon=39.9), spot_price_usd=68.2),
    CrudeSource(id="us-wti", country="USA", grade="WTI Midland", location=Coordinate(lat=29.3, lon=-94.8), spot_price_usd=83.0),
    CrudeSource(id="nigeria-bonny", country="Nigeria", grade="Bonny Light", location=Coordinate(lat=4.4, lon=7.2), spot_price_usd=84.6),
]

SIGNALS: list[RiskSignal] = [
    RiskSignal(
        id="sig-001",
        corridor_id="bab-el-mandeb",
        headline="Houthi forces claim drone strike on tanker in southern Red Sea",
        severity=0.62,
        detected_at="2026-06-21T08:14:00Z",
        citations=[Citation(source="GDELT", title="Red Sea shipping incident reported", published="2026-06-21")],
    ),
]

# --- Scenarios ------------------------------------------------------------------

_SCENARIOS = {
    "hormuz-50": ScenarioInput(
        scenario_id="hormuz-50",
        label="Strait of Hormuz — 50% closure",
        description="Partial closure of Hormuz disrupts ~50% of transiting crude volume.",
    ),
    "redsea-suspend": ScenarioInput(
        scenario_id="redsea-suspend",
        label="Red Sea shipping suspension",
        description="Major carriers suspend Red Sea transit; reroute via Cape of Good Hope.",
    ),
}


def list_scenarios() -> list[ScenarioInput]:
    return list(_SCENARIOS.values())


def map_state() -> MapState:
    return MapState(corridors=CORRIDORS, refineries=REFINERIES, sources=SOURCES, signals=SIGNALS)


def _seeded_cascade(scenario_id: str) -> tuple[CascadeResult, list[Assumption], list[ProcurementOption]]:
    """Hard-coded deterministic outputs for the demo. Replaced by urja_setu_backend.sim in Sprint 3."""
    if scenario_id == "hormuz-50":
        assumptions = [
            Assumption(key="hormuz_share", label="Crude transiting Hormuz", value=42.0, unit="%",
                       source="EIA / PPAC import routing estimates"),
            Assumption(key="closure_pct", label="Volume disrupted by closure", value=50.0, unit="%",
                       source="Scenario input (editable)"),
            Assumption(key="price_elasticity", label="Brent sensitivity to supply shock", value=0.38, unit="% per % gap",
                       source="Calibrated to 2025 US-Iran standoff (~8% on threat)"),
            Assumption(key="reroutable", label="Share of at-risk volume reroutable", value=55.0, unit="%",
                       source="Tanker availability + Cape route feasibility"),
        ]
        cascade = CascadeResult(
            supply_gap_kbd=612.0,
            price_impact_pct=8.1,
            brent_projected_usd=88.6,
            refinery_runrate_pct=92.0,
            spr_cover_days=7.1,
            notes=[
                "West-coast refineries (Jamnagar, Vadinar) most exposed via Hormuz.",
                "55% of at-risk barrels reroutable within tanker/port constraints.",
            ],
        )
        options = [
            ProcurementOption(rank=1, source_country="Russia", grade="Urals", route_name="Novorossiysk -> Cape -> Vadinar",
                              transit_days=34, delivered_cost_usd_bbl=74.5, grade_compatible=True,
                              rationale="Discounted Urals; grade-compatible with Vadinar/Jamnagar; avoids Hormuz."),
            ProcurementOption(rank=2, source_country="Nigeria", grade="Bonny Light", route_name="Bonny -> Cape -> Jamnagar",
                              transit_days=22, delivered_cost_usd_bbl=86.9, grade_compatible=True,
                              rationale="Atlantic-basin sweet crude; no Hormuz/Red Sea exposure; faster than Russian routing."),
            ProcurementOption(rank=3, source_country="USA", grade="WTI Midland", route_name="USGC -> Cape -> Jamnagar",
                              transit_days=38, delivered_cost_usd_bbl=89.2, grade_compatible=True,
                              rationale="Reliable supplier; in Jamnagar grade slate; higher delivered cost and transit time."),
        ]
        return cascade, assumptions, options

    # redsea-suspend (lighter seed)
    assumptions = [
        Assumption(key="redsea_share", label="Crude transiting Red Sea", value=10.0, unit="%",
                   source="EIA / PPAC import routing estimates"),
        Assumption(key="price_elasticity", label="Brent sensitivity to supply shock", value=0.38, unit="% per % gap",
                   source="Calibrated to 2025 US-Iran standoff"),
    ]
    cascade = CascadeResult(
        supply_gap_kbd=180.0, price_impact_pct=2.4, brent_projected_usd=83.9,
        refinery_runrate_pct=98.0, spr_cover_days=9.0,
        notes=["Reroute via Cape adds ~10-14 days transit; manageable with inventory buffer."],
    )
    options = [
        ProcurementOption(rank=1, source_country="Iraq", grade="Basrah", route_name="Basrah -> Hormuz -> Paradip",
                          transit_days=12, delivered_cost_usd_bbl=80.8, grade_compatible=True,
                          rationale="Hormuz route unaffected by Red Sea suspension; shortest transit."),
    ]
    return cascade, assumptions, options


def run_scenario(scenario_id: str) -> ScenarioResponse | None:
    scenario = _SCENARIOS.get(scenario_id)
    if scenario is None:
        return None
    start = time.perf_counter()
    cascade, assumptions, options = _seeded_cascade(scenario_id)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return ScenarioResponse(
        scenario=scenario,
        assumptions=assumptions,
        cascade=cascade,
        procurement_options=options,
        response_time_ms=round(elapsed_ms, 2),
        mode=Mode.demo,
    )
