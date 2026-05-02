// ─────────────────────────────────────────────────────────────
// V-Guard AI — Visionary Agent × CCTV-POS Bridge
// Integration Guide & Production-Ready Usage Example
// ─────────────────────────────────────────────────────────────
//
// FILE: client/src/components/admin/agents/visionary/config.ts

export interface VisionaryConfig {
  cameraId:       string;
  cctvWsEndpoint: string;
  syncIntervalMs: number;
  anomalyThreshold: number;
  showOverlays:   boolean;
  maxEventsCache: number;
}

export const DEFAULT_VISIONARY_CONFIG: VisionaryConfig = {
  cameraId:         "CAM-01",
  cctvWsEndpoint:   process.env.NODE_ENV === "production"
                      ? "wss://api.vguard.ai/ws/cctv"
                      : "ws://localhost:3001/ws/cctv",
  syncIntervalMs:   15_000,    // Poll POS every 15 seconds
  anomalyThreshold: 40,        // Minimum score to show in panel
  showOverlays:     true,      // Bounding box overlays on frame
  maxEventsCache:   100,       // Max bridge events in memory
};

export function buildVisionaryConfig(
  overrides: Partial<VisionaryConfig> = {}
): VisionaryConfig {
  return { ...DEFAULT_VISIONARY_CONFIG, ...overrides };
}

const env = typeof process !== "undefined" ? process.env : {};

export const adminPhoneNumber = "6282122190885";

export const visionEnv = {
  kasirServerUrl: env.KASIR_SERVER_URL ?? "http://localhost:4000/api/transactions",
  whatsappApiUrl: env.WHATSAPP_API_URL ?? "https://api.whatsapp.com/send",
  whatsappApiToken: env.WHATSAPP_API_TOKEN ?? "",
};

export interface KasirTransaction {
  transactionId: string;
  clientId: string;
  cashierId?: number;
  cashierName?: string;
  type?: string;
  amount?: number;
  itemCount?: number;
  timestamp?: string;
  [key: string]: unknown;
}

export async function fetchKasirTransactions(sinceEpochMs: number): Promise<KasirTransaction[]> {
  const url = new URL(visionEnv.kasirServerUrl);
  url.searchParams.set("since", sinceEpochMs.toString());

  const response = await fetch(url.toString(), {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`KASIR fetch failed: ${response.status} ${response.statusText}`);
  }

  return (await response.json()) as KasirTransaction[];
}

export function startKasirSync(
  onTransactions: (transactions: KasirTransaction[]) => void,
  config: VisionaryConfig = DEFAULT_VISIONARY_CONFIG
) {
  const intervalMs = config.syncIntervalMs;

  async function poll() {
    try {
      const since = Date.now() - intervalMs;
      const transactions = await fetchKasirTransactions(since);
      onTransactions(transactions);
    } catch (error) {
      console.error("Kasir sync error:", error);
    }
  }

  poll();
  const timer = setInterval(poll, intervalMs);

  return () => clearInterval(timer);
}

export async function sendWhatsAppNotification(message: string) {
  if (!visionEnv.whatsappApiToken) {
    throw new Error("Missing WHATSAPP_API_TOKEN in environment for WhatsApp notifications.");
  }

  const response = await fetch(visionEnv.whatsappApiUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${visionEnv.whatsappApiToken}`,
    },
    body: JSON.stringify({
      to: adminPhoneNumber,
      message,
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`WhatsApp notification failed: ${response.status} ${response.statusText} ${text}`);
  }

  return response.json();
}

export async function triggerWhatsAppOnHighThreshold(
  config: VisionaryConfig = DEFAULT_VISIONARY_CONFIG,
  anomalyScore: number,
  details?: string
) {
  if (config.anomalyThreshold <= 40) {
    return null;
  }

  const message = `Visionary alert: anomalyThreshold=${config.anomalyThreshold} (>40), anomalyScore=${anomalyScore}. ${details ?? "No extra details provided."}`;
  return sendWhatsAppNotification(message);
}

// ─────────────────────────────────────────────────────────────
// FILE: client/src/components/admin/agents/visionary/types.ts

import type {
  CCTVFrame as BridgeCCTVFrame,
  BridgeEventRecord,
} from "../../../../../server/bridge/cctv-pos-bridge";

// Re-export bridge types for component use
export type { BridgeCCTVFrame as CCTVFrame };

export interface DetectedObject {
  label:      string;
  confidence: number;
  bbox:       { x: number; y: number; w: number; h: number };
  trackId?:   string;
}

export interface BridgeEvent extends BridgeEventRecord {
  // UI-augmented fields
  visualMismatch: boolean;
  timestamp:      Date | string;
}

// ─────────────────────────────────────────────────────────────
// FILE: server/routers/bridge.ts
// tRPC Router — POS Sync Endpoint
// ─────────────────────────────────────────────────────────────

import { z }               from "zod";
import { router, procedure } from "../trpc";
import { db }              from "../../db";
import { bridgeEvents, fraudAlerts } from "../../db/schema";
import { eq, gte, and }   from "drizzle-orm";
import {
  matchTransactionsToFrames,
  buildBridgeEventRecords,
  fetchCCTVFrames,
} from "../bridge/cctv-pos-bridge";
import {
  checkR5_Visual_ItemCountMismatch,
  checkR6_Visual_VoidWithItems,
} from "../fraud.visual";

export const bridgeRouter = router({
  // ── syncPOS: Called by VisionaryAgent every syncIntervalMs ──
  syncPOS: procedure
    .input(z.object({
      clientId: z.string(),
      since:    z.number(),
    }))
    .query(async ({ input }) => {
      const { clientId, since } = input;

      // 1. Fetch recent POS transactions from DB
      //    (Replace with actual POS webhook table query)
      const transactions = await db.query.posTransactions?.findMany?.({
        where: (t: any, { and, gte, eq }: any) =>
          and(eq(t.clientId, parseInt(clientId)), gte(t.timestamp, new Date(since))),
      }) ?? [];

      // 2. Fetch CCTV frames for the period
      const frames = await fetchCCTVFrames(
        parseInt(clientId),
        "CAM-01",  // TODO: support multiple cameras
        since
      );

      // 3. Run Bridge matching algorithm
      const matches = matchTransactionsToFrames(transactions as any, frames);

      // 4. Run R5/R6 visual checks on each match
      const enrichedMatches = matches.map((m) => {
        const r5 = checkR5_Visual_ItemCountMismatch(
          m.transaction.itemCount ?? 0,
          m.frame
        );
        const r6 = checkR6_Visual_VoidWithItems(
          m.transaction.type,
          m.frame
        );

        if (r5.triggered && !m.rules.includes("R5-VISUAL")) {
          m.rules.push("R5-VISUAL");
          m.anomalyScore = Math.min(100, m.anomalyScore + r5.confidence);
        }
        if (r6.triggered && !m.rules.includes("R6-VISUAL")) {
          m.rules.push("R6-VISUAL");
          m.anomalyScore = 100; // Always critical
        }

        return m;
      });

      // 5. Persist anomalous events to DB
      const records = buildBridgeEventRecords(parseInt(clientId), enrichedMatches);

      if (records.length > 0) {
        await db.insert(bridgeEvents).values(
          records.map((r) => ({
            id:               r.id,
            clientId:         r.clientId,
            transactionId:    r.transactionId,
            frameId:          r.frameId,
            anomalyScore:     r.anomalyScore,
            triggeredRules:   r.triggeredRules,
            itemCountMismatch: r.itemCountMismatch,
            status:           r.status,
            posSnapshot:      r.posTransaction as any,
            cctvSnapshot:     r.cctvFrame as any,
          }))
        ).onConflictDoNothing();
      }

      // 6. Return bridge events for UI rendering
      return {
        bridgeEvents:  records,
        totalMatched:  enrichedMatches.length,
        totalAnomalous: records.length,
      };
    }),

  // ── getAlerts: Client portal fraud alert feed ───────────────
  getAlerts: procedure
    .input(z.object({
      clientId: z.string(),
      limit:    z.number().default(50),
    }))
    .query(async ({ input }) => {
      return db.query.fraudAlerts?.findMany?.({
        where: (t: any, { eq }: any) => eq(t.clientId, parseInt(input.clientId)),
        orderBy: (t: any, { desc }: any) => [desc(t.occurredAt)],
        limit: input.limit,
      }) ?? [];
    }),

  // ── resolveAlert: Mark alert as resolved ────────────────────
  resolveAlert: procedure
    .input(z.object({
      alertId:  z.number(),
      clientId: z.string(),
      note:     z.string().optional(),
    }))
    .mutation(async ({ input, ctx }) => {
      await db
        .update(fraudAlerts)
        .set({
          status:     "RESOLVED",
          reviewedAt: new Date(),
          reviewNote: input.note,
        })
        .where(
          and(
            eq(fraudAlerts.id, input.alertId),
            eq(fraudAlerts.clientId, parseInt(input.clientId))
          )
        );
      return { success: true };
    }),
});

// ─────────────────────────────────────────────────────────────
// USAGE IN ClientDashboard.tsx
// ─────────────────────────────────────────────────────────────
//
// import { VisionaryAgent } from "@/components/admin/agents/visionary";
// import { TierGate }        from "@/components/TierGate";
//
// // In JSX:
// <TierGate requiredTier="V-ULTRA">
//   <VisionaryAgent
//     clientId={user.userId}
//     configOverrides={{
//       cameraId:         "CAM-01",
//       syncIntervalMs:   15_000,
//       anomalyThreshold: 40,
//     }}
//   />
// </TierGate>
//
// ─────────────────────────────────────────────────────────────
// WEBHOOK: POS → V-Guard Bridge
// POST /api/webhook/pos-transaction
// ─────────────────────────────────────────────────────────────
//
// Body schema:
// {
//   "clientId":      "VG-2024-00042",
//   "transactionId": "TXN-2024-001234",
//   "cashierId":     3,
//   "cashierName":   "Budi Santoso",
//   "type":          "VOID",          // PENJUALAN | VOID | DISKON | REFUND
//   "amount":        185000,
//   "itemCount":     4,
//   "timestamp":     "2024-06-15T14:32:00+07:00"
// }
//
// The server will:
// 1. Store transaction
// 2. Trigger fetchCCTVFrames() for nearest frame
// 3. Run matchTransactionsToFrames()
// 4. Run R5/R6 visual checks
// 5. Persist BridgeEventRecord if anomalyScore > 0
// 6. Push alert to client portal via WebSocket
// ─────────────────────────────────────────────────────────────
