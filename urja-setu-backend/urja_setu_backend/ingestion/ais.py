"""Live AIS vessel tracking via AISStream.io (free websocket).

Connects, subscribes to a bounding box covering the Red Sea, Persian Gulf, and
Arabian Sea, and collects a short snapshot of live tanker/vessel positions. Cached
so the map is responsive and demo-stable. Renders ONLY real vessels — if no live
data is received (no key / network blocks websockets), the layer is simply empty.
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

# Red Sea + Bab-el-Mandeb + Persian Gulf/Hormuz + Arabian Sea approaches to India.
BOUNDING_BOXES = [[[10.0, 32.0], [30.0, 73.0]]]

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
_CACHE = DATA_DIR / "ais_snapshot.json"
_SEED = DATA_DIR / "ais_seed.json"  # a REAL snapshot captured via capture_ais.py
_TTL = 300.0  # serve a snapshot for 5 min


async def _collect(api_key: str, *, duration: float = 12.0, max_vessels: int = 400) -> list[dict]:
    try:
        import websockets
    except Exception:
        return []

    sub = {
        "APIKey": api_key,
        "BoundingBoxes": BOUNDING_BOXES,
        "FilterMessageTypes": ["PositionReport"],
    }
    seen: dict[int, dict] = {}
    try:
        async with websockets.connect("wss://stream.aisstream.io/v0/stream", open_timeout=10) as ws:
            await ws.send(json.dumps(sub))
            end = time.time() + duration
            while time.time() < end and len(seen) < max_vessels:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=max(0.2, end - time.time()))
                except asyncio.TimeoutError:
                    break
                d = json.loads(msg)
                # AISStream has used both "MetaData" and "Metadata" — accept either.
                meta = d.get("MetaData") or d.get("Metadata") or {}
                mmsi = meta.get("MMSI")
                lat = meta.get("latitude")
                lon = meta.get("longitude")
                if mmsi and lat is not None and lon is not None:
                    seen[mmsi] = {
                        "mmsi": mmsi,
                        "name": (meta.get("ShipName") or "").strip() or "Vessel",
                        "lat": lat,
                        "lon": lon,
                    }
    except Exception:
        pass
    return list(seen.values())


def _load_cache() -> dict | None:
    if _CACHE.exists():
        try:
            c = json.loads(_CACHE.read_text(encoding="utf-8"))
            if time.time() - c.get("ts", 0) < _TTL:
                return c
        except Exception:
            return None
    return None


def _load_seed() -> dict | None:
    """A real AIS snapshot captured (once) on a websocket-capable network."""
    if _SEED.exists():
        try:
            d = json.loads(_SEED.read_text(encoding="utf-8"))
            if d.get("vessels"):
                return d
        except Exception:
            return None
    return None


async def get_vessels(api_key: str | None, *, force: bool = False) -> dict:
    """Live AIS snapshot; falls back to a real captured snapshot if the live
    stream is blocked (venue network). Never fabricates vessels."""
    if not force:
        cached = _load_cache()
        if cached and cached.get("vessels"):
            return cached

    vessels = await _collect(api_key) if api_key else []
    if vessels:
        result = {"ts": time.time(), "vessels": vessels, "count": len(vessels),
                  "live": True, "note": "live AISStream snapshot"}
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            _CACHE.write_text(json.dumps(result), encoding="utf-8")
        except Exception:
            pass
        return result

    # Live blocked/empty → serve the real captured snapshot if we have one.
    seed = _load_seed()
    if seed:
        return {"ts": time.time(), "vessels": seed["vessels"], "count": len(seed["vessels"]),
                "live": False, "captured_at": seed.get("captured_at"),
                "note": "captured AIS snapshot (live stream unavailable on this network)"}

    return {"ts": time.time(), "vessels": [], "count": 0, "live": False,
            "note": "no live data and no captured snapshot — run capture_ais.py"}
