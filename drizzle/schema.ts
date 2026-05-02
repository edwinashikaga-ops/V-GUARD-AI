import { 
  int, 
  mysqlEnum, 
  mysqlTable, 
  text, 
  timestamp, 
  varchar,
  decimal,
  boolean,
  datetime,
  json,
  index,
  foreignKey,
  unique,
} from "drizzle-orm/mysql-core";

/**
 * ============================================================
 * USERS & AUTHENTICATION
 * ============================================================
 */

export const users = mysqlTable("users", {
  id: int("id").autoincrement().primaryKey(),
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

/**
 * ============================================================
 * CLIENTS & BUSINESS DATA
 * ============================================================
 */

export const clients = mysqlTable(
  "clients",
  {
    id: int("id").autoincrement().primaryKey(),
    clientId: varchar("clientId", { length: 64 }).notNull().unique(), // VG-XXXXX format
    name: varchar("name", { length: 255 }).notNull(),
    businessName: varchar("businessName", { length: 255 }).notNull(),
    email: varchar("email", { length: 320 }).notNull(),
    phone: varchar("phone", { length: 20 }).notNull(),
    tier: mysqlEnum("tier", [
      "DEMO",
      "V-LITE",
      "V-PRO",
      "V-ADVANCE",
      "V-ELITE",
      "V-ULTRA",
    ])
      .default("DEMO")
      .notNull(),
    status: mysqlEnum("status", ["pending", "aktif", "suspended", "cancelled"])
      .default("pending")
      .notNull(),
    passwordHash: varchar("passwordHash", { length: 255 }).notNull(),
    ktpUrl: text("ktpUrl"), // KTP document URL
    monthlyPrice: int("monthlyPrice").default(0), // Harga bulanan dalam Rupiah
    setupFee: int("setupFee").default(0), // Biaya setup
    commissionRate: decimal("commissionRate", { precision: 5, scale: 2 }).default("0.00"), // Referral commission %
    referrerId: int("referrerId"), // Client yang mereferensikan
    demoStartTime: datetime("demoStartTime"), // Waktu mulai demo (untuk DEMO tier)
    demoEndTime: datetime("demoEndTime"), // Waktu akhir demo
    activatedAt: timestamp("activatedAt"), // Waktu aktivasi
    createdAt: timestamp("createdAt").defaultNow().notNull(),
    updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  },
  (table) => ({
    clientIdIdx: index("clientId_idx").on(table.clientId),
    tierIdx: index("tier_idx").on(table.tier),
    statusIdx: index("status_idx").on(table.status),
    referrerIdFk: foreignKey({
      columns: [table.referrerId],
      foreignColumns: [table.id],
    }),
  })
);

export type Client = typeof clients.$inferSelect;
export type InsertClient = typeof clients.$inferInsert;

/**
 * ============================================================
 * SESSIONS (Client ID Login)
 * ============================================================
 */

export const sessions = mysqlTable(
  "sessions",
  {
    id: int("id").autoincrement().primaryKey(),
    clientId: int("clientId").notNull(),
    token: varchar("token", { length: 255 }).notNull().unique(),
    ipAddress: varchar("ipAddress", { length: 45 }),
    userAgent: text("userAgent"),
    expiresAt: timestamp("expiresAt").notNull(),
    createdAt: timestamp("createdAt").defaultNow().notNull(),
  },
  (table) => ({
    clientIdIdx: index("clientId_idx").on(table.clientId),
    tokenIdx: index("token_idx").on(table.token),
    expiresAtIdx: index("expiresAt_idx").on(table.expiresAt),
    clientIdFk: foreignKey({
      columns: [table.clientId],
      foreignColumns: [clients.id],
    }),
  })
);

export type Session = typeof sessions.$inferSelect;
export type InsertSession = typeof sessions.$inferInsert;

/**
 * ============================================================
 * TRANSACTIONS & FRAUD DETECTION
 * ============================================================
 */

export const transactions = mysqlTable(
  "transactions",
  {
    id: int("id").autoincrement().primaryKey(),
    clientId: int("clientId").notNull(),
    cashierId: int("cashierId"),
    transactionId: varchar("transactionId", { length: 64 }).notNull(), // TRX-001, TRX-002, etc
    branch: varchar("branch", { length: 255 }),
    cashierName: varchar("cashierName", { length: 255 }),
    amount: int("amount").notNull(), // Jumlah dalam Rupiah
    type: mysqlEnum("type", ["PENJUALAN", "VOID", "DISKON", "REFUND"]).notNull(),
    status: mysqlEnum("status", ["NORMAL", "ANOMALI"]).default("NORMAL").notNull(),
    physicalBalance: int("physicalBalance"), // Saldo fisik
    systemBalance: int("systemBalance"), // Saldo sistem
    balanceDifference: int("balanceDifference"), // Selisih saldo
    fraudFlags: json("fraudFlags").$type<string[]>().default([]), // Array of fraud rule IDs (R1, R2, etc)
    fraudConfidence: decimal("fraudConfidence", { precision: 5, scale: 2 }).default("0.00"), // 0-100%
    timestamp: datetime("timestamp").notNull(),
    createdAt: timestamp("createdAt").defaultNow().notNull(),
  },
  (table) => ({
    clientIdIdx: index("clientId_idx").on(table.clientId),
    cashierIdIdx: index("cashierId_idx").on(table.cashierId),
    statusIdx: index("status_idx").on(table.status),
    timestampIdx: index("timestamp_idx").on(table.timestamp),
    clientIdFk: foreignKey({
      columns: [table.clientId],
      foreignColumns: [clients.id],
    }),
    cashierIdFk: foreignKey({
      columns: [table.cashierId],
      foreignColumns: [cashiers.id],
    }),
  })
);

export type Transaction = typeof transactions.$inferSelect;
export type InsertTransaction = typeof transactions.$inferInsert;

/**
 * ============================================================
 * CASHIERS & RISK SCORING
 * ============================================================
 */

export const cashiers = mysqlTable(
  "cashiers",
  {
    id: int("id").autoincrement().primaryKey(),
    clientId: int("clientId").notNull(),
    name: varchar("name", { length: 255 }).notNull(),
    email: varchar("email", { length: 320 }),
    phone: varchar("phone", { length: 20 }),
    riskScore: decimal("riskScore", { precision: 5, scale: 2 }).default("0.00"), // 0-100
    riskLevel: mysqlEnum("riskLevel", ["LOW", "MEDIUM", "HIGH"]).default("LOW").notNull(),
    voidCount: int("voidCount").default(0),
    voidRate: decimal("voidRate", { precision: 5, scale: 2 }).default("0.00"), // 0-100%
    totalTransactions: int("totalTransactions").default(0),
    anomalyCount: int("anomalyCount").default(0),
    lastActivityAt: timestamp("lastActivityAt"),
    createdAt: timestamp("createdAt").defaultNow().notNull(),
    updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  },
  (table) => ({
    clientIdIdx: index("clientId_idx").on(table.clientId),
    riskLevelIdx: index("riskLevel_idx").on(table.riskLevel),
    clientIdFk: foreignKey({
      columns: [table.clientId],
      foreignColumns: [clients.id],
    }),
  })
);

export type Cashier = typeof cashiers.$inferSelect;
export type InsertCashier = typeof cashiers.$inferInsert;

/**
 * ============================================================
 * FRAUD ALERTS
 * ============================================================
 */

export const alerts = mysqlTable(
  "alerts",
  {
    id: int("id").autoincrement().primaryKey(),
    clientId: int("clientId").notNull(),
    transactionId: int("transactionId"),
    cashierId: int("cashierId"),
    ruleId: varchar("ruleId", { length: 10 }).notNull(), // R1, R2, R3, R4, R5, R6
    ruleName: varchar("ruleName", { length: 255 }).notNull(),
    severity: mysqlEnum("severity", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
      .default("MEDIUM")
      .notNull(),
    description: text("description"),
    amount: int("amount"),
    confidence: decimal("confidence", { precision: 5, scale: 2 }).default("0.00"), // 0-100%
    status: mysqlEnum("status", ["NEW", "ACKNOWLEDGED", "RESOLVED", "FALSE_POSITIVE"])
      .default("NEW")
      .notNull(),
    acknowledgedAt: timestamp("acknowledgedAt"),
    resolvedAt: timestamp("resolvedAt"),
    notes: text("notes"),
    createdAt: timestamp("createdAt").defaultNow().notNull(),
  },
  (table) => ({
    clientIdIdx: index("clientId_idx").on(table.clientId),
    ruleIdIdx: index("ruleId_idx").on(table.ruleId),
    statusIdx: index("status_idx").on(table.status),
    createdAtIdx: index("createdAt_idx").on(table.createdAt),
    clientIdFk: foreignKey({
      columns: [table.clientId],
      foreignColumns: [clients.id],
    }),
    transactionIdFk: foreignKey({
      columns: [table.transactionId],
      foreignColumns: [transactions.id],
    }),
    cashierIdFk: foreignKey({
      columns: [table.cashierId],
      foreignColumns: [cashiers.id],
    }),
  })
);

export type Alert = typeof alerts.$inferSelect;
export type InsertAlert = typeof alerts.$inferInsert;

/**
 * ============================================================
 * REFERRAL PROGRAM
 * ============================================================
 */

export const referrals = mysqlTable(
  "referrals",
  {
    id: int("id").autoincrement().primaryKey(),
    referrerId: int("referrerId").notNull(), // Client yang mereferensikan
    referredClientId: int("referredClientId").notNull(), // Client yang direferensikan
    referralLink: varchar("referralLink", { length: 255 }).notNull().unique(),
    status: mysqlEnum("status", ["PENDING", "ACTIVE", "INACTIVE"])
      .default("PENDING")
      .notNull(),
    commissionRate: decimal("commissionRate", { precision: 5, scale: 2 }).default("10.00"), // Default 10%
    commissionAmount: int("commissionAmount").default(0), // Komisi dalam Rupiah
    isPaid: boolean("isPaid").default(false),
    paidAt: timestamp("paidAt"),
    clickCount: int("clickCount").default(0),
    conversionDate: timestamp("conversionDate"), // Tanggal konversi ke client aktif
    createdAt: timestamp("createdAt").defaultNow().notNull(),
    updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  },
  (table) => ({
    referrerIdIdx: index("referrerId_idx").on(table.referrerId),
    referredClientIdIdx: index("referredClientId_idx").on(table.referredClientId),
    statusIdx: index("status_idx").on(table.status),
    referrerIdFk: foreignKey({
      columns: [table.referrerId],
      foreignColumns: [clients.id],
    }),
    referredClientIdFk: foreignKey({
      columns: [table.referredClientId],
      foreignColumns: [clients.id],
    }),
  })
);

export type Referral = typeof referrals.$inferSelect;
export type InsertReferral = typeof referrals.$inferInsert;

/**
 * ============================================================
 * INVOICES & PAYMENTS
 * ============================================================
 */

export const invoices = mysqlTable(
  "invoices",
  {
    id: int("id").autoincrement().primaryKey(),
    clientId: int("clientId").notNull(),
    invoiceNumber: varchar("invoiceNumber", { length: 64 }).notNull().unique(), // INV-2026-001
    tier: mysqlEnum("tier", [
      "V-LITE",
      "V-PRO",
      "V-ADVANCE",
      "V-ELITE",
      "V-ULTRA",
    ]).notNull(),
    type: mysqlEnum("type", ["MONTHLY", "SETUP", "UPGRADE"]).default("MONTHLY").notNull(),
    amount: int("amount").notNull(), // Total dalam Rupiah
    monthlyPrice: int("monthlyPrice").default(0),
    setupFee: int("setupFee").default(0),
    status: mysqlEnum("status", ["PENDING", "PAID", "OVERDUE", "CANCELLED"])
      .default("PENDING")
      .notNull(),
    paymentMethod: varchar("paymentMethod", { length: 64 }), // BCA, QRIS, etc
    paymentProof: text("paymentProof"), // URL to payment proof image
    dueDate: datetime("dueDate").notNull(),
    paidAt: timestamp("paidAt"),
    notes: text("notes"),
    whatsappLink: text("whatsappLink"), // WhatsApp payment link
    createdAt: timestamp("createdAt").defaultNow().notNull(),
    updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  },
  (table) => ({
    clientIdIdx: index("clientId_idx").on(table.clientId),
    invoiceNumberIdx: index("invoiceNumber_idx").on(table.invoiceNumber),
    statusIdx: index("status_idx").on(table.status),
    dueDateIdx: index("dueDate_idx").on(table.dueDate),
    clientIdFk: foreignKey({
      columns: [table.clientId],
      foreignColumns: [clients.id],
    }),
  })
);

export type Invoice = typeof invoices.$inferSelect;
export type InsertInvoice = typeof invoices.$inferInsert;

/**
 * ============================================================
 * INVESTOR RETURNS & PAYOUTS
 * ============================================================
 */

export const investorReturns = mysqlTable(
  "investor_returns",
  {
    id: int("id").autoincrement().primaryKey(),
    month: varchar("month", { length: 7 }).notNull(), // YYYY-MM format
    mrr: int("mrr").default(0), // Monthly Recurring Revenue
    totalRevenue: int("totalRevenue").default(0),
    expenses: int("expenses").default(0),
    netProfit: int("netProfit").default(0),
    roiPercentage: decimal("roiPercentage", { precision: 8, scale: 2 }).default("0.00"),
    yield: decimal("yield", { precision: 8, scale: 2 }).default("0.00"),
    payoutAmount: int("payoutAmount").default(0),
    isPaid: boolean("isPaid").default(false),
    paidAt: timestamp("paidAt"),
    notes: text("notes"),
    createdAt: timestamp("createdAt").defaultNow().notNull(),
  },
  (table) => ({
    monthIdx: index("month_idx").on(table.month),
    isPaidIdx: index("isPaid_idx").on(table.isPaid),
  })
);

export type InvestorReturn = typeof investorReturns.$inferSelect;
export type InsertInvestorReturn = typeof investorReturns.$inferInsert;

/**
 * ============================================================
 * AGENT STATUS & ACTIVITY
 * ============================================================
 */

export const agentActivity = mysqlTable(
  "agent_activity",
  {
    id: int("id").autoincrement().primaryKey(),
    clientId: int("clientId").notNull(),
    agentId: int("agentId").notNull(), // 1-10 for the 10 agents
    agentName: varchar("agentName", { length: 255 }).notNull(),
    status: mysqlEnum("status", ["online", "standby", "offline"])
      .default("online")
      .notNull(),
    lastActivityAt: timestamp("lastActivityAt"),
    totalInvocations: int("totalInvocations").default(0),
    successCount: int("successCount").default(0),
    errorCount: int("errorCount").default(0),
    averageResponseTime: int("averageResponseTime").default(0), // milliseconds
    createdAt: timestamp("createdAt").defaultNow().notNull(),
    updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  },
  (table) => ({
    clientIdIdx: index("clientId_idx").on(table.clientId),
    agentIdIdx: index("agentId_idx").on(table.agentId),
    statusIdx: index("status_idx").on(table.status),
    clientIdFk: foreignKey({
      columns: [table.clientId],
      foreignColumns: [clients.id],
    }),
  })
);

export type AgentActivity = typeof agentActivity.$inferSelect;
export type InsertAgentActivity = typeof agentActivity.$inferInsert;

/**
 * ============================================================
 * AUDIT LOGS
 * ============================================================
 */

export const auditLogs = mysqlTable(
  "audit_logs",
  {
    id: int("id").autoincrement().primaryKey(),
    userId: int("userId"),
    clientId: int("clientId"),
    action: varchar("action", { length: 255 }).notNull(), // login, logout, tier_upgrade, etc
    resource: varchar("resource", { length: 255 }), // users, clients, transactions, etc
    resourceId: int("resourceId"),
    details: json("details").$type<Record<string, unknown>>(), // Additional context
    ipAddress: varchar("ipAddress", { length: 45 }),
    userAgent: text("userAgent"),
    createdAt: timestamp("createdAt").defaultNow().notNull(),
  },
  (table) => ({
    userIdIdx: index("userId_idx").on(table.userId),
    clientIdIdx: index("clientId_idx").on(table.clientId),
    actionIdx: index("action_idx").on(table.action),
    createdAtIdx: index("createdAt_idx").on(table.createdAt),
    userIdFk: foreignKey({
      columns: [table.userId],
      foreignColumns: [users.id],
    }),
    clientIdFk: foreignKey({
      columns: [table.clientId],
      foreignColumns: [clients.id],
    }),
  })
);

export type AuditLog = typeof auditLogs.$inferSelect;
export type InsertAuditLog = typeof auditLogs.$inferInsert;
