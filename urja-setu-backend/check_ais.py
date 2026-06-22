"""Standalone AISStream connectivity check.

Run from this folder on YOUR machine (not inside any sandbox):

    python check_ais.py

It tells you whether live vessel data flows on your network — if it does, the
app's 🚢 Vessels button will populate with real tankers.
"""

import asyncio
import json
import time
from pathlib import Path


def _key() -> str:
    env = Path(".env")
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("AISSTREAM_API_KEY="):
                return line.split("=", 1)[1].strip()
    return ""


async def main() -> None:
    try:
        import websockets
    except ImportError:
        print("Missing dependency: pip install websockets")
        return

    key = _key()
    if not key:
        print("No AISSTREAM_API_KEY found in .env")
        return

    sub = {
        "APIKey": key,
        "BoundingBoxes": [[[-90, -180], [90, 180]]],
        "FilterMessageTypes": ["PositionReport"],
    }
    print("Connecting to AISStream (15s)...")
    try:
        async with websockets.connect("wss://stream.aisstream.io/v0/stream", open_timeout=15) as ws:
            await ws.send(json.dumps(sub))
            msgs = 0
            vessels = 0
            end = time.time() + 15
            while time.time() < end and vessels < 5:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=max(0.5, end - time.time()))
                except asyncio.TimeoutError:
                    break
                msgs += 1
                d = json.loads(msg)
                meta = d.get("MetaData") or d.get("Metadata") or {}
                if meta.get("MMSI"):
                    vessels += 1
                    print(f"  vessel: {str(meta.get('ShipName', '?')).strip()} "
                          f"@ {meta.get('latitude')}, {meta.get('longitude')}")
                elif msgs <= 3:
                    print("  server message:", str(msg)[:200])

            if vessels:
                print(f"\nSUCCESS - live AIS works here ({vessels}+ vessels). "
                      "The app's Vessels button will show real tankers.")
            elif msgs:
                print("\nKEY/AUTH ISSUE - the server replied but sent no vessels "
                      "(see 'server message' above). Confirm the key is active on aisstream.io.")
            else:
                print("\nNO DATA - connected, key not rejected, but zero frames in 15s.\n"
                      "  -> Either this network blocks websocket streaming (try a phone hotspot),\n"
                      "     or the AISStream key needs activation on aisstream.io.")
    except Exception as e:  # noqa: BLE001
        print("CONNECT FAILED:", type(e).__name__, str(e)[:160])


asyncio.run(main())
