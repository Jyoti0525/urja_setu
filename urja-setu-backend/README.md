# urja-setu-backend

FastAPI gateway + the deterministic core of URJA-SETU.

**Design rule:** this service owns every **number** shown to a judge — produced by the
deterministic simulation engine (`sim/`), never invented by an LLM. The agent layer
(`urja-setu-agents`) handles language, extraction, and orchestration.

## Package layout
```
urja_setu_backend/
├── main.py            # FastAPI app factory
├── config.py          # settings (.env)
├── api/routes/        # system · map · scenarios
├── shared/            # pydantic schemas + Demo-Mode seeded story
├── sim/               # deterministic cascade engine        (Sprint 3)
├── kg/                # knowledge graph (NetworkX)          (Sprint 1/3)
├── ingestion/         # GDELT · prices · AIS · sanctions    (Sprint 2)
└── backtest/          # lead-time + precision/recall harness (Sprint 4)
```

## Run
```bash
# from urja-setu-backend/
python -m venv .venv && .venv\Scripts\Activate.ps1      # or use the repo-root .venv
pip install -r requirements.txt
copy .env.example .env
uvicorn urja_setu_backend.main:app --reload --port 6006
# → http://localhost:6006/health   ·   http://localhost:6006/docs
```
