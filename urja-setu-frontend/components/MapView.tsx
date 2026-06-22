"use client";

import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { MapboxOverlay } from "@deck.gl/mapbox";
import { PathLayer, ScatterplotLayer, TextLayer } from "@deck.gl/layers";
import type { PickingInfo } from "@deck.gl/core";

import type { Corridor, CrudeSource, MapState, Refinery, Vessel } from "@/lib/api";
import { RISK_RGB } from "@/lib/risk";

const BASEMAP = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";
const FONT = "ui-sans-serif, system-ui, sans-serif";
const HIGHLIGHT: [number, number, number, number] = [239, 68, 68, 255];

const CHOKEPOINT_SHORT: Record<string, string> = {
  hormuz: "Strait of Hormuz",
  "bab-el-mandeb": "Bab-el-Mandeb",
  "cape-good-hope": "Cape of Good Hope",
  malacca: "Strait of Malacca",
};

const TOOLTIP_STYLE: Record<string, string> = {
  backgroundColor: "#0f172a",
  color: "#e2e8f0",
  fontSize: "12px",
  lineHeight: "1.4",
  padding: "8px 10px",
  borderRadius: "8px",
  border: "1px solid #1e293b",
  maxWidth: "260px",
};

function buildLayers(data: MapState, highlight: string | null, vessels: Vessel[]) {
  const path = (c: Corridor) => c.path.map((p) => [p.lon, p.lat] as [number, number]);

  // Soft red glow under the corridor currently being simulated.
  const glow = new PathLayer<Corridor>({
    id: "corridor-glow",
    data: data.corridors.filter((c) => c.id === highlight),
    getPath: path,
    getColor: [239, 68, 68, 70],
    getWidth: 16,
    widthUnits: "pixels",
    capRounded: true,
    jointRounded: true,
  });

  const corridors = new PathLayer<Corridor>({
    id: "corridors",
    data: data.corridors,
    getPath: path,
    getColor: (c: Corridor) =>
      c.id === highlight ? HIGHLIGHT : ([...RISK_RGB[c.risk_level], 235] as [number, number, number, number]),
    getWidth: (c: Corridor) => (c.id === highlight ? 5.5 : 2.5 + c.disruption_probability * 6),
    widthUnits: "pixels",
    widthMinPixels: 2,
    capRounded: true,
    jointRounded: true,
    pickable: true,
    updateTriggers: { getColor: [highlight], getWidth: [highlight] },
  });

  const chokepoints = new ScatterplotLayer<Corridor>({
    id: "chokepoints",
    data: data.corridors,
    getPosition: (c: Corridor) => [c.path[0].lon, c.path[0].lat] as [number, number],
    getRadius: 5,
    radiusUnits: "pixels",
    getFillColor: (c: Corridor) => (c.id === highlight ? HIGHLIGHT : ([15, 23, 42, 255] as [number, number, number, number])),
    getLineColor: [226, 232, 240, 230],
    lineWidthMinPixels: 1.5,
    stroked: true,
    pickable: true,
    updateTriggers: { getFillColor: [highlight] },
  });

  const sources = new ScatterplotLayer<CrudeSource>({
    id: "sources",
    data: data.sources,
    getPosition: (s: CrudeSource) => [s.location.lon, s.location.lat] as [number, number],
    getRadius: 4.5,
    radiusUnits: "pixels",
    getFillColor: [251, 191, 36, 220],
    getLineColor: [15, 23, 42, 220],
    lineWidthMinPixels: 1,
    stroked: true,
    pickable: true,
  });

  const refineries = new ScatterplotLayer<Refinery>({
    id: "refineries",
    data: data.refineries,
    getPosition: (r: Refinery) => [r.location.lon, r.location.lat] as [number, number],
    getRadius: (r: Refinery) => Math.sqrt(r.capacity_kbd) * 1400,
    radiusUnits: "meters",
    radiusMinPixels: 5,
    radiusMaxPixels: 30,
    getFillColor: [16, 185, 129, 210],
    getLineColor: [226, 252, 245, 200],
    lineWidthMinPixels: 1.2,
    stroked: true,
    pickable: true,
  });

  const labelOutline = { outlineWidth: 2, outlineColor: [2, 6, 23, 255] as [number, number, number, number], fontSettings: { sdf: true } };

  const chokepointLabels = new TextLayer<Corridor>({
    id: "chokepoint-labels",
    data: data.corridors,
    getPosition: (c: Corridor) => [c.path[0].lon, c.path[0].lat] as [number, number],
    getText: (c: Corridor) => CHOKEPOINT_SHORT[c.id] ?? c.name,
    getSize: 10.5,
    getColor: [241, 245, 249, 240],
    getTextAnchor: "middle",
    getAlignmentBaseline: "bottom",
    getPixelOffset: [0, -9],
    fontFamily: FONT,
    fontWeight: 600,
    ...labelOutline,
  });

  const sourceLabels = new TextLayer<CrudeSource>({
    id: "source-labels",
    data: data.sources,
    getPosition: (s: CrudeSource) => [s.location.lon, s.location.lat] as [number, number],
    getText: (s: CrudeSource) => s.country,
    getSize: 9,
    getColor: [253, 224, 161, 230],
    getTextAnchor: "middle",
    getAlignmentBaseline: "top",
    getPixelOffset: [0, 9],
    fontFamily: FONT,
    ...labelOutline,
  });

  const refineryLabels = new TextLayer<Refinery>({
    id: "refinery-labels",
    data: data.refineries,
    getPosition: (r: Refinery) => [r.location.lon, r.location.lat] as [number, number],
    getText: (r: Refinery) => r.name,
    getSize: 10,
    getColor: [209, 250, 229, 235],
    getTextAnchor: "start",
    getAlignmentBaseline: "center",
    getPixelOffset: [11, 0],
    fontFamily: FONT,
    ...labelOutline,
  });

  const vesselLayer = new ScatterplotLayer<Vessel>({
    id: "vessels",
    data: vessels,
    getPosition: (v: Vessel) => [v.lon, v.lat] as [number, number],
    getRadius: 2.2,
    radiusUnits: "pixels",
    getFillColor: [56, 189, 248, 210],
    stroked: false,
    pickable: true,
  });

  return [glow, corridors, vesselLayer, refineries, sources, chokepoints, refineryLabels, sourceLabels, chokepointLabels];
}

function getTooltip({ object, layer }: PickingInfo) {
  if (!object || !layer) return null;
  let html = "";
  if (layer.id === "corridors" || layer.id === "chokepoints") {
    const c = object as Corridor;
    html =
      `<b>${c.name}</b><br/>` +
      `Risk: ${c.risk_level}<br/>` +
      `Disruption probability: ${Math.round(c.disruption_probability * 100)}%<br/>` +
      `Share of India's crude: ${Math.round(c.throughput_share * 100)}%`;
  } else if (layer.id === "refineries") {
    const r = object as Refinery;
    html = `<b>${r.name}</b> · ${r.operator}<br/>Capacity: ${r.capacity_kbd.toLocaleString()} kbd<br/>Grades: ${r.grade_slate.join(", ")}`;
  } else if (layer.id === "sources") {
    const s = object as CrudeSource;
    html = `<b>${s.country}</b> — ${s.grade}<br/>` + (s.spot_price_usd != null ? `Spot: $${s.spot_price_usd}/bbl` : "");
  } else if (layer.id === "vessels") {
    const v = object as Vessel;
    html = `<b>${v.name}</b><br/>MMSI ${v.mmsi} · live AIS`;
  } else {
    return null;
  }
  return { html, style: TOOLTIP_STYLE };
}

export default function MapView({
  data,
  highlight = null,
  vessels = [],
}: {
  data: MapState | null;
  highlight?: string | null;
  vessels?: Vessel[];
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const overlayRef = useRef<MapboxOverlay | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: BASEMAP,
      center: [60, 16],
      zoom: 3,
      minZoom: 2,
      attributionControl: { compact: true },
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right");
    const overlay = new MapboxOverlay({ interleaved: false, layers: [], getTooltip });
    map.addControl(overlay as unknown as maplibregl.IControl);
    mapRef.current = map;
    overlayRef.current = overlay;
    return () => {
      map.remove();
      mapRef.current = null;
      overlayRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!overlayRef.current || !data) return;
    overlayRef.current.setProps({ layers: buildLayers(data, highlight, vessels), getTooltip });
  }, [data, highlight, vessels]);

  return (
    <div className="absolute inset-0">
      <div ref={containerRef} className="h-full w-full" />
    </div>
  );
}
