"""Disruption-scenario routes (signal -> cascade -> procurement)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from urja_setu_backend.services import scenario_service
from urja_setu_backend.shared import demo_data
from urja_setu_backend.shared.schemas import ScenarioInput, ScenarioResponse
from urja_setu_backend.sim import cascade

router = APIRouter(prefix="/api", tags=["scenarios"])


class SimulateRequest(BaseModel):
    scenario_id: str
    overrides: dict | None = None


# --- Computed scenarios (deterministic engine + KG procurement) ----------------


@router.get("/scenario/list", response_model=list[ScenarioInput])
def scenario_list() -> list[ScenarioInput]:
    return cascade.list_scenarios()


@router.post("/scenario/simulate", response_model=ScenarioResponse)
def scenario_simulate(req: SimulateRequest) -> ScenarioResponse:
    """Run the deterministic cascade + Procurement Orchestrator for a scenario.

    `overrides` may tweak editable assumptions (e.g. {"reroutable_share": 0.2}).
    """
    try:
        return scenario_service.simulate_scenario(req.scenario_id, req.overrides)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown scenario '{req.scenario_id}'")


# --- Seeded Demo Mode (fallback / offline-reliable) ----------------------------


@router.get("/scenarios", response_model=list[ScenarioInput])
def list_scenarios() -> list[ScenarioInput]:
    return demo_data.list_scenarios()


@router.get("/demo/scenario/{scenario_id}", response_model=ScenarioResponse)
def run_demo_scenario(scenario_id: str) -> ScenarioResponse:
    """Run a seeded disruption scenario in Demo Mode."""
    result = demo_data.run_scenario(scenario_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Unknown scenario '{scenario_id}'")
    return result
