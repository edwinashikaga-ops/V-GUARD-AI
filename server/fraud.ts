/**
 * ============================================================
 * FRAUD DETECTION ENGINE - V-Guard AI v1.0.0
 * ============================================================
 * 
 * Implements fraud detection rules R1-R6 per SOP v5.0
 * Each rule has a severity level and confidence score
 */

import { Transaction } from "../drizzle/schema";

/**
 * Fraud Rule Definitions
 */
export const FRAUD_RULES = {
  R1: {
    id: "R1",
    name: "VOID Direct Flag",
    description: "Any transaction marked as VOID",
    severity: "HIGH",
    minTier: "V-LITE",
    color: "#FF3B5C",
  },
  R2: {
    id: "R2",
    name: "VOID Rate Spike",
    description: "VOID percentage exceeds 20% per cashier",
    severity: "HIGH",
    minTier: "V-LITE",
    color: "#FF3B5C",
  },
  R3: {
    id: "R3",
    name: "Duplicate Transaction",
    description: "Same cashier + amount within 5 minutes",
    severity: "MEDIUM",
    minTier: "V-LITE",
    color: "#FFAB00",
  },
  R4: {
    id: "R4",
    name: "Balance Mismatch",
    description: "Physical balance ≠ system balance",
    severity: "MEDIUM",
    minTier: "V-PRO",
    color: "#FFAB00",
  },
  R5: {
    id: "R5",
    name: "Off-Hours Transaction",
    description: "Transaction outside business hours (< 07:00 or ≥ 23:00 WIB)",
    severity: "LOW",
    minTier: "V-PRO",
    color: "#7B2FFF",
  },
  R6: {
    id: "R6",
    name: "Rapid VOID",
    description: "More than 2 VOIDs in 10 minutes",
    severity: "CRITICAL",
    minTier: "V-PRO",
    color: "#FF3B5C",
  },
};

export type FraudRule = keyof typeof FRAUD_RULES;

/**
 * Fraud Detection Result
 */
export interface FraudDetectionResult {
  transactionId: string;
  flaggedRules: string[]; // Array of rule IDs (R1, R2, etc)
  confidence: number; // 0-100
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  isAnomalous: boolean;
  details: Record<string, unknown>;
}

/**
 * ============================================================
 * RULE IMPLEMENTATIONS
 * ============================================================
 */

/**
 * R1: VOID Direct Flag
 * Any transaction marked as VOID is immediately flagged
 */
export function checkR1_VoidDirectFlag(
  transaction: Transaction
): { triggered: boolean; confidence: number } {
  const triggered = transaction.type === "VOID";
  return {
    triggered,
    confidence: triggered ? 100 : 0,
  };
}

/**
 * R2: VOID Rate Spike
 * If VOID percentage exceeds 20% for a cashier, flag all recent transactions
 */
export function checkR2_VoidRateSpike(
  cashierVoidRate: number
): { triggered: boolean; confidence: number } {
  const triggered = cashierVoidRate > 20;
  const confidence = Math.min(100, (cashierVoidRate / 100) * 100);
  return {
    triggered,
    confidence,
  };
}

/**
 * R3: Duplicate Transaction
 * Same cashier + same amount within 5 minutes
 */
export function checkR3_DuplicateTransaction(
  currentTx: Transaction,
  recentTransactions: Transaction[],
  timeWindowMinutes: number = 5
): { triggered: boolean; confidence: number } {
  const timeWindowMs = timeWindowMinutes * 60 * 1000;
  const currentTime = new Date(currentTx.timestamp).getTime();

  const duplicates = recentTransactions.filter((tx) => {
    if (tx.id === currentTx.id) return false; // Skip self
    if (tx.cashierId !== currentTx.cashierId) return false; // Different cashier
    if (tx.amount !== currentTx.amount) return false; // Different amount

    const txTime = new Date(tx.timestamp).getTime();
    const timeDiff = Math.abs(currentTime - txTime);

    return timeDiff <= timeWindowMs;
  });

  const triggered = duplicates.length > 0;
  const confidence = triggered ? 85 : 0;

  return {
    triggered,
    confidence,
  };
}

/**
 * R4: Balance Mismatch
 * Physical balance does not match system balance
 */
export function checkR4_BalanceMismatch(
  transaction: Transaction
): { triggered: boolean; confidence: number } {
  if (
    transaction.physicalBalance === null ||
    transaction.systemBalance === null
  ) {
    return { triggered: false, confidence: 0 };
  }

  const mismatch =
    transaction.physicalBalance !== transaction.systemBalance;
  const difference = Math.abs(
    transaction.systemBalance - transaction.physicalBalance
  );

  // Confidence increases with larger mismatch (max 100 at 1M Rp difference)
  const confidence = Math.min(100, (difference / 1000000) * 100);

  return {
    triggered: mismatch,
    confidence: mismatch ? confidence : 0,
  };
}

/**
 * R5: Off-Hours Transaction
 * Transaction outside business hours (< 07:00 or >= 23:00 WIB)
 */
export function checkR5_OffHoursTransaction(
  transaction: Transaction
): { triggered: boolean; confidence: number } {
  const txDate = new Date(transaction.timestamp);
  const hour = txDate.getHours();

  const isOffHours = hour < 7 || hour >= 23;
  const confidence = isOffHours ? 70 : 0;

  return {
    triggered: isOffHours,
    confidence,
  };
}

/**
 * R6: Rapid VOID
 * More than 2 VOIDs in 10 minutes
 */
export function checkR6_RapidVoid(
  currentTx: Transaction,
  recentTransactions: Transaction[],
  timeWindowMinutes: number = 10,
  voidThreshold: number = 2
): { triggered: boolean; confidence: number } {
  if (currentTx.type !== "VOID") {
    return { triggered: false, confidence: 0 };
  }

  const timeWindowMs = timeWindowMinutes * 60 * 1000;
  const currentTime = new Date(currentTx.timestamp).getTime();

  const recentVoids = recentTransactions.filter((tx) => {
    if (tx.type !== "VOID") return false;
    if (tx.cashierId !== currentTx.cashierId) return false;

    const txTime = new Date(tx.timestamp).getTime();
    const timeDiff = Math.abs(currentTime - txTime);

    return timeDiff <= timeWindowMs;
  });

  // Include current transaction in count
  const voidCount = recentVoids.length + 1;
  const triggered = voidCount > voidThreshold;
  const confidence = triggered ? Math.min(100, (voidCount / 5) * 100) : 0;

  return {
    triggered,
    confidence,
  };
}

/**
 * ============================================================
 * MAIN FRAUD DETECTION FUNCTION
 * ============================================================
 */

export function scanTransactionForFraud(
  transaction: Transaction,
  recentTransactions: Transaction[],
  cashierVoidRate: number,
  enabledRules: FraudRule[] = ["R1", "R2", "R3", "R4", "R5", "R6"]
): FraudDetectionResult {
  const flaggedRules: string[] = [];
  const ruleScores: Record<string, number> = {};

  // R1: VOID Direct Flag
  if (enabledRules.includes("R1")) {
    const result = checkR1_VoidDirectFlag(transaction);
    if (result.triggered) {
      flaggedRules.push("R1");
      ruleScores["R1"] = result.confidence;
    }
  }

  // R2: VOID Rate Spike
  if (enabledRules.includes("R2")) {
    const result = checkR2_VoidRateSpike(cashierVoidRate);
    if (result.triggered) {
      flaggedRules.push("R2");
      ruleScores["R2"] = result.confidence;
    }
  }

  // R3: Duplicate Transaction
  if (enabledRules.includes("R3")) {
    const result = checkR3_DuplicateTransaction(
      transaction,
      recentTransactions
    );
    if (result.triggered) {
      flaggedRules.push("R3");
      ruleScores["R3"] = result.confidence;
    }
  }

  // R4: Balance Mismatch
  if (enabledRules.includes("R4")) {
    const result = checkR4_BalanceMismatch(transaction);
    if (result.triggered) {
      flaggedRules.push("R4");
      ruleScores["R4"] = result.confidence;
    }
  }

  // R5: Off-Hours Transaction
  if (enabledRules.includes("R5")) {
    const result = checkR5_OffHoursTransaction(transaction);
    if (result.triggered) {
      flaggedRules.push("R5");
      ruleScores["R5"] = result.confidence;
    }
  }

  // R6: Rapid VOID
  if (enabledRules.includes("R6")) {
    const result = checkR6_RapidVoid(transaction, recentTransactions);
    if (result.triggered) {
      flaggedRules.push("R6");
      ruleScores["R6"] = result.confidence;
    }
  }

  // Calculate overall confidence (average of all triggered rules)
  const overallConfidence =
    flaggedRules.length > 0
      ? Object.values(ruleScores).reduce((a, b) => a + b, 0) /
        flaggedRules.length
      : 0;

  // Determine severity
  let severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" = "LOW";
  if (flaggedRules.includes("R6") || flaggedRules.includes("R1")) {
    severity = "CRITICAL";
  } else if (
    flaggedRules.includes("R2") ||
    flaggedRules.includes("R4") ||
    flaggedRules.includes("R5")
  ) {
    severity = "HIGH";
  } else if (flaggedRules.includes("R3")) {
    severity = "MEDIUM";
  }

  return {
    transactionId: transaction.transactionId,
    flaggedRules,
    confidence: Math.round(overallConfidence),
    severity,
    isAnomalous: flaggedRules.length > 0 && overallConfidence >= 50,
    details: {
      ruleScores,
      cashierVoidRate,
      balanceDifference: transaction.balanceDifference,
      transactionType: transaction.type,
    },
  };
}

/**
 * Batch scan multiple transactions
 */
export function scanTransactionsBatch(
  transactions: Transaction[],
  cashierVoidRates: Record<number, number>,
  enabledRules?: FraudRule[]
): FraudDetectionResult[] {
  return transactions.map((tx) => {
    const recentTxs = transactions.filter(
      (t) =>
        t.cashierId === tx.cashierId &&
        t.id !== tx.id &&
        new Date(t.timestamp).getTime() >
          new Date(tx.timestamp).getTime() - 15 * 60 * 1000
    );

    const voidRate = cashierVoidRates[tx.cashierId || 0] || 0;

    return scanTransactionForFraud(tx, recentTxs, voidRate, enabledRules);
  });
}

/**
 * Get fraud statistics
 */
export function calculateFraudStats(results: FraudDetectionResult[]) {
  const stats = {
    totalScanned: results.length,
    totalAnomalous: results.filter((r) => r.isAnomalous).length,
    anomalyRate: 0,
    ruleHits: {} as Record<string, number>,
    severityBreakdown: {
      CRITICAL: 0,
      HIGH: 0,
      MEDIUM: 0,
      LOW: 0,
    },
    averageConfidence: 0,
  };

  // Calculate anomaly rate
  stats.anomalyRate =
    stats.totalScanned > 0
      ? (stats.totalAnomalous / stats.totalScanned) * 100
      : 0;

  // Count rule hits
  results.forEach((result) => {
    result.flaggedRules.forEach((rule) => {
      stats.ruleHits[rule] = (stats.ruleHits[rule] || 0) + 1;
    });

    stats.severityBreakdown[result.severity]++;
  });

  // Average confidence
  const anomalousResults = results.filter((r) => r.isAnomalous);
  stats.averageConfidence =
    anomalousResults.length > 0
      ? anomalousResults.reduce((sum, r) => sum + r.confidence, 0) /
        anomalousResults.length
      : 0;

  return stats;
}
