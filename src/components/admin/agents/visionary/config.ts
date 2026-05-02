// client/src/components/admin/agents/visionary/config.ts
// ─────────────────────────────────────────────────────────────
// Visionary Agent — Configuration, Kasir Sync & WhatsApp Notif
// ─────────────────────────────────────────────────────────────

export interface VisionaryConfig {
  cameraId:         string;
  cctvWsEndpoint:   string;
  syncIntervalMs:   number;
  anomalyThreshold: number;
  showOverlays:     boolean;
  maxEventsCache:   number;
}

export const DEFAULT_VISIONARY_CONFIG: VisionaryConfig = {
  cameraId:         "CAM-01",
  cctvWsEndpoint:   process.env.NODE_ENV === "production"
                      ? "wss://api.vguard.ai/ws/cctv"
                      : "ws://localhost:3001/ws/cctv",
  syncIntervalMs:   15_000,   // Poll POS every 15 seconds
  anomalyThreshold: 40,       // Minimum score to show in panel
  showOverlays:     true,     // Bounding box overlays on frame
  maxEventsCache:   100,      // Max bridge events in memory
};

export function buildVisionaryConfig(
  overrides: Partial<VisionaryConfig> = {}
): VisionaryConfig {
  return { ...DEFAULT_VISIONARY_CONFIG, ...overrides };
}

// ── Environment & Constants ───────────────────────────────────

const env = typeof process !== "undefined" ? process.env : {};

export const adminPhoneNumber = "6282122190885";

export const visionEnv = {
  kasirServerUrl:   env.KASIR_SERVER_URL    ?? "http://localhost:4000/api/transactions",
  whatsappApiUrl:   env.WHATSAPP_API_URL    ?? "https://api.whatsapp.com/send",
  whatsappApiToken: env.WHATSAPP_API_TOKEN  ?? "",
};

// ── Kasir Transaction Type ────────────────────────────────────

export interface KasirTransaction {
  transactionId: string;
  clientId:      string;
  cashierId?:    number;
  cashierName?:  string;
  type?:         string;
  amount?:       number;
  itemCount?:    number;
  timestamp?:    string;
  [key: string]: unknown;
}

// ── Kasir Fetch ───────────────────────────────────────────────

export async function fetchKasirTransactions(
  sinceEpochMs: number
): Promise<KasirTransaction[]> {
  const url = new URL(visionEnv.kasirServerUrl);
  url.searchParams.set("since", sinceEpochMs.toString());

  const response = await fetch(url.toString(), {
    method:  "GET",
    headers: { "Content-Type": "application/json" },
  });

  if (!response.ok) {
    throw new Error(
      `KASIR fetch failed: ${response.status} ${response.statusText}`
    );
  }

  return (await response.json()) as KasirTransaction[];
}

// ── Kasir Polling Sync ────────────────────────────────────────

export function startKasirSync(
  onTransactions: (transactions: KasirTransaction[]) => void,
  config: VisionaryConfig = DEFAULT_VISIONARY_CONFIG
): () => void {
  const intervalMs = config.syncIntervalMs;

  async function poll() {
    try {
      const since        = Date.now() - intervalMs;
      const transactions = await fetchKasirTransactions(since);
      onTransactions(transactions);
    } catch (error) {
      console.error("[VisionaryConfig] Kasir sync error:", error);
    }
  }

  poll();
  const timer = setInterval(poll, intervalMs);

  // Returns cleanup function
  return () => clearInterval(timer);
}

// ── WhatsApp Notification ─────────────────────────────────────

export async function sendWhatsAppNotification(message: string): Promise<unknown> {
  if (!visionEnv.whatsappApiToken) {
    throw new Error(
      "Missing WHATSAPP_API_TOKEN in environment for WhatsApp notifications."
    );
  }

  const response = await fetch(visionEnv.whatsappApiUrl, {
    method:  "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization:  `Bearer ${visionEnv.whatsappApiToken}`,
    },
    body: JSON.stringify({
      to:      adminPhoneNumber,
      message,
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(
      `WhatsApp notification failed: ${response.status} ${response.statusText} ${text}`
    );
  }

  return response.json();
}

// ── Threshold-based WA Trigger ────────────────────────────────

export async function triggerWhatsAppOnHighThreshold(
  config:       VisionaryConfig = DEFAULT_VISIONARY_CONFIG,
  anomalyScore: number,
  details?:     string
): Promise<unknown | null> {
  if (config.anomalyThreshold <= 40) return null;

  const message =
    `⚠️ Visionary Alert — anomalyThreshold=${config.anomalyThreshold} (>40), ` +
    `anomalyScore=${anomalyScore}. ${details ?? "No extra details provided."}`;

  return sendWhatsAppNotification(message);
}
