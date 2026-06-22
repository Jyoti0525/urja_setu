"use client";

import type { HealthResponse, LiveMeta, MapState, RiskSignal } from "@/lib/api";
import { RISK_HEX, RISK_LABEL } from "@/lib/risk";

export function Header({
  health,
  isLive,
  loading,
  meta,
  onGoLive,
  onSimulate,
  onBacktest,
  onVessels,
  vesselsActive,
}: {
  health: HealthResponse | null;
  isLive: boolean;
  loading: boolean;
  meta: LiveMeta | null;
  onGoLive: () => void;
  onSimulate: () => void;
  onBacktest: () => void;
  onVessels: () => void;
  vesselsActive: boolean;
}) {
  return (
    <header className="pointer-events-none absolute inset-x-0 top-0 z-10 flex items-start justify-between p-4">
      <div className="pointer-events-auto rounded-xl border border-slate-800 bg-slate-950/70 px-4 py-3 backdrop-blur">
        <p className="text-[10px] uppercase tracking-[0.3em] text-slate-400">
          Energy Supply Chain Resilience
        </p>
        <h1 className="text-2xl font-bold leading-tight">
          URJA<span className="text-emerald-400">-</span>SETU
        </h1>
      </div>

      <div className="pointer-events-auto flex items-center gap-2">
        {meta && (
          <BrentChip usd={meta.brent_usd} changePct={meta.brent_change_pct} />
        )}

        <div className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-950/70 px-3 py-2 text-xs backdrop-blur">
          <span
            className={`inline-block h-2 w-2 rounded-full ${
              isLive ? "animate-pulse bg-emerald-400" : "bg-slate-500"
            }`}
          />
          <span className="text-slate-300">{isLive ? "LIVE" : health?.status === "ok" ? "Demo" : "Offline"}</span>
        </div>

        <button
          onClick={onGoLive}
          disabled={loading}
          className="rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-3 py-2 text-xs font-medium text-emerald-300 backdrop-blur transition hover:bg-emerald-500/20 disabled:cursor-wait disabled:opacity-60"
        >
          {loading ? "Scanning signals…" : isLive ? "Refresh" : "Go Live ▸"}
        </button>

        <button
          onClick={onSimulate}
          className="rounded-xl border border-sky-500/40 bg-sky-500/10 px-3 py-2 text-xs font-medium text-sky-300 backdrop-blur transition hover:bg-sky-500/20"
        >
          ⚡ Simulate
        </button>

        <button
          onClick={onBacktest}
          className="rounded-xl border border-violet-500/40 bg-violet-500/10 px-3 py-2 text-xs font-medium text-violet-300 backdrop-blur transition hover:bg-violet-500/20"
        >
          📊 Backtest
        </button>

        <button
          onClick={onVessels}
          className={`rounded-xl border px-3 py-2 text-xs font-medium backdrop-blur transition ${
            vesselsActive
              ? "border-cyan-400/60 bg-cyan-500/20 text-cyan-200"
              : "border-cyan-500/40 bg-cyan-500/10 text-cyan-300 hover:bg-cyan-500/20"
          }`}
        >
          🚢 Live Traffic
        </button>
      </div>
    </header>
  );
}

function BrentChip({ usd, changePct }: { usd: number | null; changePct: number | null }) {
  if (usd == null) return null;
  const up = (changePct ?? 0) >= 0;
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/70 px-3 py-2 text-xs backdrop-blur">
      <span className="text-slate-400">Brent </span>
      <span className="font-semibold tabular-nums text-slate-100">${usd.toFixed(2)}</span>
      {changePct != null && (
        <span className={`ml-1 tabular-nums ${up ? "text-red-400" : "text-emerald-400"}`}>
          {up ? "▲" : "▼"}
          {Math.abs(changePct).toFixed(2)}%
        </span>
      )}
    </div>
  );
}

export function IntelBar({ meta }: { meta: LiveMeta | null }) {
  if (!meta) return null;
  const t = new Date(meta.generated_at);
  const hhmmss = isNaN(t.getTime()) ? "" : t.toISOString().slice(11, 19) + " UTC";
  return (
    <div className="pointer-events-none absolute inset-x-0 top-[4.75rem] z-10 flex justify-center">
      <div className="pointer-events-auto rounded-full border border-slate-800 bg-slate-950/70 px-4 py-1.5 text-[11px] text-slate-400 backdrop-blur">
        🛰 {meta.articles_scanned} signals scanned · {(meta.response_time_ms / 1000).toFixed(1)}s ·
        updated {hhmmss} · scored from GDELT + Brent + OFAC
      </div>
    </div>
  );
}

export function CorridorPanel({ data }: { data: MapState | null }) {
  if (!data) return null;
  const corridors = [...data.corridors].sort(
    (a, b) => b.disruption_probability - a.disruption_probability,
  );

  return (
    <aside className="absolute left-4 top-24 z-10 w-72 space-y-3">
      <Card title={`Crude lifelines · ${corridors.length}`}>
        <ul className="space-y-2">
          {corridors.map((c) => (
            <li key={c.id} className="flex items-center justify-between gap-2">
              <span className="flex items-center gap-2 truncate">
                <span
                  className="inline-block h-2.5 w-2.5 shrink-0 rounded-full"
                  style={{ backgroundColor: RISK_HEX[c.risk_level] }}
                />
                <span className="truncate text-sm text-slate-200">{c.name}</span>
              </span>
              <span className="shrink-0 text-xs tabular-nums text-slate-400">
                {Math.round(c.disruption_probability * 100)}%
              </span>
            </li>
          ))}
        </ul>
      </Card>

      <Card title={`Refineries · ${data.refineries.length}`}>
        <p className="text-xs text-slate-400">
          {data.refineries.reduce((s, r) => s + r.capacity_kbd, 0).toLocaleString()} kbd total
          capacity · {data.sources.length} crude sources tracked
        </p>
      </Card>
    </aside>
  );
}

export function SignalPanel({ signals }: { signals: RiskSignal[] }) {
  if (!signals.length) return null;
  return (
    <div className="absolute right-4 top-24 z-10 w-80 space-y-2">
      <p className="px-1 text-[10px] uppercase tracking-widest text-slate-500">
        Live signals · {signals.length}
      </p>
      {signals.slice(0, 4).map((sig) => (
        <SignalItem key={sig.id} sig={sig} />
      ))}
    </div>
  );
}

function SignalItem({ sig }: { sig: RiskSignal }) {
  const url = sig.citations[0]?.url ?? undefined;
  const src = sig.citations[0]?.source ?? "feed";
  const Wrapper = url ? "a" : "div";
  return (
    <Wrapper
      {...(url ? { href: url, target: "_blank", rel: "noopener noreferrer" } : {})}
      className="block rounded-xl border border-orange-500/30 bg-slate-950/75 p-3 backdrop-blur transition hover:border-orange-400/60"
    >
      <p className="text-sm text-slate-100">{sig.headline}</p>
      <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400">
        <span className="truncate">{src}</span>
        <span className="ml-2 shrink-0 tabular-nums">
          severity {Math.round(sig.severity * 100)}%
        </span>
      </div>
    </Wrapper>
  );
}

export function Legend() {
  const items: Array<[string, string]> = [
    [RISK_HEX.low, RISK_LABEL.low],
    [RISK_HEX.moderate, RISK_LABEL.moderate],
    [RISK_HEX.high, RISK_LABEL.high],
    [RISK_HEX.critical, RISK_LABEL.critical],
  ];
  return (
    <div className="absolute bottom-4 left-4 z-10 rounded-xl border border-slate-800 bg-slate-950/70 p-3 text-xs backdrop-blur">
      <p className="mb-2 uppercase tracking-wide text-slate-500">Corridor risk</p>
      <div className="flex gap-3">
        {items.map(([hex, label]) => (
          <span key={label} className="flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: hex }} />
            <span className="text-slate-300">{label}</span>
          </span>
        ))}
      </div>
      <div className="mt-2 flex gap-4 border-t border-slate-800 pt-2 text-slate-400">
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-emerald-400" /> Refinery
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-amber-400" /> Crude source
        </span>
      </div>
    </div>
  );
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-3 backdrop-blur">
      <p className="mb-2 text-[10px] uppercase tracking-widest text-slate-500">{title}</p>
      {children}
    </div>
  );
}
