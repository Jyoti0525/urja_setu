# urja-setu-agents

The LangGraph multi-agent layer for URJA-SETU. **Language & orchestration only** — agents
extract signals, explain, and orchestrate. They never compute the numbers a judge sees;
that is the deterministic engine's job (`urja-setu-backend/.../sim`).

## Planned agents (Sprint 2–3)
| Agent | Role |
|---|---|
| **Risk Intelligence** | Relevance-filter + entity-ground GDELT/sanctions/price signals → structured risk inputs |
| **Scenario Simulation** | Wrap the deterministic engine; narrate results; expose editable assumptions |
| **Procurement Orchestrator** | Traverse the knowledge graph → rank executable reroute/alternative-source options |
| **SPR Optimiser** | Drawdown schedule vs supply gap + replenishment window |

## Reliability rules
- Structured output via JSON-schema / tool-calling + validation + retry.
- LLM: Groq free API (Llama 3.3 70B) primary · Ollama local fallback.
