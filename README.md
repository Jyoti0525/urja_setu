# URJA-SETU — AI-Driven Energy Supply Chain Resilience

> ET AI Hackathon 2.0 · Phase 2 PoC. An agentic early-warning + decision-support platform that turns a
> geopolitical oil shock from a 47-day reactive scramble into a managed, hour-by-hour, **evidence-backed** response.

**Core principle:** auditable math owns every number a judge sees; the LLM owns the words.
Full master plan: [`POC_PLAN.md`](./POC_PLAN.md).

## Repository layout
```
ET_AI_HACK/
├── urja-setu-frontend/    # Next.js 15 war-room UI (TypeScript · MapLibre/deck.gl)
├── urja-setu-backend/     # FastAPI gateway + deterministic sim + knowledge graph + ingestion + backtest
├── urja-setu-agents/      # LangGraph multi-agent layer (language & orchestration only)
├── data/                  # curated, cited domain datasets (refineries, grades, routes, chokepoints, SPR)
├── docs/                  # architecture diagram, deck assets
├── docker-compose.yml     # Postgres + pgvector · Redis
└── POC_PLAN.md            # master plan
```

## Stack (100% free / open-source)
- **Frontend:** Next.js 15 · TypeScript · Tailwind · MapLibre/deck.gl
- **Backend:** FastAPI · deterministic NumPy engine · NetworkX knowledge graph
- **Agents:** LangGraph · Groq free API (Llama 3.3 70B) · Ollama local fallback
- **Data stores:** Postgres + pgvector · Redis
- **Data:** GDELT · yfinance · AISStream · OFAC/EU/UN sanctions

## Quickstart (Sprint 0 skeleton)

### 1. Infrastructure (Postgres + Redis)
```bash
docker compose up -d
```

### 2. Backend (FastAPI)
```bash
# from repo root — reuse the root .venv, or make one per the backend README
.venv\Scripts\Activate.ps1
pip install -r urja-setu-backend/requirements.txt
cd urja-setu-backend
copy .env.example .env
uvicorn urja_setu_backend.main:app --reload --port 6006
# → http://localhost:6006/health   ·   http://localhost:6006/docs
```

### 3. Frontend (Next.js)
```bash
cd urja-setu-frontend
npm install
copy .env.local.example .env.local
npm run dev
# → http://localhost:4000
```

> Ports: frontend **4000**, backend **6006** (6000 is a browser-blocked port), agents **9000** (Sprint 2+).

Sprint status & roadmap: [`POC_PLAN.md`](./POC_PLAN.md) §8.
