"""Live AIS vessel-tracking route (AISStream)."""

from __future__ import annotations

from fastapi import APIRouter

from urja_setu_backend.config import settings
from urja_setu_backend.ingestion import ais

router = APIRouter(prefix="/api", tags=["ais"])


@router.get("/vessels")
async def vessels(force: bool = False) -> dict:
    """Live tanker/vessel positions near the chokepoints (cached 5 min)."""
    return await ais.get_vessels(settings.aisstream_api_key, force=force)
