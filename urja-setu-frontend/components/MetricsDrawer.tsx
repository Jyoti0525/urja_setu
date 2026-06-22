"use client";

import { useEffect, useState } from "react";

import { api, type BacktestResult } from "@/lib/api";

export function MetricsDrawer({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [data, setData] = useState<BacktestResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && !data) {
      api.backtest().then(setData).catch((e: unknown) =>
        setError(e instanceof Error ? e.message : String(e)),
      );
    }
  }, [open, data]);

  if (!open) return null;

  return (
    <div className="absolute right-0 top-0 z-20 flex h-full w-[26rem] max-w-[92vw] flex-col border-l border-slate-800 bg-slate-950/95 backdrop-blur">
      <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
        <div>
          <p className="text-[10px] uppercase tracking-widest text-slate-500">Backtest</p>
          <h2 className="text-sm font-semibold text-slate-100">Proven detection on history</h2>
        </div>
        <button onClick={onClose} className="rounded-lg px-2 py-1 text-slate-400 hover:bg-slate-800 hover:text-slate-100">
          ✕
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {error && <p className="text-sm text-red-300">{error}</p>}
        {!data && !error && <p className="text-sm text-slate-400">Loading backtest…</p>}

        {data && (
          <div className="space-y-5">
            <div className="grid grid-cols-2 gap-2">
              <Metric label="Recall" value={`${Math.round(data.recall * 100)}%`} sub={`${data.events_detected}/${data.events_total} events caught`} tone="good" />
              <Metric label="Precision" value={`${Math.round(data.precision * 100)}%`} sub={`${data.alerts_total} alerts raised`} tone="good" />
              <Metric label="F1 score" value={data.f1.toFixed(2)} sub="recall × precision balance" tone="good" />
              <Metric label="Avg lead-time" value={`${data.avg_lead_days} d`} sub="ahead of impact · 0d baseline" tone="good" />
            </div>

            <p className="text-[11px] text-slate-500">
              {data.source} · window {data.window}. An alert is a 2.7σ spike in corridor
              news-attention; it &ldquo;catches&rdquo; an event if it lands 21 days before to 7 days
              after it. Baseline (no early-warning layer): 0% recall, 0-day lead.
            </p>

            {Object.entries(data.timelines).map(([cor, series]) => (
              <Sparkline
                key={cor}
                corridor={cor}
                series={series}
                events={data.events.filter((e) => e.corridor === cor)}
                alerts={(data.alerts_by_corridor[cor] ?? []).map((a) => a.date)}
              />
            ))}

            <div>
              <p className="mb-2 text-[10px] uppercase tracking-widest text-slate-500">Labeled events</p>
              <div className="space-y-1.5">
                {data.events.map((e, i) => (
                  <div key={i} className="rounded-lg border border-slate-800 bg-slate-900/40 p-2 text-xs">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-slate-300">{e.date}</span>
                      {e.detected ? (
                        <span className="rounded bg-emerald-500/15 px-1.5 py-0.5 text-[10px] text-emerald-300">
                          caught · {e.lead_days}d early
                        </span>
                      ) : (
                        <span className="rounded bg-slate-700/40 px-1.5 py-0.5 text-[10px] text-slate-400">
                          missed
                        </span>
                      )}
                    </div>
                    <div className="mt-0.5 text-[11px] text-slate-500">{e.note}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function Metric({
  label,
  value,
  sub,
  tone,
}: {
  label: string;
  value: string;
  sub?: string;
  tone: "good" | "bad" | "warn";
}) {
  const color =
    tone === "bad" ? "text-slate-400" : tone === "good" ? "text-emerald-400" : "text-amber-300";
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-2.5">
      <div className="text-[10px] uppercase tracking-wide text-slate-500">{label}</div>
      <div className={`mt-0.5 text-xl font-semibold tabular-nums ${color}`}>{value}</div>
      {sub && <div className="text-[11px] text-slate-500">{sub}</div>}
    </div>
  );
}

function Sparkline({
  corridor,
  series,
  events,
  alerts,
}: {
  corridor: string;
  series: [string, number][];
  events: { date: string }[];
  alerts: string[];
}) {
  const W = 340;
  const H = 48;
  if (series.length < 2) return null;
  const dates = series.map((s) => s[0]);
  const vals = series.map((s) => s[1]);
  const max = Math.max(...vals, 0.001);
  const x = (i: number) => (i / (series.length - 1)) * W;
  const y = (v: number) => H - (v / max) * (H - 4) - 2;

  const idxOf = (date: string) => {
    let idx = dates.findIndex((d) => d >= date);
    if (idx < 0) idx = dates.length - 1;
    return idx;
  };

  const points = series.map((s, i) => `${x(i).toFixed(1)},${y(s[1]).toFixed(1)}`).join(" ");

  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-[11px] text-slate-400">
        <span className="capitalize">{corridor.replace(/-/g, " ")} · news attention</span>
        <span className="text-slate-600">2024 → 2026</span>
      </div>
      <svg width="100%" viewBox={`0 0 ${W} ${H}`} className="rounded-lg border border-slate-800 bg-slate-900/40">
        {alerts.map((d, i) => (
          <line key={`a${i}`} x1={x(idxOf(d))} y1={0} x2={x(idxOf(d))} y2={H} stroke="#f59e0b" strokeWidth={1} opacity={0.35} />
        ))}
        <polyline points={points} fill="none" stroke="#38bdf8" strokeWidth={1.2} />
        {events.map((e, i) => (
          <circle key={`e${i}`} cx={x(idxOf(e.date))} cy={H - 4} r={2.6} fill="#ef4444" />
        ))}
      </svg>
    </div>
  );
}
