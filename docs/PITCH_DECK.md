# URJA-SETU — Pitch Deck (slide-by-slide)

> ET AI Hackathon 2.0 · Finale. Suggested 12 slides / ~6 min. Speaker notes in _italics_.

---

### Slide 1 — Title
**URJA-SETU** · *Energy Supply Chain Resilience, as a decision system.*
"Turning a geopolitical oil shock from a 47-day scramble into a managed, hour-by-hour response."
_Team, 1 line. Logo + the live war-room screenshot._

### Slide 2 — The stakes (Business Impact)
- India imports **~88%** of its crude; **40–45%** transits the **Strait of Hormuz**.
- Strategic reserves = **~9.5 days**. A sustained disruption exhausts the buffer fast.
- McKinsey: economies without automated rerouting took **+47 days** longer to stabilise.
_This is national-security-grade economics — ET's home turf._

### Slide 3 — The gap
"The data exists. The **intelligence layer to act on it** does not."
Traditional supply-chain tools can't model geopolitical scenarios in real time, evaluate
alternative corridors, or orchestrate a coordinated response. _That layer is what we built._

### Slide 4 — What URJA-SETU is
A real-time **digital twin** of India's crude network + an **agentic** brain that:
1. **detects** disruption signals early, 2. **simulates** their economic cascade,
3. **orchestrates** procurement rerouting — all **provably**, on open infrastructure.

### Slide 5 — Live demo handoff
_Switch to the app. Run the 3-beat demo (see DEMO_SCRIPT.md): Go Live → Simulate → Backtest._

### Slide 6 — Innovation: the deterministic-core bet
Most "AI" demos let an LLM hallucinate the numbers. **We don't.**
- **Deterministic engine** owns every number (cited, editable equations).
- **LLM** owns only language: extraction, rationale, narrative.
- This is exactly what the rubric demands: *assumptions explicit & testable*.

### Slide 7 — The agents are real (Technical Excellence)
Two **LangGraph** state machines, Groq Llama 3.3 70B, JSON-validated + retried:
- **Risk Intelligence Agent**: GDELT + Brent + sanctions → scored corridors with citations.
- **Procurement Orchestrator**: NetworkX **knowledge graph** → ranked, executable reroutes.

### Slide 8 — We prove it (the differentiator)
**Backtest on real history (GDELT, 2024–26):** detected disruption events an average of
**~8–10 days early**, vs a no-early-warning baseline. _Most teams assert accuracy; we measured it._

### Slide 9 — Business model & users
- **Buyers:** MoP&NG / PPAC, OMCs (IOCL/BPCL/HPCL), private refiners, ISPRL, trading desks.
- **Value:** days shaved off response = avoided spot-premium + fiscal/strategic protection.
- **GTM:** pilot one OMC risk desk → expand to LNG/coal and other import-dependent economies.

### Slide 10 — Scalability
Event-driven ingestion · modular agents (add commodities/countries by config) ·
NetworkX→Neo4j · stateless gateway · **zero vendor lock-in (100% free/open stack)**.

### Slide 11 — UX
An analyst **war-room**: one glanceable map, explainability everywhere (citations, confidence,
editable assumptions), live latency/lead-time badges. Built for decisions under time pressure.

### Slide 12 — Close
"From reactive chaos to a managed, evidence-backed response — built in a sprint, on open infra,
and **proven on history**." _Ask + thank you._

---

## Mapping to judging criteria
| Criterion | Where we win | Slides |
|---|---|---|
| Innovation 25% | deterministic-core + closed-loop digital twin | 4, 6, 8 |
| Business Impact 25% | national energy security, quantified ROI, clear buyers | 2, 9 |
| Technical Excellence 20% | real multi-agent LangGraph + KG + deterministic engine + backtest | 6, 7, 8 |
| Scalability 15% | modular, open, event-driven | 10 |
| User Experience 15% | war-room, explainability, editable assumptions | 5, 11 |
