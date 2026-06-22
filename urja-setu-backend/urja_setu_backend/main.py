"""URJA-SETU API gateway (FastAPI).

Sprint 0: health + Demo-Mode endpoints serving the seeded hero story.
Later sprints add live feeds, the agent orchestrator, the deterministic engine,
the knowledge graph, and the backtest/metrics routes.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from urja_setu_backend.api.routes import ais, live
from urja_setu_backend.api.routes import map as map_routes
from urja_setu_backend.api.routes import metrics, scenarios, system
from urja_setu_backend.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="AI-Driven Energy Supply Chain Resilience — Phase 2 PoC",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(system.router)
    app.include_router(map_routes.router)
    app.include_router(scenarios.router)
    app.include_router(live.router)
    app.include_router(metrics.router)
    app.include_router(ais.router)
    return app


app = create_app()
