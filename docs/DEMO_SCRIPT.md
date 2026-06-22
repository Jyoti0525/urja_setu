# URJA-SETU — Demo Script (~4 minutes)

> For the live finale and the demo video. Three beats: **Detect → Simulate → Prove.**
> Before you start: click **Go Live** once to warm the GDELT cache, then refresh the page.

---

## Setup (10s, off-camera)
- Backend on `:6006`, frontend on `:4000`. Open `http://localhost:4000` full-screen.
- Pre-warm: click **Go Live** once (loads the live cache), then reload so you start clean.

## Beat 0 — The board (0:00–0:30)
> "This is India's crude supply network as a live digital twin — every lifeline a tanker
> corridor, every node a refinery. Hormuz alone carries ~42% of our imports."

_Pan/zoom the map. Point at Hormuz, the Red Sea, the Cape reroute, the refineries (Jamnagar…)._

## Beat 1 — Detect (0:30–1:30) → **Go Live**
> "URJA-SETU isn't a dashboard — it's an agent. Watch."

_Click **Go Live**._ While it scans:
> "A LangGraph agent is pulling live GDELT news, the live Brent price, and active OFAC
> sanctions — then Llama-3.3-70B grades each corridor's threat."

When it lands:
> "Corridors just re-scored from **real signals**, with the **source headlines** cited.
> Brent is live, top-right. And notice the latency badge — signal to score in seconds."

_Point at the corridor risk re-ordering, the Brent chip, the live signal cards._

## Beat 2 — Simulate (1:30–2:45) → **⚡ Simulate**
> "Now the question a minister actually asks: *what if Hormuz closes?*"

_Click **⚡ Simulate → Strait of Hormuz — 50% closure**._
> "Our **deterministic** engine — not the LLM — computes the cascade: a **444 kbd** supply
> gap, **+8%** on Brent, refinery run-rate down to 90%, and how long strategic reserves buy us."

_Open the **assumptions** — tweak 'reroutable share' down, hit **Re-simulate**._
> "Every assumption is explicit, sourced, and editable — change it and the math moves. That's
> auditable, not a black box."

_Scroll to procurement:_
> "And the **Procurement Orchestrator** has already walked our knowledge graph for executable
> alternatives — Russian Urals via Suez at $73 a barrel, grade-compatible with Jamnagar — each
> with the agent's rationale. Crisis to a ranked action plan, in seconds."

## Beat 3 — Prove (2:45–3:40) → **📊 Backtest**
> "Anyone can demo a happy path. So we tested it on **history**."

_Click **📊 Backtest**._
> "Against real GDELT attention data for 2024–2026, URJA-SETU's early-warning layer caught
> known Red Sea and Hormuz disruptions an average of **~8–10 days early** — versus zero warning
> for a traditional system. These sparklines show the attention spikes our alerts fired on,
> with the real events marked."

_Point at a caught event row ("caught · Nd early") and a sparkline spike._

## Close (3:40–4:00)
> "Real signals, auditable math, a knowledge-graph agent, and a backtest that proves it — built
> in a sprint, on a 100% free and open stack. URJA-SETU turns an energy shock from reactive
> chaos into a managed, evidence-backed response. Thank you."

---

## Safety nets (if live feeds hiccup on stage)
- **Go Live** rate-limited? It serves the 10-min cache — warm it before you present.
- Network down? **Demo Mode** seeded story still runs the full visual narrative.
- The **Backtest** is precomputed/cached — it never needs live GDELT during the demo.

## Numbers to have on your tongue
88% import dependence · 42% via Hormuz · 9.5 days SPR · +47 days without response intelligence ·
Hormuz-50 → +8% Brent / 444 kbd gap · backtest ~8–10 day lead-time.
