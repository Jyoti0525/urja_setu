"""System / health routes."""

from __future__ import annotations

from fastapi import APIRouter

from urja_setu_backend.config import settings
from urja_setu_backend.shared.schemas import HealthResponse, Mode

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.version,
        mode=Mode(settings.mode),
    )
