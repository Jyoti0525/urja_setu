"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useState } from "react";

import { api, type HealthResponse, type LiveMeta, type MapState } from "@/lib/api";
import {
  CorridorPanel,
  Header,
  IntelBar,
  Legend,
  SignalPanel,
} from "@/components/Overlay";
import { ScenarioDrawer } from "@/components/ScenarioDrawer";
import { MetricsDrawer } from "@/components/MetricsDrawer";
import { MaritimeTrafficPanel } from "@/components/MaritimeTrafficPanel";

// MapLibre/deck.gl touch `window`; load client-only.
const MapView = dynamic(() => import("@/components/MapView"), {
  ssr: false,
  loading: () => (
    <div className="absolute inset-0 grid place-items-center text-slate-500">
      Loading digital twin…
    </div>
  ),
});

export default function Home() {
  const [data, setData] = useState<MapState | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [meta, setMeta] = useState<LiveMeta | null>(null);
  const [isLive, setIsLive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [metricsOpen, setMetricsOpen] = useState(false);
  const [highlight, setHighlight] = useState<string | null>(null);
  const [trafficOpen, setTrafficOpen] = useState(false);

  useEffect(() => {
    api.map().then(setData).catch((e: unknown) =>
      setError(e instanceof Error ? e.message : String(e)),
    );
    api.health().then(setHealth).catch(() => {});
  }, []);

  const goLive = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await api.liveRisk();
      setData({
        corridors: r.corridors,
        refineries: r.refineries,
        sources: r.sources,
        signals: r.signals,
      });
      setMeta(r.meta);
      setIsLive(true);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <main className="relative h-screen w-screen overflow-hidden bg-slate-950">
      <MapView data={data} highlight={highlight} />

      <Header
        health={health}
        isLive={isLive}
        loading={loading}
        meta={meta}
        onGoLive={goLive}
        onSimulate={() => {
          setMetricsOpen(false);
          setDrawerOpen(true);
        }}
        onBacktest={() => {
          setDrawerOpen(false);
          setMetricsOpen(true);
        }}
        onVessels={() => setTrafficOpen(true)}
        vesselsActive={trafficOpen}
      />
      <IntelBar meta={isLive ? meta : null} />
      <CorridorPanel data={data} />
      {data && <SignalPanel signals={data.signals} />}
      <Legend />
      <ScenarioDrawer
        open={drawerOpen}
        onClose={() => {
          setDrawerOpen(false);
          setHighlight(null);
        }}
        onAffectedCorridor={setHighlight}
      />
      <MetricsDrawer open={metricsOpen} onClose={() => setMetricsOpen(false)} />
      <MaritimeTrafficPanel open={trafficOpen} onClose={() => setTrafficOpen(false)} />

      {error && (
        <div className="absolute inset-x-0 bottom-4 z-20 mx-auto w-fit rounded-lg border border-red-500/40 bg-slate-950/90 px-4 py-2 text-sm text-red-300">
          {error} — is the API running on{" "}
          <code className="text-slate-200">http://localhost:6006</code>?
        </div>
      )}
    </main>
  );
}
