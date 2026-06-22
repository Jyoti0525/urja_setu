"""Capture a REAL AIS snapshot to data/ais_seed.json.

Run this ONCE on any environment that allows websockets (your own terminal, a
phone hotspot, or a free cloud shell like Google Colab). The app then serves
these real vessel positions even if the live stream is blocked at demo time.

Usage:
    python capture_ais.py            # reads key from ../.env or .env
    python capture_ais.py <APIKEY>   # or pass the key explicitly
"""

import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Red Sea + Bab-el-Mandeb + Persian Gulf/Hormuz + Arabian Sea approaches.
BOXES = [[[10.0, 32.0], [30.0, 73.0]]]


def _key() -> str:
    if len(sys.argv) > 1:
        return sys.argv[1].strip()
    for env in (Path(".env"), Path(__file__).resolve().parent / ".env"):
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                if line.startswith("AISSTREAM_API_KEY="):
                    return line.split("=", 1)[1].strip()
    return ""


async def collect(key: str, duration: float = 25.0, max_vessels: int = 500) -> list[dict]:
    import websockets

    seen: dict[int, dict] = {}
    sub = {"APIKey": key, "BoundingBoxes": BOXES, "FilterMessageTypes": ["PositionReport"]}
    async with websockets.connect("wss://stream.aisstream.io/v0/stream", open_timeout=15) as ws:
        await ws.send(json.dumps(sub))
        end = time.time() + duration
        while time.time() < end and len(seen) < max_vessels:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=max(0.5, end - time.time()))
            except asyncio.TimeoutError:
                break
            d = json.loads(msg)
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
    return list(seen.values())


def main() -> None:
    key = _key()
    if not key:
        print("No key. Pass it as an argument or set AISSTREAM_API_KEY in .env")
        return
    print("Capturing real AIS for ~25s (needs a websocket-capable network)...")
    try:
        vessels = asyncio.run(collect(key))
    except Exception as e:  # noqa: BLE001
        print("FAILED:", type(e).__name__, str(e)[:160])
        return
    if not vessels:
        print("No vessels captured - this network blocks websocket streaming.\n"
              "Try a phone hotspot or run this in Google Colab, then copy data/ais_seed.json over.")
        return
    out_dir = Path(__file__).resolve().parents[1] / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {"captured_at": datetime.now(timezone.utc).isoformat(), "vessels": vessels}
    (out_dir / "ais_seed.json").write_text(json.dumps(payload), encoding="utf-8")
    print(f"Saved {len(vessels)} REAL vessels to data/ais_seed.json")
    print("Restart the backend - the Vessels button will now show them.")


if __name__ == "__main__":
    main()
