"""Backtest / metrics routes — proven detection lead-time + precision/recall."""

from __future__ import annotations

from fastapi import APIRouter

from urja_setu_backend.backtest import harness

router = APIRouter(prefix="/api", tags=["metrics"])


@router.get("/backtest")
def backtest() -> dict:
    """Cached backtest results (lead-time, precision/recall over historical events)."""
    return harness.run_backtest()
