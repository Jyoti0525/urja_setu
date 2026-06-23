"""Shared domain contract for URJA-SETU.

These pydantic models are the single source of truth shared by the API, the
deterministic simulation engine, the agents, and the frontend (mirrored in TS).
Every field that becomes a *number on screen* is owned by the deterministic
engine (urja_setu_backend.sim) — never invented by an LLM.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    low = "low"
    moderate = "moderate"
    high = "high"
    critical = "critical"


class Mode(str, Enum):
    demo = "demo"
    live = "live"


class Coordinate(BaseModel):
    lat: float
    lon: float


class Citation(BaseModel):
    """Provenance for a signal — supports the 'explicit & testable' rubric line."""

    source: str
    title: str
    url: str | None = None
    published: str | None = None


class RiskSignal(BaseModel):
    id: str
    corridor_id: str
    headline: str
    severity: float = Field(ge=0.0, le=1.0)
    citations: list[Citation] = Field(default_factory=list)
    detected_at: str


class Corridor(BaseModel):
    """A maritime shipping corridor / chokepoint for crude transit."""

    id: str
    name: str
    path: list[Coordinate]
    chokepoint: Coordinate | None = None  # the actual chokepoint (marker), distinct from route ends
    throughput_share: float = Field(ge=0.0, le=1.0, description="Fraction of India's crude transiting here")
    disruption_probability: float = Field(default=0.0, ge=0.0, le=1.0)
    risk_level: RiskLevel = RiskLevel.low


class Refinery(BaseModel):
    id: str
    name: str
    operator: str
    location: Coordinate
    capacity_kbd: float = Field(description="Capacity in thousand barrels/day")
    grade_slate: list[str] = Field(default_factory=list, description="Crude grades it can process")


class CrudeSource(BaseModel):
    id: str
    country: str
    grade: str
    location: Coordinate
    spot_price_usd: float | None = None


class Assumption(BaseModel):
    """A named, sourced, editable model parameter. Fidelity = transparency."""

    key: str
    label: str
    value: float
    unit: str | None = None
    source: str
    editable: bool = True


class CascadeResult(BaseModel):
    """Deterministic downstream impacts of a disruption scenario."""

    supply_gap_kbd: float
    price_impact_pct: float
    brent_projected_usd: float
    refinery_runrate_pct: float
    spr_cover_days: float
    notes: list[str] = Field(default_factory=list)


class ProcurementOption(BaseModel):
    rank: int
    source_country: str
    grade: str
    route_name: str
    transit_days: float
    delivered_cost_usd_bbl: float
    grade_compatible: bool
    rationale: str


class SprStep(BaseModel):
    day: int
    drawdown_kbd: float
    reserve_kbd_days: float


class SprPlan(BaseModel):
    reserve_initial_kbd_days: float
    peak_drawdown_kbd: float
    first_reroute_days: float
    days_to_full_coverage: float
    reserve_remaining_kbd_days: float
    reserve_remaining_pct: float
    depletion_day: int | None = None
    verdict: str
    schedule: list[SprStep] = Field(default_factory=list)


class ScenarioInput(BaseModel):
    scenario_id: str
    label: str
    description: str | None = None


class ScenarioResponse(BaseModel):
    scenario: ScenarioInput
    assumptions: list[Assumption]
    cascade: CascadeResult
    procurement_options: list[ProcurementOption]
    response_time_ms: float
    mode: Mode = Mode.demo
    affected_corridor: str | None = None
    spr_plan: SprPlan | None = None


class MapState(BaseModel):
    corridors: list[Corridor]
    refineries: list[Refinery]
    sources: list[CrudeSource]
    signals: list[RiskSignal] = Field(default_factory=list)


class LiveMeta(BaseModel):
    """Provenance + transparency for a live risk run (supports the rubric)."""

    brent_usd: float | None = None
    brent_change_pct: float | None = None
    articles_scanned: int = 0
    response_time_ms: float = 0.0
    generated_at: str
    assumptions: list[Assumption] = Field(default_factory=list)
    mode: Mode = Mode.live


class LiveMapResponse(BaseModel):
    """Live digital-twin state: corridors scored from real signals, with provenance."""

    corridors: list[Corridor]
    refineries: list[Refinery]
    sources: list[CrudeSource]
    signals: list[RiskSignal]
    meta: LiveMeta


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    mode: Mode
