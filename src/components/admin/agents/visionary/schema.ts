// db/schema.ts
// ─────────────────────────────────────────────────────────────
// V-Guard AI v1.0.0 — Drizzle ORM Master Schema
// Tables: clients, invoices, credentials, fraud_alerts,
//         bridge_events, agent_configs, audit_logs
// ─────────────────────────────────────────────────────────────
import {
  pgTable,
  serial,
  text,
  integer,
  boolean,
  timestamp,
  real,
  jsonb,
  pgEnum,
  varchar,
  index,
  uniqueIndex,
} from "drizzle-orm/pg-core";
import { relations } from "drizzle-orm";

// ── Enums ─────────────────────────────────────────────────────

export const tierEnum = pgEnum("tier", [
  "DEMO",
  "V-LITE",
  "V-PRO",
  "V-ADVANCE",
  "V-ELITE",
  "V-ULTRA",
]);

export const kycStatusEnum = pgEnum("kyc_status", [
  "PENDING",      // Form submitted, awaiting admin review
  "REVIEWING",    // Admin actively reviewing KTP
  "APPROVED",     // KYC passed — invoice will be generated
  "REJECTED",     // KYC failed — client notified
  "SUSPENDED",    // Post-approval account suspension
]);

export const invoiceStatusEnum = pgEnum("invoice_status", [
  "DRAFT",
  "SENT",
  "PAID",
  "OVERDUE",
  "CANCELLED",
]);

export const fraudSeverityEnum = pgEnum("fraud_severity", [
  "LOW",
  "MEDIUM",
  "HIGH",
  "CRITICAL",
]);

export const fraudStatusEnum = pgEnum("fraud_status", [
  "NEW",
  "ACKNOWLEDGED",
  "RESOLVED",
  "FALSE_POSITIVE",
]);

export const bridgeStatusEnum = pgEnum("bridge_status", [
  "PENDING_REVIEW",
  "REVIEWED",
  "ESCALATED",
  "DISMISSED",
]);

// ── Table: clients ─────────────────────────────────────────────
// Core entity — one row per registered business client

export const clients = pgTable(
  "clients",
  {
    id:            serial("id").primaryKey(),

    // ── Registration Data ──────────────────────────────────────
    fullName:      text("full_name").notNull(),
    businessName:  text("business_name").notNull(),
    whatsapp:      varchar("whatsapp", { length: 20 }).notNull(),
    email:         text("email"),
    address:       text("address"),

    // ── KYC ───────────────────────────────────────────────────
    kycStatus:     kycStatusEnum("kyc_status").notNull().default("PENDING"),
    ktpImageUrl:   text("ktp_image_url"),           // S3/R2 URL
    ktpVerifiedAt: timestamp("ktp_verified_at"),
    ktpVerifiedBy: integer("kyc_verified_by"),      // FK → admin user id
    kycNotes:      text("kyc_notes"),               // Admin notes on rejection

    // ── Subscription ──────────────────────────────────────────
    tier:          tierEnum("tier").notNull().default("DEMO"),
    packageName:   text("package_name"),            // "V-LITE", "V-PRO", "V-ULTRA"
    subscriptionStartDate: timestamp("subscription_start_date"),
    subscriptionEndDate:   timestamp("subscription_end_date"),
    isActive:      boolean("is_active").notNull().default(false),

    // ── Credentials (unlocked after payment) ──────────────────
    pluginLink:    text("plugin_link"),             // Download URL for plugin
    portalUserId:  varchar("portal_user_id", { length: 50 }),
    portalPasswordHash: text("portal_password_hash"),   // bcrypt hash
    apiKey:        text("api_key"),                 // Generated API key

    // ── CCTV / POS Config ─────────────────────────────────────
    cameraIds:     jsonb("camera_ids").$type<string[]>().default([]),
    posIntegration: text("pos_integration"),        // "moka", "majoo", "pawoon", "custom"
    webhookUrl:    text("webhook_url"),

    // ── Timestamps ────────────────────────────────────────────
    registeredAt:  timestamp("registered_at").notNull().defaultNow(),
    updatedAt:     timestamp("updated_at").notNull().defaultNow(),
    deletedAt:     timestamp("deleted_at"),         // Soft delete
  },
  (t) => ({
    whatsappIdx:   uniqueIndex("clients_whatsapp_idx").on(t.whatsapp),
    userIdIdx:     uniqueIndex("clients_portal_user_id_idx").on(t.portalUserId),
    kycStatusIdx:  index("clients_kyc_status_idx").on(t.kycStatus),
    tierIdx:       index("clients_tier_idx").on(t.tier),
  })
);

// ── Table: invoices ────────────────────────────────────────────
// One invoice per billing cycle; auto-generated on KYC approval

export const invoices = pgTable(
  "invoices",
  {
    id:              serial("id").primaryKey(),
    clientId:        integer("client_id").notNull().references(() => clients.id),

    invoiceNumber:   varchar("invoice_number", { length: 30 }).notNull().unique(),
    // Format: INV-YYYYMM-XXXXX  e.g. INV-202506-00042

    // ── Amounts ───────────────────────────────────────────────
    packageName:     text("package_name").notNull(),
    monthlyFee:      integer("monthly_fee").notNull(),    // IDR
    setupFee:        integer("setup_fee").notNull().default(0),
    discountAmount:  integer("discount_amount").notNull().default(0),
    totalAmount:     integer("total_amount").notNull(),   // IDR

    // ── Status & Dates ────────────────────────────────────────
    status:          invoiceStatusEnum("status").notNull().default("DRAFT"),
    issuedAt:        timestamp("issued_at").notNull().defaultNow(),
    dueDate:         timestamp("due_date").notNull(),
    paidAt:          timestamp("paid_at"),
    periodStart:     timestamp("period_start").notNull(),
    periodEnd:       timestamp("period_end").notNull(),

    // ── Payment Details ───────────────────────────────────────
    paymentMethod:   text("payment_method"),        // "bank_transfer", "qris"
    paymentProofUrl: text("payment_proof_url"),
    confirmedBy:     integer("confirmed_by"),       // Admin who confirmed

    // ── Bilingual Invoice Data ─────────────────────────────────
    lang:            varchar("lang", { length: 5 }).notNull().default("id"),
    // "id" = Bahasa Indonesia, "en" = English
    notes:           text("notes"),

    createdAt:       timestamp("created_at").notNull().defaultNow(),
    updatedAt:       timestamp("updated_at").notNull().defaultNow(),
  },
  (t) => ({
    clientIdx:       index("invoices_client_id_idx").on(t.clientId),
    statusIdx:       index("invoices_status_idx").on(t.status),
  })
);

// ── Table: fraud_alerts ────────────────────────────────────────
// Fraud detection events (R1–R6 + visual rules)

export const fraudAlerts = pgTable(
  "fraud_alerts",
  {
    id:              serial("id").primaryKey(),
    clientId:        integer("client_id").notNull().references(() => clients.id),

    // ── Alert Identity ────────────────────────────────────────
    alertCode:       varchar("alert_code", { length: 20 }).notNull(),
    // "R1", "R2", "R3", "R4", "R5-VISUAL", "R6-VISUAL"
    ruleName:        text("rule_name").notNull(),
    severity:        fraudSeverityEnum("severity").notNull(),
    status:          fraudStatusEnum("status").notNull().default("NEW"),

    // ── Transaction Data ──────────────────────────────────────
    transactionId:   integer("transaction_id"),
    cashierId:       integer("cashier_id"),
    cashierName:     text("cashier_name"),
    transactionType: text("transaction_type"),      // "VOID", "DISKON", etc.
    amount:          integer("amount"),
    itemCount:       integer("item_count"),

    // ── Visual Evidence (R5/R6 — V-ULTRA tier) ────────────────
    cctvFrameId:     text("cctv_frame_id"),
    cctvThumbnailUrl: text("cctv_thumbnail_url"),   // Frame screenshot URL
    cctvCapturedAt:  timestamp("cctv_captured_at"),
    visualItemCount: integer("visual_item_count"),  // Items detected by CV
    confidenceScore: real("confidence_score"),      // 0.0–1.0

    // ── Anomaly Details ───────────────────────────────────────
    anomalyScore:    integer("anomaly_score").notNull().default(0),
    // 0–100 composite risk score
    triggeredRules:  jsonb("triggered_rules").$type<string[]>().default([]),
    details:         jsonb("details").$type<Record<string, unknown>>().default({}),

    // ── Review ────────────────────────────────────────────────
    reviewedBy:      integer("reviewed_by"),
    reviewedAt:      timestamp("reviewed_at"),
    reviewNote:      text("review_note"),

    occurredAt:      timestamp("occurred_at").notNull(),
    createdAt:       timestamp("created_at").notNull().defaultNow(),
  },
  (t) => ({
    clientIdx:       index("fraud_alerts_client_id_idx").on(t.clientId),
    statusIdx:       index("fraud_alerts_status_idx").on(t.status),
    severityIdx:     index("fraud_alerts_severity_idx").on(t.severity),
    occurredAtIdx:   index("fraud_alerts_occurred_at_idx").on(t.occurredAt),
  })
);

// ── Table: bridge_events ───────────────────────────────────────
// CCTV-POS Bridge correlation records (V-ULTRA)

export const bridgeEvents = pgTable(
  "bridge_events",
  {
    id:              text("id").primaryKey(),
    // Format: "bridge-{timestamp}-{random}"

    clientId:        integer("client_id").notNull().references(() => clients.id),
    transactionId:   integer("transaction_id").notNull(),
    frameId:         text("frame_id"),

    // ── Scores & Rules ────────────────────────────────────────
    anomalyScore:    integer("anomaly_score").notNull().default(0),
    triggeredRules:  jsonb("triggered_rules").$type<string[]>().default([]),
    itemCountMismatch: boolean("item_count_mismatch").notNull().default(false),
    status:          bridgeStatusEnum("status").notNull().default("PENDING_REVIEW"),

    // ── Snapshot Data (denormalized for quick display) ─────────
    posSnapshot:     jsonb("pos_snapshot").$type<Record<string, unknown>>(),
    cctvSnapshot:    jsonb("cctv_snapshot").$type<Record<string, unknown>>(),

    timestamp:       timestamp("timestamp").notNull().defaultNow(),
  },
  (t) => ({
    clientIdx:       index("bridge_events_client_id_idx").on(t.clientId),
    statusIdx:       index("bridge_events_status_idx").on(t.status),
  })
);

// ── Table: agent_configs ───────────────────────────────────────
// Per-client AI Agent configuration & enable/disable

export const agentConfigs = pgTable(
  "agent_configs",
  {
    id:              serial("id").primaryKey(),
    clientId:        integer("client_id").notNull().references(() => clients.id),

    agentId:         varchar("agent_id", { length: 30 }).notNull(),
    // "visionary", "sentinel", "revenue", "legal", "social",
    // "logistic", "hunter", "recruiter", "support", "security"

    isEnabled:       boolean("is_enabled").notNull().default(false),
    config:          jsonb("config").$type<Record<string, unknown>>().default({}),
    // Agent-specific configuration overrides
    lastRunAt:       timestamp("last_run_at"),
    updatedAt:       timestamp("updated_at").notNull().defaultNow(),
  },
  (t) => ({
    clientAgentUniqueIdx: uniqueIndex("agent_configs_client_agent_idx")
      .on(t.clientId, t.agentId),
  })
);

// ── Table: audit_logs ─────────────────────────────────────────
// Immutable audit trail for admin actions

export const auditLogs = pgTable(
  "audit_logs",
  {
    id:              serial("id").primaryKey(),
    actorId:         integer("actor_id"),           // Admin or null (system)
    actorType:       text("actor_type"),            // "admin", "system", "client"
    clientId:        integer("client_id"),           // Affected client (nullable)

    action:          text("action").notNull(),
    // e.g. "KYC_APPROVED", "INVOICE_SENT", "CREDENTIALS_ASSIGNED"
    entityType:      text("entity_type"),           // "client", "invoice", etc.
    entityId:        text("entity_id"),
    before:          jsonb("before").$type<Record<string, unknown>>(),
    after:           jsonb("after").$type<Record<string, unknown>>(),
    ipAddress:       text("ip_address"),
    userAgent:       text("user_agent"),

    createdAt:       timestamp("created_at").notNull().defaultNow(),
  },
  (t) => ({
    actorIdx:        index("audit_logs_actor_idx").on(t.actorId),
    clientIdx:       index("audit_logs_client_idx").on(t.clientId),
    actionIdx:       index("audit_logs_action_idx").on(t.action),
    createdAtIdx:    index("audit_logs_created_at_idx").on(t.createdAt),
  })
);

// ── Relations ─────────────────────────────────────────────────

export const clientsRelations = relations(clients, ({ many }) => ({
  invoices:      many(invoices),
  fraudAlerts:   many(fraudAlerts),
  bridgeEvents:  many(bridgeEvents),
  agentConfigs:  many(agentConfigs),
  auditLogs:     many(auditLogs),
}));

export const invoicesRelations = relations(invoices, ({ one }) => ({
  client: one(clients, {
    fields:     [invoices.clientId],
    references: [clients.id],
  }),
}));

export const fraudAlertsRelations = relations(fraudAlerts, ({ one }) => ({
  client: one(clients, {
    fields:     [fraudAlerts.clientId],
    references: [clients.id],
  }),
}));

// ── Type Exports (inferred from schema) ───────────────────────

export type Client         = typeof clients.$inferSelect;
export type NewClient      = typeof clients.$inferInsert;
export type Invoice        = typeof invoices.$inferSelect;
export type NewInvoice     = typeof invoices.$inferInsert;
export type FraudAlert     = typeof fraudAlerts.$inferSelect;
export type NewFraudAlert  = typeof fraudAlerts.$inferInsert;
export type BridgeEvent    = typeof bridgeEvents.$inferSelect;
export type AgentConfig    = typeof agentConfigs.$inferSelect;
export type AuditLog       = typeof auditLogs.$inferSelect;
