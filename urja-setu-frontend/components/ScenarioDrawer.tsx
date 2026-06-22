"use client";

import { useEffect, useState } from "react";

import {
  api,
  type Assumption,
  type ScenarioInput,
  type ScenarioResponse,
  type SprStep,
} from "@/lib/api";

// Assumptions whose backend value is a fraction but shown as a percent.
const PERCENT_KEYS = new Set(["corridor_share", "closure_pct", "reroutable_share"]);

export function ScenarioDrawer({
  open,
  onClose,
  onAffectedCorridor,
}: {
  open: boolean;
  onClose: () => void;
  onAffectedCorridor?: (corridor: string | null) => void;
}) {
  const [scenarios, setScenarios] = useState<ScenarioInput[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [result, setResult] = useState<ScenarioResponse | null>(null);
  const [overrides, setOverrides] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && scenarios.length === 0) {
      api.scenarioList().then(setScenarios).catch(() => {});
    }
  }, [open, scenarios.length]);

  async function run(scenarioId: string, payload?: Record<string, number>) {
    setLoading(true);
    setError(null);
    setSelectedId(scenarioId);
    try {
      const r = await api.simulate(scenarioId, payload);
      setResult(r);
      onAffectedCorridor?.(r.affected_corridor ?? null);
      const ov: Record<string, number> = {};
      r.assumptions.forEach((a) => (ov[a.key] = a.value));
      setOverrides(ov);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  function reSimulate() {
    if (!selectedId) return;
    const payload: Record<string, number> = {};
    for (const [k, v] of Object.entries(overrides)) {
      payload[k] = PERCENT_KEYS.has(k) ? v / 100 : v;
    }
    run(selectedId, payload);
  }

  if (!open) return null;

  return (
    <div className="absolute right-0 top-0 z-20 flex h-full w-[26rem] max-w-[92vw] flex-col border-l border-slate-800 bg-slate-950/95 backdrop-blur">
      <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
        <div>
          <p className="text-[10px] uppercase tracking-widest text-slate-500">Scenario Simulator</p>
          <h2 className="text-sm font-semibold text-slate-100">Disruption → Response</h2>
        </div>
        <button onClick={onClose} className="rounded-lg px-2 py-1 text-slate-400 hover:bg-slate-800 hover:text-slate-100">
          ✕
        </button>
      </div>

      <div className="flex flex-wrap gap-2 border-b border-slate-800 p-3">
        {scenarios.map((s) => (
          <button
            key={s.scenario_id}
            onClick={() => run(s.scenario_id)}
            className={`rounded-lg border px-2.5 py-1.5 text-xs transition ${
              selectedId === s.scenario_id
                ? "border-emerald-500/50 bg-emerald-500/15 text-emerald-200"
                : "border-slate-700 text-slate-300 hover:bg-slate-800"
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {loading && <p className="text-sm text-slate-400">Running cascade + procurement agent…</p>}
        {error && <p className="text-sm text-red-300">{error}</p>}
        {!loading && !result && !error && (
          <p className="text-sm text-slate-500">Pick a scenario above to simulate its impact.</p>
        )}

        {result && !loading && (
          <div className="space-y-5">
            <CascadeMetrics result={result} />
            <SprPanel result={result} />
            <AssumptionsEditor
              assumptions={result.assumptions}
              overrides={overrides}
              onChange={(k, v) => setOverrides((o) => ({ ...o, [k]: v }))}
              onReSimulate={reSimulate}
            />
            <Procurement result={result} />
            <p className="text-[11px] text-slate-600">
              signal→recommendation in {(result.response_time_ms / 1000).toFixed(1)}s · deterministic
              engine + knowledge-graph procurement
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function CascadeMetrics({ result }: { result: ScenarioResponse }) {
  const c = result.cascade;
  const up = c.price_impact_pct >= 0;
  return (
    <div>
      <p className="mb-2 text-[10px] uppercase tracking-widest text-slate-500">Projected impact</p>
      <div className="grid grid-cols-2 gap-2">
        <Metric label="Supply gap" value={`${c.supply_gap_kbd.toLocaleString()} kbd`} tone="warn" />
        <Metric
          label="Brent impact"
          value={`${up ? "+" : ""}${c.price_impact_pct}%`}
          sub={`→ $${c.brent_projected_usd}`}
          tone={up ? "bad" : "good"}
        />
        <Metric label="Refinery run-rate" value={`${c.refinery_runrate_pct}%`} tone="warn" />
        <Metric label="SPR offsets gap" value={`${c.spr_cover_days} d`} tone="good" />
      </div>
      {c.notes.length > 0 && (
        <ul className="mt-2 space-y-1">
          {c.notes.map((n, i) => (
            <li key={i} className="text-[11px] text-slate-400">• {n}</li>
          ))}
        </ul>
      )}
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
    tone === "bad" ? "text-red-400" : tone === "good" ? "text-emerald-400" : "text-amber-300";
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-2.5">
      <div className="text-[10px] uppercase tracking-wide text-slate-500">{label}</div>
      <div className={`mt-0.5 text-lg font-semibold tabular-nums ${color}`}>{value}</div>
      {sub && <div className="text-[11px] text-slate-500">{sub}</div>}
    </div>
  );
}

function AssumptionsEditor({
  assumptions,
  overrides,
  onChange,
  onReSimulate,
}: {
  assumptions: Assumption[];
  overrides: Record<string, number>;
  onChange: (key: string, value: number) => void;
  onReSimulate: () => void;
}) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-3">
      <p className="mb-2 text-[10px] uppercase tracking-widest text-slate-500">
        Assumptions · editable &amp; testable
      </p>
      <div className="space-y-2">
        {assumptions.map((a) => (
          <div key={a.key} className="flex items-center justify-between gap-2">
            <div className="min-w-0">
              <div className="truncate text-xs text-slate-200">{a.label}</div>
              <div className="truncate text-[10px] text-slate-500">{a.source}</div>
            </div>
            <div className="flex shrink-0 items-center gap-1">
              <input
                type="number"
                value={overrides[a.key] ?? a.value}
                onChange={(e) => onChange(a.key, parseFloat(e.target.value))}
                className="w-20 rounded border border-slate-700 bg-slate-950 px-2 py-1 text-right text-xs tabular-nums text-slate-100 focus:border-emerald-500 focus:outline-none"
                step="any"
              />
              {a.unit && <span className="w-8 text-[10px] text-slate-500">{a.unit}</span>}
            </div>
          </div>
        ))}
      </div>
      <button
        onClick={onReSimulate}
        className="mt-3 w-full rounded-lg border border-emerald-500/40 bg-emerald-500/10 py-1.5 text-xs font-medium text-emerald-300 hover:bg-emerald-500/20"
      >
        Re-simulate ▸
      </button>
    </div>
  );
}

function SprPanel({ result }: { result: ScenarioResponse }) {
  const plan = result.spr_plan;
  if (!plan) return null;
  const safe = plan.depletion_day == null;
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-3">
      <p className="mb-2 text-[10px] uppercase tracking-widest text-slate-500">
        SPR drawdown optimiser
      </p>
      <div className="grid grid-cols-3 gap-2">
        <MiniStat label="Peak draw" value={`${Math.round(plan.peak_drawdown_kbd)}`} unit="kbd/d" />
        <MiniStat label="Full cover by" value={`${plan.days_to_full_coverage}`} unit="d" />
        <MiniStat
          label="Reserve left"
          value={`${plan.reserve_remaining_pct}`}
          unit="%"
          tone={safe ? "good" : "bad"}
        />
      </div>
      <ReserveSpark schedule={plan.schedule} />
      <p className={`mt-2 text-[11px] ${safe ? "text-emerald-300" : "text-red-300"}`}>{plan.verdict}</p>
    </div>
  );
}

function MiniStat({
  label,
  value,
  unit,
  tone,
}: {
  label: string;
  value: string;
  unit: string;
  tone?: "good" | "bad";
}) {
  const color = tone === "bad" ? "text-red-400" : tone === "good" ? "text-emerald-400" : "text-slate-100";
  return (
    <div className="rounded border border-slate-800 bg-slate-950/40 p-1.5 text-center">
      <div className="text-[9px] uppercase tracking-wide text-slate-500">{label}</div>
      <div className={`text-sm font-semibold tabular-nums ${color}`}>
        {value}
        <span className="text-[10px] text-slate-500"> {unit}</span>
      </div>
    </div>
  );
}

function ReserveSpark({ schedule }: { schedule: SprStep[] }) {
  const W = 340;
  const H = 34;
  if (schedule.length < 2) return null;
  const max = Math.max(...schedule.map((s) => s.reserve_kbd_days), 1);
  const x = (i: number) => (i / (schedule.length - 1)) * W;
  const y = (v: number) => H - (v / max) * (H - 2) - 1;
  const line = schedule.map((s, i) => `${x(i).toFixed(1)},${y(s.reserve_kbd_days).toFixed(1)}`).join(" ");
  const area = `0,${H} ${line} ${W},${H}`;
  return (
    <svg width="100%" viewBox={`0 0 ${W} ${H}`} className="mt-2 rounded border border-slate-800 bg-slate-950/40">
      <polygon points={area} fill="rgba(16,185,129,0.13)" />
      <polyline points={line} fill="none" stroke="#10b981" strokeWidth={1.2} />
    </svg>
  );
}

function Procurement({ result }: { result: ScenarioResponse }) {
  return (
    <div>
      <p className="mb-2 text-[10px] uppercase tracking-widest text-slate-500">
        Procurement orchestrator · ranked alternatives
      </p>
      <div className="space-y-2">
        {result.procurement_options.map((o) => (
          <div key={o.rank} className="rounded-lg border border-slate-800 bg-slate-900/50 p-3">
            <div className="flex items-center justify-between gap-2">
              <span className="flex items-center gap-2">
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-800 text-[11px] text-slate-300">
                  {o.rank}
                </span>
                <span className="text-sm font-medium text-slate-100">
                  {o.source_country} · {o.grade}
                </span>
              </span>
              <span
                className={`rounded px-1.5 py-0.5 text-[10px] ${
                  o.grade_compatible
                    ? "bg-emerald-500/15 text-emerald-300"
                    : "bg-amber-500/15 text-amber-300"
                }`}
              >
                {o.grade_compatible ? "grade ✓" : "grade ✗"}
              </span>
            </div>
            <div className="mt-1 text-[11px] text-slate-400">{o.route_name}</div>
            <div className="mt-1 flex gap-3 text-[11px] text-slate-400">
              <span className="tabular-nums">{o.transit_days}d transit</span>
              <span className="tabular-nums">${o.delivered_cost_usd_bbl}/bbl delivered</span>
            </div>
            {o.rationale && (
              <div className="mt-1.5 text-[11px] italic text-slate-300">“{o.rationale}”</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
