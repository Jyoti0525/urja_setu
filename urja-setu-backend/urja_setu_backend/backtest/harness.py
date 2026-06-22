"""Backtest harness — proves detection lead-time + precision/recall on real history.

Method:
1. Pull GDELT TimelineVol (daily news-attention intensity) per corridor over 2024-2026.
2. Detect ALERTS as robust-z-score spikes in attention.
3. Match alerts to curated labeled events (an alert within [-3d, +21d before] an event).
4. Report recall, precision, and average lead-time vs a no-early-warning baseline.

Results are cached to data/backtest_results.json so the Metrics view is fast and
demo-stable (no live dependency at presentation time). Re-run with run_backtest(force=True).
"""

from __future__ import annotations

import json
import statistics
import time
from datetime import datetime
from pathlib import Path

import httpx

from urja_setu_backend.backtest.events import LABELED_EVENTS

GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
DATA_DIR = Path(__file__).resolve().parents[3] / "data"
RESULTS_PATH = DATA_DIR / "backtest_results.json"

TIMELINE_QUERIES: dict[str, str] = {
    "hormuz": '(Hormuz OR "Persian Gulf") (oil OR tanker OR crude OR sanctions) sourcelang:english',
    "bab-el-mandeb": '("Red Sea" OR Houthi OR "Bab el Mandeb") (oil OR tanker OR shipping) sourcelang:english',
}

START = "20240101000000"
END = "20260601000000"

# Matching window: an alert "catches" an event if it lands from LEAD_MAX_BEFORE days
# before the event (early warning) to LEAD_MAX_AFTER days after (coverage lags reality).
LEAD_MAX_BEFORE = 21
LEAD_MAX_AFTER = 7


def fetch_timeline(corridor: str, *, timeout: float = 30.0) -> list[tuple[str, float]]:
    """GDELT TimelineVol daily attention series for a corridor. Fails soft to []."""
    q = TIMELINE_QUERIES[corridor]
    params = {
        "query": q,
        "mode": "TimelineVol",
        "format": "json",
        "startdatetime": START,
        "enddatetime": END,
        "timelinesmooth": "3",
    }
    data = None
    for attempt in range(3):
        try:
            r = httpx.get(GDELT_URL, params=params, timeout=timeout,
                          headers={"User-Agent": "urja-setu/0.1 (hackathon PoC)"})
            if r.status_code == 200 and r.text.strip().startswith("{"):
                data = r.json()
                break
            if attempt < 2:  # 429 / transient — back off past the 5s window
                time.sleep(7)
                continue
            return []
        except Exception:
            if attempt < 2:
                time.sleep(7)
                continue
            return []
    if data is None:
        return []

    series: list[tuple[str, float]] = []
    for block in data.get("timeline", []) or []:
        for pt in block.get("data", []) or []:
            raw = str(pt.get("date", ""))  # e.g. "20240104T000000Z"
            if len(raw) >= 8:
                d = f"{raw[0:4]}-{raw[4:6]}-{raw[6:8]}"
                series.append((d, float(pt.get("value", 0.0))))
        break  # first series only
    return series


def detect_alerts(series: list[tuple[str, float]], *, z: float = 2.7, min_gap_days: int = 14) -> list[dict]:
    """Robust-z-score spike detection, de-duplicated to one alert per spike cluster."""
    vals = [v for _, v in series]
    if len(vals) < 15:
        return []
    med = statistics.median(vals)
    deviations = [abs(v - med) for v in vals]
    mad = statistics.median(deviations) or 1e-6

    alerts: list[dict] = []
    last_dt: datetime | None = None
    for d, v in series:
        score = 0.6745 * (v - med) / mad
        if score >= z:
            dt = datetime.fromisoformat(d)
            if last_dt is None or (dt - last_dt).days >= min_gap_days:
                alerts.append({"date": d, "z": round(score, 2), "value": round(v, 3)})
                last_dt = dt
    return alerts


def _downsample(series: list[tuple[str, float]], n: int = 160) -> list[list]:
    if len(series) <= n:
        return [[d, round(v, 3)] for d, v in series]
    step = len(series) / n
    out = []
    for i in range(n):
        d, v = series[int(i * step)]
        out.append([d, round(v, 3)])
    return out


TIMELINES_PATH = DATA_DIR / "backtest_timelines.json"


def get_timelines(*, refresh: bool = False, sleep_between: float = 8.0) -> dict[str, list]:
    """Load per-corridor full timelines from cache; fetch any missing (or all if refresh).

    Only overwrites a corridor's cached series when a fetch returns non-empty data, so a
    transient GDELT 429 can never wipe good history.
    """
    cache: dict[str, list] = {}
    if TIMELINES_PATH.exists() and not refresh:
        try:
            raw = json.loads(TIMELINES_PATH.read_text(encoding="utf-8"))
            cache = {c: [(d, float(v)) for d, v in s] for c, s in raw.items()}
        except Exception:
            cache = {}

    corridors = list(TIMELINE_QUERIES)
    for i, cor in enumerate(corridors):
        if cor in cache and cache[cor] and not refresh:
            continue
        series = fetch_timeline(cor)
        if series:
            cache[cor] = series
        if i < len(corridors) - 1:
            time.sleep(sleep_between)

    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        TIMELINES_PATH.write_text(
            json.dumps({c: [[d, v] for d, v in s] for c, s in cache.items()}, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass
    return cache


def evaluate(timelines: dict | None = None) -> dict:
    """Detect alerts + score against labeled events (deterministic given timelines)."""
    if timelines is None:
        timelines = get_timelines()
    alerts_by = {cor: detect_alerts(series) for cor, series in timelines.items()}

    events = [e for e in LABELED_EVENTS if e["corridor"] in timelines]
    matched_alert_keys: set[tuple[str, str]] = set()
    detected = 0
    lead_times: list[int] = []
    event_rows: list[dict] = []

    for ev in events:
        ed = datetime.fromisoformat(ev["date"])
        cor = ev["corridor"]
        best_lead: int | None = None
        best_alert: str | None = None
        for al in alerts_by.get(cor, []):
            lead = (ed - datetime.fromisoformat(al["date"])).days  # +ve = alert before event
            if -LEAD_MAX_AFTER <= lead <= LEAD_MAX_BEFORE:
                matched_alert_keys.add((cor, al["date"]))
                if best_lead is None or lead > best_lead:
                    best_lead, best_alert = lead, al["date"]
        if best_lead is not None:
            detected += 1
            lead_times.append(best_lead)
        event_rows.append(
            {**ev, "detected": best_lead is not None,
             "lead_days": best_lead, "alert_date": best_alert}
        )

    total_alerts = sum(len(a) for a in alerts_by.values())
    recall = detected / len(events) if events else 0.0
    precision = len(matched_alert_keys) / total_alerts if total_alerts else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "window": "2024-01 → 2026-06",
        "source": "GDELT TimelineVol (news-attention intensity)",
        "events_total": len(events),
        "events_detected": detected,
        "recall": round(recall, 3),
        "precision": round(precision, 3),
        "f1": round(f1, 3),
        "avg_lead_days": round(statistics.mean(lead_times), 1) if lead_times else 0.0,
        "alerts_total": total_alerts,
        "baseline": {"recall": 0.0, "avg_lead_days": 0.0, "note": "no early-warning layer"},
        "events": event_rows,
        "alerts_by_corridor": alerts_by,
        "timelines": {c: _downsample(s) for c, s in timelines.items()},
    }


def run_backtest(*, force: bool = False) -> dict:
    """Return cached results; compute + cache if missing or forced."""
    if not force and RESULTS_PATH.exists():
        try:
            return json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    result = evaluate()
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        RESULTS_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    except Exception:
        pass
    return result
