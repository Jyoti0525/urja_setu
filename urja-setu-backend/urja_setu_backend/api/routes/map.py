"""Digital-twin map state routes."""

from __future__ import annotations

from fastapi import APIRouter

from urja_setu_backend.shared import demo_data
from urja_setu_backend.shared.schemas import MapState

router = APIRouter(prefix="/api", tags=["map"])


@router.get("/map", response_model=MapState)
def get_map() -> MapState:
    """Digital-twin base state: corridors, refineries, crude sources, live signals."""
    return demo_data.map_state()
