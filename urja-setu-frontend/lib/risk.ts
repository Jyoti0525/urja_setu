import type { RiskLevel } from "./api";

/** deck.gl RGB triplets for corridor risk levels. */
export const RISK_RGB: Record<RiskLevel, [number, number, number]> = {
  low: [34, 197, 94],
  moderate: [234, 179, 8],
  high: [249, 115, 22],
  critical: [239, 68, 68],
};

/** CSS hex for UI chips / legend. */
export const RISK_HEX: Record<RiskLevel, string> = {
  low: "#22c55e",
  moderate: "#eab308",
  high: "#f97316",
  critical: "#ef4444",
};

export const RISK_LABEL: Record<RiskLevel, string> = {
  low: "Low",
  moderate: "Moderate",
  high: "High",
  critical: "Critical",
};

/** Map a disruption probability (0..1) to a risk band. Mirrors backend intent. */
export function riskFromProbability(p: number): RiskLevel {
  if (p >= 0.5) return "critical";
  if (p >= 0.25) return "high";
  if (p >= 0.1) return "moderate";
  return "low";
}

export const pct = (x: number): string => `${Math.round(x * 100)}%`;
