"use client";

import { useState } from "react";

type Region = { id: string; label: string; lat: number; lon: number; zoom: number };

const REGIONS: Region[] = [
  { id: "hormuz", label: "Strait of Hormuz", lat: 26.4, lon: 56.4, zoom: 7 },
  { id: "redsea", label: "Bab-el-Mandeb / Red Sea", lat: 13.6, lon: 43.3, zoom: 6 },
  { id: "arabian", label: "Arabian Sea (India)", lat: 20.0, lon: 64.0, zoom: 5 },
];

function embedUrl(r: Region): string {
  return (
    `https://www.marinetraffic.com/en/ais/embed/zoom:${r.zoom}` +
    `/centery:${r.lat}/centerx:${r.lon}/maptype:1/shownames:false` +
    `/mmsi:0/shipid:0/fleet:false/showmenu:false/remember:false`
  );
}

export function MaritimeTrafficPanel({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [region, setRegion] = useState<Region>(REGIONS[0]);
  if (!open) return null;

  return (
    <div className="absolute inset-0 z-30 flex items-center justify-center bg-slate-950/70 p-4 backdrop-blur-sm sm:p-8">
      <div className="flex h-[82vh] w-[min(1040px,94vw)] flex-col overflow-hidden rounded-2xl border border-slate-700 bg-slate-950 shadow-2xl">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 px-4 py-3">
          <div>
            <p className="text-[10px] uppercase tracking-widest text-slate-500">Live AIS · MarineTraffic</p>
            <h2 className="text-sm font-semibold text-slate-100">🚢 Live Maritime Traffic</h2>
          </div>
          <div className="flex items-center gap-1.5">
            {REGIONS.map((r) => (
              <button
                key={r.id}
                onClick={() => setRegion(r)}
                className={`rounded-lg border px-2.5 py-1.5 text-xs transition ${
                  region.id === r.id
                    ? "border-cyan-400/60 bg-cyan-500/20 text-cyan-200"
                    : "border-slate-700 text-slate-300 hover:bg-slate-800"
                }`}
              >
                {r.label}
              </button>
            ))}
            <button
              onClick={onClose}
              className="ml-1 rounded-lg px-2 py-1 text-slate-400 hover:bg-slate-800 hover:text-slate-100"
            >
              ✕
            </button>
          </div>
        </div>

        <iframe
          key={region.id}
          title="Live AIS vessel traffic"
          src={embedUrl(region)}
          className="h-full w-full border-0"
        />

        <div className="border-t border-slate-800 px-4 py-2 text-[11px] text-slate-500">
          Real-time vessel positions from the global AIS network. Red = tankers · green = cargo ·
          blue = other. Watch crude tankers transit the chokepoints live.
        </div>
      </div>
    </div>
  );
}
