"""Scenario service — deterministic cascade + knowledge-graph procurement.

Combines the cascade engine (numbers) with the Procurement Orchestrator agent
(KG ranking + LLM rationale) into one ScenarioResponse.
"""

from __future__ import annotations

import time

from urja_setu_agents.llm import LLMClient
from urja_setu_agents.procurement_agent import build_procurement_graph

from urja_setu_backend.config import settings
from urja_setu_backend.ingestion import prices
from urja_setu_backend.kg import graph as kg
from urja_setu_backend.shared.schemas import (
    Mode,
    ProcurementOption,
    ScenarioInput,
    ScenarioResponse,
    SprPlan,
)
from urja_setu_backend.sim import cascade, spr

_proc_graph = None


def _get_proc_graph():
    global _proc_graph
    if _proc_graph is None:
        llm = LLMClient(
            groq_api_key=settings.groq_api_key,
            gemini_api_key=settings.gemini_api_key,
            ollama_base_url=settings.ollama_base_url,
        )
        _proc_graph = build_procurement_graph(llm, kg.alternative_sources)
    return _proc_graph


def simulate_scenario(scenario_id: str, overrides: dict | None = None) -> ScenarioResponse:
    if scenario_id not in cascade.SCENARIOS:
        raise KeyError(scenario_id)

    t0 = time.perf_counter()
    brent = prices.brent_snapshot().get("price")

    result, assumptions = cascade.simulate(scenario_id, overrides=overrides, brent_usd=brent)

    s = cascade.SCENARIOS[scenario_id]
    state = _get_proc_graph().invoke(
        {"blocked": s["corridor_id"], "brent": brent, "scenario_label": s["label"]}
    )
    ranked = state.get("ranked", []) or []
    rationales = state.get("rationales", {}) or {}

    options: list[ProcurementOption] = []
    for i, a in enumerate(ranked):
        options.append(
            ProcurementOption(
                rank=i + 1,
                source_country=a["country"],
                grade=a["grade"],
                route_name=f'{a["country"]} {a["grade"]} via {a.get("route_label", a["corridor"])}',
                transit_days=float(a["transit_days"]),
                delivered_cost_usd_bbl=float(a["delivered_usd_bbl"]),
                grade_compatible=bool(a["grade_compatible"]),
                rationale=rationales.get(a["id"], ""),
            )
        )

    # Strategic reserve drawdown plan (first reroute ETA = fastest ranked option).
    first_eta = options[0].transit_days if options else 30.0
    spr_plan = SprPlan(**spr.optimize(result.supply_gap_kbd, first_eta))

    return ScenarioResponse(
        scenario=ScenarioInput(scenario_id=scenario_id, label=s["label"], description=s["description"]),
        assumptions=assumptions,
        cascade=result,
        procurement_options=options,
        response_time_ms=round((time.perf_counter() - t0) * 1000, 1),
        mode=Mode.live,
        affected_corridor=s["corridor_id"],
        spr_plan=spr_plan,
    )
