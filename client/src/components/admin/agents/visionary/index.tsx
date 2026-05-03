// client/src/components/admin/agents/visionary/index.tsx
// ─────────────────────────────────────────────────────────────
// Visionary Agent Panel — CCTV × POS Bridge UI Component
// Features: 15s polling, real-time anomaly detection, WhatsApp notifications
// ─────────────────────────────────────────────────────────────

import React, { useState, useEffect, useCallback } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, Activity, CheckCircle, Zap } from "lucide-react";
import {
  DEFAULT_VISIONARY_CONFIG,
  startKasirSync,
  adminPhoneNumber,
} from "./config";
import type { VisionaryAgentProps, SyncStatus, AnomalySeverity } from "./types";
import { scoreToSeverity, SEVERITY_COLORS } from "./types";

interface BridgeEvent {
  id: string;
  clientId: string;
  transactionId: number;
  frameId?: string;
  anomalyScore: number;
  triggeredRules: string[];
  itemCountMismatch: boolean;
  status: "PENDING_REVIEW" | "REVIEWED" | "ESCALATED" | "DISMISSED";
  timestamp: Date | string;
}

interface VisionaryAgentState {
  syncStatus: SyncStatus;
  lastSyncTime: Date | null;
  recentEvents: BridgeEvent[];
  connectionStatus: "connected" | "disconnected" | "error";
  notificationTarget: string;
  monitoringInterval: number;
}

export default function VisionaryAgent({
  clientId,
  configOverrides,
}: VisionaryAgentProps) {
  const config = { ...DEFAULT_VISIONARY_CONFIG, ...configOverrides };

  const [state, setState] = useState<VisionaryAgentState>({
    syncStatus: "idle",
    lastSyncTime: null,
    recentEvents: [],
    connectionStatus: "connected",
    notificationTarget: adminPhoneNumber,
    monitoringInterval: config.syncIntervalMs,
  });

  // Simulate bridge event polling (in production, this would fetch from API)
  const pollBridgeEvents = useCallback(async () => {
    setState((prev) => ({ ...prev, syncStatus: "syncing" }));

    try {
      // Mock data — in production, fetch from tRPC or API
      const mockEvents: BridgeEvent[] = [
        {
          id: `bridge-${Date.now()}-1`,
          clientId,
          transactionId: 1001,
          frameId: "frame-001",
          anomalyScore: 65,
          triggeredRules: ["R5-VISUAL", "R2"],
          itemCountMismatch: true,
          status: "PENDING_REVIEW",
          timestamp: new Date(),
        },
        {
          id: `bridge-${Date.now()}-2`,
          clientId,
          transactionId: 1002,
          frameId: "frame-002",
          anomalyScore: 35,
          triggeredRules: ["R1"],
          itemCountMismatch: false,
          status: "REVIEWED",
          timestamp: new Date(Date.now() - 30000),
        },
      ];

      setState((prev) => ({
        ...prev,
        syncStatus: "idle",
        lastSyncTime: new Date(),
        recentEvents: mockEvents,
        connectionStatus: "connected",
      }));
    } catch (error) {
      console.error("[VisionaryAgent] Poll error:", error);
      setState((prev) => ({
        ...prev,
        syncStatus: "error",
        connectionStatus: "error",
      }));
    }
  }, [clientId]);

  // Initialize polling on mount
  useEffect(() => {
    pollBridgeEvents();
    const interval = setInterval(pollBridgeEvents, config.syncIntervalMs);

    return () => clearInterval(interval);
  }, [config.syncIntervalMs, pollBridgeEvents]);

  const criticalEvents = state.recentEvents.filter(
    (e) => e.anomalyScore >= 60
  );
  const highRiskCount = state.recentEvents.filter(
    (e) => e.anomalyScore >= 40 && e.anomalyScore < 60
  ).length;

  const formatTime = (date: Date | string | null) => {
    if (!date) return "—";
    const d = typeof date === "string" ? new Date(date) : date;
    return d.toLocaleTimeString("id-ID");
  };

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <Card className="bg-gradient-to-r from-slate-800 to-slate-900 border-slate-700 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">
              👁️ Visionary Agent (V-ULTRA)
            </h2>
            <p className="text-slate-400">
              CCTV × POS Real-Time Bridge & Anomaly Detection
            </p>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-2 mb-2">
              <div
                className={`w-3 h-3 rounded-full ${
                  state.connectionStatus === "connected"
                    ? "bg-green-500 animate-pulse"
                    : state.connectionStatus === "error"
                    ? "bg-red-500"
                    : "bg-yellow-500"
                }`}
              />
              <span
                className={`text-sm font-semibold ${
                  state.connectionStatus === "connected"
                    ? "text-green-400"
                    : state.connectionStatus === "error"
                    ? "text-red-400"
                    : "text-yellow-400"
                }`}
              >
                {state.connectionStatus === "connected"
                  ? "Connected"
                  : state.connectionStatus === "error"
                  ? "Error"
                  : "Connecting"}
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Monitoring: {state.notificationTarget}
            </p>
          </div>
        </div>
      </Card>

      {/* Status Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-slate-800 border-slate-700 p-4">
          <div className="flex items-center gap-3">
            <Activity className="w-5 h-5 text-cyan-400" />
            <div>
              <p className="text-xs text-slate-400">Sync Interval</p>
              <p className="text-lg font-bold text-white">
                {config.syncIntervalMs / 1000}s
              </p>
            </div>
          </div>
        </Card>

        <Card className="bg-slate-800 border-slate-700 p-4">
          <div className="flex items-center gap-3">
            <Zap className="w-5 h-5 text-yellow-400" />
            <div>
              <p className="text-xs text-slate-400">Recent Events</p>
              <p className="text-lg font-bold text-white">
                {state.recentEvents.length}
              </p>
            </div>
          </div>
        </Card>

        <Card className="bg-slate-800 border-slate-700 p-4">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <div>
              <p className="text-xs text-slate-400">Critical</p>
              <p className="text-lg font-bold text-white">
                {criticalEvents.length}
              </p>
            </div>
          </div>
        </Card>

        <Card className="bg-slate-800 border-slate-700 p-4">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-green-400" />
            <div>
              <p className="text-xs text-slate-400">Last Sync</p>
              <p className="text-xs font-mono text-white">
                {formatTime(state.lastSyncTime)}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Recent Events Table */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          Recent Bridge Events
        </h3>

        {state.recentEvents.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-slate-400">No events detected</p>
          </div>
        ) : (
          <div className="space-y-3">
            {state.recentEvents.map((event) => {
              const severity = scoreToSeverity(event.anomalyScore);
              const severityColor = SEVERITY_COLORS[severity];

              return (
                <div
                  key={event.id}
                  className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg border border-slate-600 hover:border-slate-500 transition-colors"
                >
                  <div className="flex items-center gap-4 flex-1">
                    <div
                      className="w-12 h-12 rounded-lg flex items-center justify-center text-white font-bold text-sm"
                      style={{ backgroundColor: severityColor }}
                    >
                      {event.anomalyScore}
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold text-white">
                        Transaction #{event.transactionId}
                      </p>
                      <div className="flex gap-2 mt-1 flex-wrap">
                        {event.triggeredRules.map((rule) => (
                          <Badge
                            key={rule}
                            className="bg-slate-600 text-slate-200 text-xs"
                          >
                            {rule}
                          </Badge>
                        ))}
                        {event.itemCountMismatch && (
                          <Badge className="bg-orange-600/50 text-orange-200 text-xs">
                            Item Mismatch
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-slate-400 mt-2">
                        {formatTime(event.timestamp)} • Frame: {event.frameId}
                      </p>
                    </div>
                  </div>
                  <Badge
                    className={
                      event.status === "PENDING_REVIEW"
                        ? "bg-yellow-600 text-white"
                        : event.status === "ESCALATED"
                        ? "bg-red-600 text-white"
                        : "bg-green-600 text-white"
                    }
                  >
                    {event.status}
                  </Badge>
                </div>
              );
            })}
          </div>
        )}
      </Card>

      {/* Configuration Info */}
      <Card className="bg-slate-800 border-slate-700 p-4">
        <h4 className="text-sm font-semibold text-white mb-3">
          Configuration
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          <div>
            <p className="text-slate-400">Camera ID</p>
            <p className="text-cyan-400 font-mono">{config.cameraId}</p>
          </div>
          <div>
            <p className="text-slate-400">Anomaly Threshold</p>
            <p className="text-cyan-400 font-mono">{config.anomalyThreshold}</p>
          </div>
          <div>
            <p className="text-slate-400">Max Events Cache</p>
            <p className="text-cyan-400 font-mono">{config.maxEventsCache}</p>
          </div>
          <div>
            <p className="text-slate-400">Notification Target</p>
            <p className="text-cyan-400 font-mono">
              {state.notificationTarget}
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
