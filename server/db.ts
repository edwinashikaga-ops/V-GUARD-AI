import { eq, and, or, desc, gte, lte, like } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import {
  InsertUser,
  users,
  clients,
  sessions,
  transactions,
  cashiers,
  alerts,
  referrals,
  invoices,
  investorReturns,
  agentActivity,
  auditLogs,
  type Client,
  type Transaction,
  type Cashier,
  type Alert,
  type Referral,
  type Invoice,
} from "../drizzle/schema";
import { ENV } from "./_core/env";

let _db: ReturnType<typeof drizzle> | null = null;

export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

/**
 * ============================================================
 * USER MANAGEMENT
 * ============================================================
 */

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) {
    throw new Error("User openId is required for upsert");
  }

  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot upsert user: database not available");
    return;
  }

  try {
    const values: InsertUser = {
      openId: user.openId,
    };
    const updateSet: Record<string, unknown> = {};

    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];

    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };

    textFields.forEach(assignNullable);

    if (user.lastSignedIn !== undefined) {
      values.lastSignedIn = user.lastSignedIn;
      updateSet.lastSignedIn = user.lastSignedIn;
    }
    if (user.role !== undefined) {
      values.role = user.role;
      updateSet.role = user.role;
    } else if (user.openId === ENV.ownerOpenId) {
      values.role = "admin";
      updateSet.role = "admin";
    }

    if (!values.lastSignedIn) {
      values.lastSignedIn = new Date();
    }

    if (Object.keys(updateSet).length === 0) {
      updateSet.lastSignedIn = new Date();
    }

    await db.insert(users).values(values).onDuplicateKeyUpdate({
      set: updateSet,
    });
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) return undefined;

  const result = await db
    .select()
    .from(users)
    .where(eq(users.openId, openId))
    .limit(1);

  return result.length > 0 ? result[0] : undefined;
}

/**
 * ============================================================
 * CLIENT MANAGEMENT
 * ============================================================
 */

export async function createClient(data: {
  clientId: string;
  name: string;
  businessName: string;
  email: string;
  phone: string;
  passwordHash: string;
  tier?: string;
  referrerId?: number;
}): Promise<Client | undefined> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const [result] = await db.insert(clients).values({
    clientId: data.clientId,
    name: data.name,
    businessName: data.businessName,
    email: data.email,
    phone: data.phone,
    passwordHash: data.passwordHash,
    tier: (data.tier as any) || "DEMO",
    referrerId: data.referrerId,
  });

  return getClientById(result.insertId);
}

export async function getClientById(id: number): Promise<Client | undefined> {
  const db = await getDb();
  if (!db) return undefined;

  const result = await db
    .select()
    .from(clients)
    .where(eq(clients.id, id))
    .limit(1);

  return result[0];
}

export async function getClientByClientId(
  clientId: string
): Promise<Client | undefined> {
  const db = await getDb();
  if (!db) return undefined;

  const result = await db
    .select()
    .from(clients)
    .where(eq(clients.clientId, clientId))
    .limit(1);

  return result[0];
}

export async function updateClientTier(
  clientId: number,
  tier: string
): Promise<void> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  await db
    .update(clients)
    .set({ tier: tier as any, activatedAt: new Date() })
    .where(eq(clients.id, clientId));
}

export async function listClients(
  status?: string
): Promise<Client[]> {
  const db = await getDb();
  if (!db) return [];

  if (status) {
    return db
      .select()
      .from(clients)
      .where(eq(clients.status, status as any))
      .orderBy(desc(clients.createdAt));
  }

  return db
    .select()
    .from(clients)
    .orderBy(desc(clients.createdAt));
}

/**
 * ============================================================
 * SESSION MANAGEMENT
 * ============================================================
 */

export async function createSession(data: {
  clientId: number;
  token: string;
  expiresAt: Date;
  ipAddress?: string;
  userAgent?: string;
}): Promise<void> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  await db.insert(sessions).values({
    clientId: data.clientId,
    token: data.token,
    expiresAt: data.expiresAt,
    ipAddress: data.ipAddress,
    userAgent: data.userAgent,
  });
}

export async function getSessionByToken(token: string) {
  const db = await getDb();
  if (!db) return undefined;

  const result = await db
    .select()
    .from(sessions)
    .where(eq(sessions.token, token))
    .limit(1);

  return result[0];
}

/**
 * ============================================================
 * TRANSACTION MANAGEMENT
 * ============================================================
 */

export async function createTransaction(data: {
  clientId: number;
  cashierId?: number;
  transactionId: string;
  branch?: string;
  cashierName?: string;
  amount: number;
  type: string;
  physicalBalance?: number;
  systemBalance?: number;
  timestamp: Date;
  fraudFlags?: string[];
  fraudConfidence?: number;
}): Promise<Transaction | undefined> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const balanceDifference =
    data.systemBalance && data.physicalBalance
      ? data.systemBalance - data.physicalBalance
      : undefined;

  const [result] = await db.insert(transactions).values({
    clientId: data.clientId,
    cashierId: data.cashierId,
    transactionId: data.transactionId,
    branch: data.branch,
    cashierName: data.cashierName,
    amount: data.amount,
    type: data.type as any,
    physicalBalance: data.physicalBalance,
    systemBalance: data.systemBalance,
    balanceDifference,
    fraudFlags: data.fraudFlags || [],
    fraudConfidence: (data.fraudConfidence || 0) as any,
    timestamp: data.timestamp,
  });

  return getTransactionById(result.insertId);
}

export async function getTransactionById(id: number): Promise<Transaction | undefined> {
  const db = await getDb();
  if (!db) return undefined;

  const result = await db
    .select()
    .from(transactions)
    .where(eq(transactions.id, id))
    .limit(1);

  return result[0];
}

export async function getClientTransactions(
  clientId: number,
  limit: number = 50,
  offset: number = 0
): Promise<Transaction[]> {
  const db = await getDb();
  if (!db) return [];

  return db
    .select()
    .from(transactions)
    .where(eq(transactions.clientId, clientId))
    .orderBy(desc(transactions.timestamp))
    .limit(limit)
    .offset(offset);
}

/**
 * ============================================================
 * CASHIER MANAGEMENT
 * ============================================================
 */

export async function createCashier(data: {
  clientId: number;
  name: string;
  email?: string;
  phone?: string;
}): Promise<Cashier | undefined> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const [result] = await db.insert(cashiers).values({
    clientId: data.clientId,
    name: data.name,
    email: data.email,
    phone: data.phone,
  });

  return getCashierById(result.insertId);
}

export async function getCashierById(id: number): Promise<Cashier | undefined> {
  const db = await getDb();
  if (!db) return undefined;

  const result = await db
    .select()
    .from(cashiers)
    .where(eq(cashiers.id, id))
    .limit(1);

  return result[0];
}

export async function getClientCashiers(clientId: number): Promise<Cashier[]> {
  const db = await getDb();
  if (!db) return [];

  return db
    .select()
    .from(cashiers)
    .where(eq(cashiers.clientId, clientId))
    .orderBy(desc(cashiers.riskScore));
}

export async function updateCashierRiskScore(
  cashierId: number,
  riskScore: number,
  riskLevel: string
): Promise<void> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  await db
    .update(cashiers)
    .set({
      riskScore: riskScore as any,
      riskLevel: riskLevel as any,
      lastActivityAt: new Date(),
    })
    .where(eq(cashiers.id, cashierId));
}

/**
 * ============================================================
 * FRAUD ALERTS
 * ============================================================
 */

export async function createAlert(data: {
  clientId: number;
  transactionId?: number;
  cashierId?: number;
  ruleId: string;
  ruleName: string;
  severity: string;
  description?: string;
  amount?: number;
  confidence: number;
}): Promise<Alert | undefined> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const [result] = await db.insert(alerts).values({
    clientId: data.clientId,
    transactionId: data.transactionId,
    cashierId: data.cashierId,
    ruleId: data.ruleId,
    ruleName: data.ruleName,
    severity: data.severity as any,
    description: data.description,
    amount: data.amount,
    confidence: (data.confidence) as any,
  });

  return getAlertById(result.insertId);
}

export async function getAlertById(id: number): Promise<Alert | undefined> {
  const db = await getDb();
  if (!db) return undefined;

  const result = await db
    .select()
    .from(alerts)
    .where(eq(alerts.id, id))
    .limit(1);

  return result[0];
}

export async function getClientAlerts(
  clientId: number,
  limit: number = 20
): Promise<Alert[]> {
  const db = await getDb();
  if (!db) return [];

  return db
    .select()
    .from(alerts)
    .where(
      and(
        eq(alerts.clientId, clientId),
        eq(alerts.status, "NEW")
      )
    )
    .orderBy(desc(alerts.createdAt))
    .limit(limit);
}

/**
 * ============================================================
 * REFERRAL PROGRAM
 * ============================================================
 */

export async function createReferral(data: {
  referrerId: number;
  referredClientId: number;
  referralLink: string;
}): Promise<Referral | undefined> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const [result] = await db.insert(referrals).values({
    referrerId: data.referrerId,
    referredClientId: data.referredClientId,
    referralLink: data.referralLink,
  });

  return getReferralById(result.insertId);
}

export async function getReferralById(id: number): Promise<Referral | undefined> {
  const db = await getDb();
  if (!db) return undefined;

  const result = await db
    .select()
    .from(referrals)
    .where(eq(referrals.id, id))
    .limit(1);

  return result[0];
}

export async function getReferrerCommissions(referrerId: number) {
  const db = await getDb();
  if (!db) return { totalCommission: 0, activePartners: 0, referrals: [] };

  const referralList = await db
    .select()
    .from(referrals)
    .where(eq(referrals.referrerId, referrerId));

  const totalCommission = referralList.reduce(
    (sum, r) => sum + (r.commissionAmount || 0),
    0
  );
  const activePartners = referralList.filter(
    (r) => r.status === "ACTIVE"
  ).length;

  return { totalCommission, activePartners, referrals: referralList };
}

/**
 * ============================================================
 * INVOICES & PAYMENTS
 * ============================================================
 */

export async function createInvoice(data: {
  clientId: number;
  invoiceNumber: string;
  tier: string;
  type: string;
  amount: number;
  monthlyPrice?: number;
  setupFee?: number;
  dueDate: Date;
  whatsappLink?: string;
}): Promise<Invoice | undefined> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const [result] = await db.insert(invoices).values({
    clientId: data.clientId,
    invoiceNumber: data.invoiceNumber,
    tier: data.tier as any,
    type: data.type as any,
    amount: data.amount,
    monthlyPrice: data.monthlyPrice,
    setupFee: data.setupFee,
    dueDate: data.dueDate,
    whatsappLink: data.whatsappLink,
  });

  return getInvoiceById(result.insertId);
}

export async function getInvoiceById(id: number): Promise<Invoice | undefined> {
  const db = await getDb();
  if (!db) return undefined;

  const result = await db
    .select()
    .from(invoices)
    .where(eq(invoices.id, id))
    .limit(1);

  return result[0];
}

export async function getClientInvoices(clientId: number) {
  const db = await getDb();
  if (!db) return [];

  return db
    .select()
    .from(invoices)
    .where(eq(invoices.clientId, clientId))
    .orderBy(desc(invoices.createdAt));
}

/**
 * ============================================================
 * INVESTOR RETURNS
 * ============================================================
 */

export async function getInvestorReturns(
  limit: number = 12
) {
  const db = await getDb();
  if (!db) return [];

  return db
    .select()
    .from(investorReturns)
    .orderBy(desc(investorReturns.month))
    .limit(limit);
}

export async function getCurrentMRR(): Promise<number> {
  const db = await getDb();
  if (!db) return 0;

  const result = await db
    .select()
    .from(clients)
    .where(
      and(
        eq(clients.status, "aktif"),
        or(
          eq(clients.tier, "V-LITE"),
          eq(clients.tier, "V-PRO"),
          eq(clients.tier, "V-ADVANCE"),
          eq(clients.tier, "V-ELITE"),
          eq(clients.tier, "V-ULTRA")
        )
      )
    );

  const tierPrices: Record<string, number> = {
    "V-LITE": 150000,
    "V-PRO": 450000,
    "V-ADVANCE": 1200000,
    "V-ELITE": 3500000,
    "V-ULTRA": 0,
  };

  return result.reduce((sum, client) => {
    return sum + (tierPrices[client.tier] || 0);
  }, 0);
}

/**
 * ============================================================
 * AGENT ACTIVITY
 * ============================================================
 */

export async function updateAgentActivity(data: {
  clientId: number;
  agentId: number;
  agentName: string;
  status: string;
}): Promise<void> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const existing = await db
    .select()
    .from(agentActivity)
    .where(
      and(
        eq(agentActivity.clientId, data.clientId),
        eq(agentActivity.agentId, data.agentId)
      )
    )
    .limit(1);

  if (existing.length > 0) {
    await db
      .update(agentActivity)
      .set({
        status: data.status as any,
        lastActivityAt: new Date(),
      })
      .where(eq(agentActivity.id, existing[0].id));
  } else {
    await db.insert(agentActivity).values({
      clientId: data.clientId,
      agentId: data.agentId,
      agentName: data.agentName,
      status: data.status as any,
    });
  }
}

/**
 * ============================================================
 * AUDIT LOGS
 * ============================================================
 */

export async function logAuditEvent(data: {
  userId?: number;
  clientId?: number;
  action: string;
  resource?: string;
  resourceId?: number;
  details?: Record<string, unknown>;
  ipAddress?: string;
  userAgent?: string;
}): Promise<void> {
  const db = await getDb();
  if (!db) return;

  try {
    await db.insert(auditLogs).values({
      userId: data.userId,
      clientId: data.clientId,
      action: data.action,
      resource: data.resource,
      resourceId: data.resourceId,
      details: data.details,
      ipAddress: data.ipAddress,
      userAgent: data.userAgent,
    });
  } catch (error) {
    console.error("[Audit] Failed to log event:", error);
  }
}
