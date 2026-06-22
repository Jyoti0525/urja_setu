"""Live intelligence routes — real GDELT/price/sanctions + Risk Agent."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from urja_setu_backend.services import risk_service
from urja_setu_backend.shared.schemas import LiveMapResponse

router = APIRouter(prefix="/api", tags=["live"])


@router.get("/risk/live", response_model=LiveMapResponse)
def risk_live() -> LiveMapResponse:
    """Run the Risk Intelligence Agent on live signals and return scored corridors."""
    try:
        return risk_service.run_live_risk()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"live risk failed: {e}")
