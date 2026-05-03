// client/src/components/admin/agents/visionary/types.ts
// ─────────────────────────────────────────────────────────────
// Visionary Agent — TypeScript Interfaces & Type Re-exports
// ─────────────────────────────────────────────────────────────

import type {
  CCTVFrame as BridgeCCTVFrame,
  BridgeEventRecord,
} from "../../../../../server/bridge/cctv-pos-bridge";

// ── Re-exports from Bridge ────────────────────────────────────
// Alias BridgeCCTVFrame → CCTVFrame for cleaner component usage

export type { BridgeCCTVFrame as CCTVFrame };

// ── Object Detection ──────────────────────────────────────────

export interface DetectedObject {
  label:      string;       // "product" | "person" | "cashier" | "hand"
  confidence: number;       // 0.0 – 1.0
  bbox: {
    x: number;              // Left offset as % of frame width
    y: number;              // Top offset as % of frame height
    w: number;              // Width as % of frame width
    h: number;              // Height as % of frame height
  };
  trackId?:   string;       // Persistent object ID across frames
}

// ── Bridge Event (UI-augmented) ───────────────────────────────

export interface BridgeEvent extends BridgeEventRecord {
  /**
   * True when CCTV item count diverges from POS receipt by > threshold.
   * Corresponds to R5-VISUAL rule.
   */
  visualMismatch: boolean;

  /**
   * Typed as Date | string — component should normalise to Date
   * via: new Date(event.timestamp)
   */
  timestamp: Date | string;
}

// ── Visionary Component Props ─────────────────────────────────

export interface VisionaryAgentProps {
  clientId:        string;
  configOverrides?: Partial<import("./config").VisionaryConfig>;
}

// ── Sync Status ───────────────────────────────────────────────

export type SyncStatus = "syncing" | "idle" | "error";

// ── Anomaly Severity (for UI colouring) ──────────────────────

export type AnomalySeverity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export function scoreToSeverity(score: number): AnomalySeverity {
  if (score >= 80) return "CRITICAL";
  if (score >= 60) return "HIGH";
  if (score >= 40) return "MEDIUM";
  return "LOW";
}

export const SEVERITY_COLORS: Record<AnomalySeverity, string> = {
  CRITICAL: "#FF3B5C",
  HIGH:     "#FF6B00",
  MEDIUM:   "#FFAB00",
  LOW:      "#22d3ee",
};
