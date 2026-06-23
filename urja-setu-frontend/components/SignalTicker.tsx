"use client";

import type { MapState } from "@/lib/api";
import { RISK_HEX } from "@/lib/risk";
import { Marquee } from "@/components/ui/marquee";

export function SignalTicker({ data }: { data: MapState | null }) {
  if (!data) return null;
  const corridors = [...data.corridors].sort(
    (a, b) => b.disruption_probability - a.disruption_probability,
  );

  return (
    <div className="absolute inset-x-0 bottom-0 z-10 border-t border-slate-800 bg-slate-950/85 backdrop-blur">
      <div className="flex items-center">
        <span className="z-10 shrink-0 border-r border-slate-800 bg-slate-900/80 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-widest text-emerald-300">
          ● Live Feed
        </span>
        <Marquee className="flex-1 [--duration:42s] [--gap:2.5rem] py-1.5" pauseOnHover>
          {corridors.map((c) => (
            <span key={c.id} className="flex items-center gap-2 text-xs text-slate-300">
              <span
                className="inline-block h-2 w-2 rounded-full"
                style={{ backgroundColor: RISK_HEX[c.risk_level] }}
              />
              <span>{c.name}</span>
              <span className="tabular-nums text-slate-400">
                {Math.round(c.disruption_probability * 100)}%
              </span>
            </span>
          ))}
          {data.signals.map((s) => (
            <span key={s.id} className="flex items-center gap-2 text-xs text-orange-200">
              <span className="text-orange-400">▲</span>
              <span className="max-w-[36rem] truncate">{s.headline}</span>
              <span className="text-[10px] text-slate-500">
                {s.citations[0]?.source ?? "feed"}
              </span>
            </span>
          ))}
        </Marquee>
      </div>
    </div>
  );
}
