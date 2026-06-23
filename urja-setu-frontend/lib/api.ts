// Typed client for the URJA-SETU API. Types mirror urja_setu_backend/shared/schemas.py.

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:6006";

export type Mode = "demo" | "live";
export type RiskLevel = "low" | "moderate" | "high" | "critical";

export interface Coordinate {
  lat: number;
  lon: number;
}

export interface Citation {
  source: string;
  title: string;
  url?: string | null;
  published?: string | null;
}

export interface RiskSignal {
  id: string;
  corridor_id: string;
  headline: string;
  severity: number;
  citations: Citation[];
  detected_at: string;
}

export interface Corridor {
  id: string;
  name: string;
  path: Coordinate[];
  chokepoint?: Coordinate | null;
  origin_label?: string | null;
  throughput_share: number;
  disruption_probability: number;
  risk_level: RiskLevel;
}

export interface Refinery {
  id: string;
  name: string;
  operator: string;
  location: Coordinate;
  capacity_kbd: number;
  grade_slate: string[];
}

export interface CrudeSource {
  id: string;
  country: string;
  grade: string;
  location: Coordinate;
  spot_price_usd?: number | null;
}

export interface MapState {
  corridors: Corridor[];
  refineries: Refinery[];
  sources: CrudeSource[];
  signals: RiskSignal[];
}

export interface Assumption {
  key: string;
  label: string;
  value: number;
  unit?: string | null;
  source: string;
  editable?: boolean;
}

export interface LiveMeta {
  brent_usd: number | null;
  brent_change_pct: number | null;
  articles_scanned: number;
  response_time_ms: number;
  generated_at: string;
  assumptions: Assumption[];
  mode: Mode;
}

export interface LiveMapResponse {
  corridors: Corridor[];
  refineries: Refinery[];
  sources: CrudeSource[];
  signals: RiskSignal[];
  meta: LiveMeta;
}

export interface CascadeResult {
  supply_gap_kbd: number;
  price_impact_pct: number;
  brent_projected_usd: number;
  refinery_runrate_pct: number;
  spr_cover_days: number;
  notes: string[];
}

export interface ProcurementOption {
  rank: number;
  source_country: string;
  grade: string;
  route_name: string;
  transit_days: number;
  delivered_cost_usd_bbl: number;
  grade_compatible: boolean;
  rationale: string;
}

export interface ScenarioInput {
  scenario_id: string;
  label: string;
  description?: string | null;
}

export interface SprStep {
  day: number;
  drawdown_kbd: number;
  reserve_kbd_days: number;
}

export interface SprPlan {
  reserve_initial_kbd_days: number;
  peak_drawdown_kbd: number;
  first_reroute_days: number;
  days_to_full_coverage: number;
  reserve_remaining_kbd_days: number;
  reserve_remaining_pct: number;
  depletion_day: number | null;
  verdict: string;
  schedule: SprStep[];
}

export interface ScenarioResponse {
  scenario: ScenarioInput;
  assumptions: Assumption[];
  cascade: CascadeResult;
  procurement_options: ProcurementOption[];
  response_time_ms: number;
  mode: Mode;
  affected_corridor?: string | null;
  spr_plan?: SprPlan | null;
}

export interface BacktestEvent {
  date: string;
  corridor: string;
  note: string;
  detected: boolean;
  lead_days: number | null;
  alert_date: string | null;
}

export interface BacktestAlert {
  date: string;
  z: number;
  value: number;
}

export interface BacktestResult {
  generated_at: string;
  window: string;
  source: string;
  events_total: number;
  events_detected: number;
  recall: number;
  precision: number;
  f1: number;
  avg_lead_days: number;
  alerts_total: number;
  baseline: { recall: number; avg_lead_days: number; note: string };
  events: BacktestEvent[];
  alerts_by_corridor: Record<string, BacktestAlert[]>;
  timelines: Record<string, [string, number][]>;
}

export interface Vessel {
  mmsi: number;
  name: string;
  lat: number;
  lon: number;
}

export interface VesselsResponse {
  ts: number;
  vessels: Vessel[];
  count: number;
  live: boolean;
  note?: string;
}

export interface HealthResponse {
  status: string;
  app: string;
  version: string;
  mode: Mode;
}

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json() as Promise<T>;
}

async function postJSON<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json() as Promise<T>;
}

export const api = {
  health: () => getJSON<HealthResponse>("/health"),
  map: () => getJSON<MapState>("/api/map"),
  liveRisk: () => getJSON<LiveMapResponse>("/api/risk/live"),
  scenarioList: () => getJSON<ScenarioInput[]>("/api/scenario/list"),
  simulate: (scenario_id: string, overrides?: Record<string, number>) =>
    postJSON<ScenarioResponse>("/api/scenario/simulate", { scenario_id, overrides }),
  backtest: () => getJSON<BacktestResult>("/api/backtest"),
  vessels: (force?: boolean) =>
    getJSON<VesselsResponse>(`/api/vessels${force ? "?force=true" : ""}`),
};
