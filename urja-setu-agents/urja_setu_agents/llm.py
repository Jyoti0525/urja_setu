"""Multi-provider LLM client with structured-JSON output and automatic fallback.

Provider order: Groq (Llama 3.3 70B) -> Gemini (free tier) -> Ollama (local).
If one provider errors or rate-limits, the next is tried — so a live demo can't die
on a single provider. The client does *language* work only (relevance filtering,
severity judgement, rationale); it never produces the final risk number.
"""

from __future__ import annotations

import json
import os

import httpx
from groq import Groq

GROQ_MODEL = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-2.5-flash"
OLLAMA_MODEL = "llama3.1"

_SYSTEM = (
    "You are an energy supply-chain geopolitical risk analyst for India's crude oil "
    "imports (India imports ~88% of its crude; ~40-45% transits the Strait of Hormuz). "
    "You assess whether recent news indicates a supply-disruption threat to specific "
    "maritime shipping corridors. Be precise and conservative — do not invent threats "
    "the headlines do not support. Respond with ONLY valid JSON, no prose."
)


class LLMClient:
    def __init__(
        self,
        groq_api_key: str | None = None,
        gemini_api_key: str | None = None,
        ollama_base_url: str = "http://localhost:11434",
    ):
        self._groq = Groq(api_key=groq_api_key) if groq_api_key else None
        self._gemini_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self._ollama = ollama_base_url

    # --- providers --------------------------------------------------------------

    def _groq_json(self, user: str, max_tokens: int) -> dict:
        resp = self._groq.chat.completions.create(  # type: ignore[union-attr]
            model=GROQ_MODEL,
            messages=[{"role": "system", "content": _SYSTEM}, {"role": "user", "content": user}],
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=max_tokens,
        )
        return json.loads(resp.choices[0].message.content or "{}")

    def _gemini_json(self, user: str, max_tokens: int) -> dict:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}"
            f":generateContent?key={self._gemini_key}"
        )
        body = {
            "system_instruction": {"parts": [{"text": _SYSTEM}]},
            "contents": [{"parts": [{"text": user}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0,
                "maxOutputTokens": max_tokens,
            },
        }
        r = httpx.post(url, json=body, timeout=40)
        r.raise_for_status()
        text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text)

    def _ollama_json(self, user: str, max_tokens: int) -> dict:
        r = httpx.post(
            f"{self._ollama}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [{"role": "system", "content": _SYSTEM}, {"role": "user", "content": user}],
                "format": "json",
                "stream": False,
                "options": {"temperature": 0, "num_predict": max_tokens},
            },
            timeout=120,
        )
        r.raise_for_status()
        return json.loads(r.json()["message"]["content"])

    def _json_call(self, user: str, *, retries: int = 1, max_tokens: int = 1600) -> dict:
        providers: list[tuple[str, object]] = []
        if self._groq:
            providers.append(("groq", self._groq_json))
        if self._gemini_key:
            providers.append(("gemini", self._gemini_json))
        providers.append(("ollama", self._ollama_json))

        last: Exception | None = None
        for _name, fn in providers:
            for _ in range(retries + 1):
                try:
                    return fn(user, max_tokens)  # type: ignore[operator]
                except Exception as e:  # noqa: BLE001 — try next provider/attempt
                    last = e
        raise RuntimeError(f"All LLM providers failed: {last}")

    # --- tasks ------------------------------------------------------------------

    def extract_corridor_risk(
        self, corridors: list[dict], articles_by_corridor: dict, price: dict | None
    ) -> dict:
        """Batched assessment of all corridors in one call.

        Returns {corridor_id: {relevant: bool, severity: float, rationale: str,
        cited_titles: list[str]}}.
        """
        price = price or {}
        brent = price.get("price")
        change = price.get("change_pct")
        price_line = (
            f"Current Brent crude: ${brent} ({change:+.2f}% today).\n"
            if brent is not None and change is not None
            else "Current Brent crude: unavailable.\n"
        )

        blocks: list[str] = []
        for c in corridors:
            arts = articles_by_corridor.get(c["id"], [])
            lines = (
                "\n".join(
                    f'- "{a["title"]}" ({a.get("domain", "")}, {a.get("seendate", "")})'
                    for a in arts[:6]
                )
                or "- (no recent headlines)"
            )
            blocks.append(f'## {c["name"]} (id: {c["id"]})\n{lines}')

        user = (
            price_line
            + "Assess each corridor's crude-supply disruption threat from the headlines below.\n"
            + "severity scale: 0.0 = no threat, 0.3 = minor/elevated, 0.6 = significant, "
            + "0.9 = severe imminent disruption.\n"
            + 'Return JSON exactly: {"corridors": [{"id": str, "relevant": bool, '
            + '"severity": number, "rationale": "<=160 chars", "cited_titles": [exact titles you relied on]}]}\n\n'
            + "\n\n".join(blocks)
        )

        data = self._json_call(user)
        out: dict[str, dict] = {}
        for item in data.get("corridors", []) or []:
            cid = item.get("id")
            if not cid:
                continue
            try:
                sev = float(item.get("severity", 0.0))
            except (TypeError, ValueError):
                sev = 0.0
            out[cid] = {
                "relevant": bool(item.get("relevant", False)),
                "severity": max(0.0, min(sev, 1.0)),
                "rationale": str(item.get("rationale", ""))[:200],
                "cited_titles": [str(t) for t in (item.get("cited_titles") or [])],
            }
        for c in corridors:
            out.setdefault(
                c["id"], {"relevant": False, "severity": 0.0, "rationale": "", "cited_titles": []}
            )
        return out

    def procurement_rationales(self, scenario_label: str, options: list[dict]) -> dict[str, str]:
        """One short procurement rationale per alternative source. Returns {id: rationale}."""
        if not options:
            return {}
        items = "\n".join(
            f'- id={o["id"]} | {o["country"]} {o["grade"]} | route via {o.get("route_label", o["corridor"])} '
            f'| transit {o["transit_days"]}d | delivered ${o["delivered_usd_bbl"]}/bbl '
            f'| grade_compatible={o["grade_compatible"]}'
            for o in options
        )
        user = (
            f"Scenario: {scenario_label}. India must replace disrupted crude imports. "
            "For each alternative source below, give a concise procurement rationale "
            "(<=140 chars) — why pick it or a key caveat (cost, transit, grade fit, geopolitics).\n"
            'Return JSON exactly: {"rationales": [{"id": str, "rationale": str}]}\n\n'
            f"{items}"
        )
        data = self._json_call(user, max_tokens=900)
        out: dict[str, str] = {}
        for r in data.get("rationales", []) or []:
            rid = r.get("id")
            if rid:
                out[str(rid)] = str(r.get("rationale", ""))[:160]
        return out
