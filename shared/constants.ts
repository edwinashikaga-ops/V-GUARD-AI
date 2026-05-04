/**
 * ============================================================
 * V-GUARD AI SHARED CONSTANTS
 * ============================================================
 */

/**
 * TIER SYSTEM
 */
export const TIERS = {
  DEMO: { id: "DEMO", name: "DEMO", monthlyPrice: 0, setupFee: 0, agents: 2 },
  "V-LITE": {
    id: "V-LITE",
    name: "V-LITE",
    monthlyPrice: 150000,
    setupFee: 500000,
    agents: 4,
  },
  "V-PRO": {
    id: "V-PRO",
    name: "V-PRO",
    monthlyPrice: 450000,
    setupFee: 1500000,
    agents: 10,
  },
  "V-ADVANCE": {
    id: "V-ADVANCE",
    name: "V-ADVANCE",
    monthlyPrice: 1200000,
    setupFee: 5000000,
    agents: 10,
  },
  "V-ELITE": {
    id: "V-ELITE",
    name: "V-ELITE",
    monthlyPrice: 3500000,
    setupFee: 15000000,
    agents: 10,
  },
  "V-ULTRA": {
    id: "V-ULTRA",
    name: "V-ULTRA",
    monthlyPrice: 0,
    setupFee: 0,
    agents: 10,
  },
} as const;

/**
 * AI AGENTS (10 Total)
 */
export const AGENTS = [
  {
    id: 1,
    name: "Visionary",
    role: "CCTV Visual Intelligence",
    icon: "👁️",
    minTier: "V-ADVANCE",
    description: "Real-time CCTV analysis and visual anomaly detection",
  },
  {
    id: 2,
    name: "Concierge",
    role: "CS Intelligence",
    icon: "🤝",
    minTier: "V-LITE",
    description: "Customer service automation and support",
  },
  {
    id: 3,
    name: "GrowthHacker",
    role: "Marketing Automation",
    icon: "📣",
    minTier: "V-LITE",
    description: "Marketing campaign automation and growth optimization",
  },
  {
    id: 4,
    name: "Liaison",
    role: "POS Integration",
    icon: "🔗",
    minTier: "V-PRO",
    description: "POS system integration and data synchronization",
  },
  {
    id: 5,
    name: "Analyst",
    role: "Financial Forensic",
    icon: "🏦",
    minTier: "V-PRO",
    description: "Financial analysis and forensic investigation",
  },
  {
    id: 6,
    name: "Stockmaster",
    role: "Inventory OCR",
    icon: "📦",
    minTier: "V-PRO",
    description: "Inventory management and OCR processing",
  },
  {
    id: 7,
    name: "Watchdog",
    role: "Fraud Detector",
    icon: "🐕",
    minTier: "V-LITE",
    description: "Real-time fraud detection and alerting",
  },
  {
    id: 8,
    name: "Sentinel",
    role: "Infra Monitor",
    icon: "🖥️",
    minTier: "V-PRO",
    description: "Infrastructure monitoring and system health",
  },
  {
    id: 9,
    name: "Legalist",
    role: "Compliance",
    icon: "⚖️",
    minTier: "V-PRO",
    description: "Compliance monitoring and regulatory reporting",
  },
  {
    id: 10,
    name: "Treasurer",
    role: "Gross Revenue Monitor",
    icon: "💰",
    minTier: "V-LITE",
    description: "Revenue tracking and financial monitoring",
  },
] as const;

/**
 * FRAUD RULES
 */
export const FRAUD_RULE_TIERS = {
  R1: "V-LITE",
  R2: "V-LITE",
  R3: "V-LITE",
  R4: "V-PRO",
  R5: "V-PRO",
  R6: "V-PRO",
} as const;

/**
 * FEATURE ACCESS BY TIER
 */
export const FEATURE_ACCESS = {
  fraud_rules_r1_r2_r3: ["DEMO", "V-LITE", "V-PRO", "V-ADVANCE", "V-ELITE", "V-ULTRA"],
  fraud_rules_r4_r5_r6: ["V-PRO", "V-ADVANCE", "V-ELITE", "V-ULTRA"],
  bank_audit: ["V-PRO", "V-ADVANCE", "V-ELITE", "V-ULTRA"],
  ocr_invoice: ["V-PRO", "V-ADVANCE", "V-ELITE", "V-ULTRA"],
  cctv_ai_live: ["V-ADVANCE", "V-ELITE", "V-ULTRA"],
  multi_branch: ["V-ADVANCE", "V-ELITE", "V-ULTRA"],
  dedicated_server: ["V-ELITE", "V-ULTRA"],
  forensic_deep_scan: ["V-ELITE", "V-ULTRA"],
  white_label: ["V-ULTRA"],
  neural_network: ["V-ULTRA"],
} as const;

/**
 * DEMO MODE
 */
export const DEMO_CONFIG = {
  DURATION_MINUTES: 15,
  DURATION_MS: 15 * 60 * 1000,
  PREVIEW_TIER: "V-LITE",
  AVAILABLE_AGENTS: [2, 7], // Concierge, Watchdog
  WATERMARK_TEXT: "DEMO MODE",
  WATERMARK_OPACITY: 0.15,
} as const;

/**
 * REFERRAL PROGRAM
 */
export const REFERRAL_CONFIG = {
  COMMISSION_RATE: 10, // Percent
  MIN_REFERRAL_TIER: "V-LITE",
} as const;

/**
 * COLORS & STYLING
 */
export const COLORS = {
  primary: "#00D4FF",
  primaryDark: "#0B0F1A",
  danger: "#FF3B5C",
  warning: "#FFAB00",
  success: "#00D97E",
  info: "#7B2FFF",
  neutral: "#8A92A2",
  border: "#2A3142",
  background: "#0B0F1A",
  surface: "#141B28",
  surfaceLight: "#1F2937",
} as const;

/**
 * FRAUD RULE COLORS
 */
export const FRAUD_COLORS = {
  R1: "#FF3B5C", // Critical - Red
  R2: "#FF3B5C", // Critical - Red
  R3: "#FFAB00", // Warning - Orange
  R4: "#FFAB00", // Warning - Orange
  R5: "#7B2FFF", // Info - Purple
  R6: "#FF3B5C", // Critical - Red
} as const;

/**
 * RISK LEVELS
 */
export const RISK_LEVELS = {
  LOW: { label: "Low", color: "#00D97E", value: 0 },
  MEDIUM: { label: "Medium", color: "#FFAB00", value: 1 },
  HIGH: { label: "High", color: "#FF3B5C", value: 2 },
} as const;

/**
 * TRANSACTION TYPES
 */
export const TRANSACTION_TYPES = {
  PENJUALAN: "PENJUALAN",
  VOID: "VOID",
  DISKON: "DISKON",
  REFUND: "REFUND",
} as const;

/**
 * ALERT STATUSES
 */
export const ALERT_STATUSES = {
  NEW: "NEW",
  ACKNOWLEDGED: "ACKNOWLEDGED",
  RESOLVED: "RESOLVED",
  FALSE_POSITIVE: "FALSE_POSITIVE",
} as const;

/**
 * CLIENT STATUSES
 */
export const CLIENT_STATUSES = {
  PENDING: "pending",
  ACTIVE: "aktif",
  SUSPENDED: "suspended",
  CANCELLED: "cancelled",
} as const;

/**
 * INVOICE STATUSES
 */
export const INVOICE_STATUSES = {
  PENDING: "PENDING",
  PAID: "PAID",
  OVERDUE: "OVERDUE",
  CANCELLED: "CANCELLED",
} as const;

/**
 * PAGINATION
 */
export const PAGINATION = {
  DEFAULT_LIMIT: 20,
  MAX_LIMIT: 100,
} as const;

/**
 * TIMEZONE
 */
export const TIMEZONE = {
  DEFAULT: "Asia/Jakarta",
  OFFSET_HOURS: 7,
} as const;

/**
 * BUSINESS HOURS (WIB - Western Indonesia Time)
 */
export const BUSINESS_HOURS = {
  START: 7, // 07:00
  END: 23, // 23:00
} as const;

/**
 * HELPER: Check if tier has access to feature
 */
export function hasFeatureAccess(
  tier: string | undefined | null,
  feature: keyof typeof FEATURE_ACCESS
): boolean {
  const allowedTiers = FEATURE_ACCESS[feature];
  if (!allowedTiers || !tier) return false;
  return (allowedTiers as readonly string[]).includes(tier);
}

/**
 * HELPER: Check if agent is unlocked for tier
 */
export function isAgentUnlocked(agentId: number, tier: string | undefined | null): boolean {
  const agent = AGENTS.find((a) => a.id === agentId);
  if (!agent || !tier) return false;

  const tierOrder = ["DEMO", "V-LITE", "V-PRO", "V-ADVANCE", "V-ELITE", "V-ULTRA"];
  const tierIndex = tierOrder.indexOf(tier);
  const minTierIndex = tierOrder.indexOf(agent.minTier);

  return tierIndex >= minTierIndex;
}

/**
 * HELPER: Get tier pricing
 */
export function getTierPricing(tier: string) {
  return TIERS[tier as keyof typeof TIERS] || TIERS["V-LITE"];
}

/**
 * HELPER: Format currency (IDR)
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * HELPER: Generate Client ID
 */
export function generateClientId(): string {
  const prefix = "VG";
  const timestamp = Date.now().toString(36).toUpperCase();
  const random = Math.random().toString(36).substring(2, 7).toUpperCase();
  return `${prefix}-${timestamp}${random}`;
}

/**
 * HELPER: Generate Invoice Number
 */
export function generateInvoiceNumber(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  const random = Math.random().toString(36).substring(2, 6).toUpperCase();
  return `INV-${year}${month}${day}-${random}`;
}

/**
 * HELPER: Generate Referral Link
 */
export function generateReferralLink(clientId: string): string {
  return `https://v-guard-ai.com/?ref=${clientId}&source=referral`;
}
