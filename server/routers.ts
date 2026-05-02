import { z } from "zod";
import { TRPCError } from "@trpc/server";
import { publicProcedure, protectedProcedure, adminProcedure, router } from "./_core/trpc";
import { systemRouter } from "./_core/systemRouter";
import * as db from "./db";
import * as fraud from "./fraud";
import { AGENTS, TIERS, hasFeatureAccess, isAgentUnlocked, generateInvoiceNumber, generateReferralLink, REFERRAL_CONFIG } from "../shared/constants";
import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import bcrypt from "bcrypt";
import crypto from "crypto";

/**
 * ============================================================
 * AUTHENTICATION ROUTER
 * ============================================================
 */
const authRouter = router({
  me: publicProcedure.query(({ ctx }) => ctx.user),

  logout: publicProcedure.mutation(({ ctx }) => {
    const cookieOptions = getSessionCookieOptions(ctx.req);
    ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
    return { success: true } as const;
  }),

  loginClient: publicProcedure
    .input(
      z.object({
        clientId: z.string().min(1),
        password: z.string().min(1),
      })
    )
    .mutation(async ({ input, ctx }) => {
      const client = await db.getClientByClientId(input.clientId);

      if (!client) {
        throw new TRPCError({
          code: "UNAUTHORIZED",
          message: "Client ID atau password salah",
        });
      }

      const passwordMatch = await bcrypt.compare(
        input.password,
        client.passwordHash
      );

      if (!passwordMatch) {
        throw new TRPCError({
          code: "UNAUTHORIZED",
          message: "Client ID atau password salah",
        });
      }

      if (client.status !== "aktif" && client.tier !== "DEMO") {
        throw new TRPCError({
          code: "FORBIDDEN",
          message: "Akun Anda tidak aktif. Hubungi support.",
        });
      }

      // Create session
      const token = crypto.randomBytes(32).toString("hex");
      const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days

      await db.createSession({
        clientId: client.id,
        token,
        expiresAt,
        ipAddress: ctx.req.ip,
        userAgent: ctx.req.get("user-agent"),
      });

      // Log audit
      await db.logAuditEvent({
        clientId: client.id,
        action: "login",
        ipAddress: ctx.req.ip,
      });

      return {
        clientId: client.clientId,
        name: client.name,
        tier: client.tier,
        token,
      };
    }),
});

/**
 * ============================================================
 * CLIENT DASHBOARD ROUTER
 * ============================================================
 */
const clientDashRouter = router({
  getDashboard: protectedProcedure.query(async ({ ctx }) => {
    // This is a placeholder - would need to be extended for client-specific data
    return {
      totalOmset: 0,
      transactionCount: 0,
      anomalyCount: 0,
      cashierCount: 0,
      systemStatus: "online",
    };
  }),

  getTransactions: protectedProcedure
    .input(
      z.object({
        limit: z.number().min(1).max(100).default(20),
        offset: z.number().min(0).default(0),
      })
    )
    .query(async ({ input }) => {
      // Placeholder implementation
      return {
        transactions: [],
        total: 0,
      };
    }),

  getAlerts: protectedProcedure
    .input(z.object({ limit: z.number().min(1).max(50).default(20) }))
    .query(async ({ input }) => {
      // Placeholder implementation
      return [];
    }),

  getCashiers: protectedProcedure.query(async () => {
    // Placeholder implementation
    return [];
  }),
});

/**
 * ============================================================
 * FRAUD DETECTION ROUTER
 * ============================================================
 */
const fraudRouter = router({
  scanTransactions: protectedProcedure
    .input(
      z.object({
        transactions: z.array(z.any()),
      })
    )
    .mutation(async ({ input }) => {
      // Placeholder for fraud scanning
      return {
        results: [],
        stats: {},
      };
    }),

  getAnomalies: protectedProcedure.query(async () => {
    // Placeholder
    return [];
  }),

  getRuleStats: protectedProcedure.query(async () => {
    // Placeholder
    return {};
  }),
});

/**
 * ============================================================
 * AGENTS ROUTER
 * ============================================================
 */
const agentsRouter = router({
  list: publicProcedure.query(() => {
    return AGENTS.map((agent) => ({
      ...agent,
      minTier: agent.minTier,
    }));
  }),

  getStatus: publicProcedure
    .input(z.object({ agentId: z.number() }))
    .query(async ({ input }) => {
      return {
        agentId: input.agentId,
        status: "online",
        lastActivity: new Date(),
      };
    }),

  invoke: protectedProcedure
    .input(
      z.object({
        agentId: z.number(),
        params: z.record(z.any()).optional(),
      })
    )
    .mutation(async ({ input }) => {
      return {
        success: true,
        result: {},
      };
    }),
});

/**
 * ============================================================
 * REFERRAL ROUTER
 * ============================================================
 */
const referralRouter = router({
  generateLink: protectedProcedure.mutation(async ({ ctx }) => {
    // Placeholder - would need client context
    return {
      link: "",
      qrCode: "",
    };
  }),

  getCommissions: protectedProcedure.query(async () => {
    return {
      totalCommission: 0,
      activePartners: 0,
      commissionRate: REFERRAL_CONFIG.COMMISSION_RATE,
      history: [],
    };
  }),

  getPartners: protectedProcedure.query(async () => {
    return [];
  }),
});

/**
 * ============================================================
 * INVESTOR ROUTER
 * ============================================================
 */
const investorRouter = router({
  getMRR: adminProcedure.query(async () => {
    const mrr = await db.getCurrentMRR();
    return { mrr };
  }),

  getROI: adminProcedure.query(async () => {
    return { roi: 0, trend: [] };
  }),

  getReturns: adminProcedure.query(async () => {
    const returns = await db.getInvestorReturns();
    return returns;
  }),
});

/**
 * ============================================================
 * ADMIN ROUTER
 * ============================================================
 */
const adminRouter = router({
  listClients: adminProcedure.query(async () => {
    return await db.listClients();
  }),

  approveClient: adminProcedure
    .input(z.object({ clientId: z.number() }))
    .mutation(async ({ input }) => {
      await db.updateClientTier(input.clientId, "V-LITE");
      return { success: true };
    }),

  generatePaymentLink: adminProcedure
    .input(
      z.object({
        clientId: z.number(),
        tier: z.string(),
      })
    )
    .mutation(async ({ input }) => {
      const invoiceNumber = generateInvoiceNumber();
      const tier = TIERS[input.tier as keyof typeof TIERS];

      const invoice = await db.createInvoice({
        clientId: input.clientId,
        invoiceNumber,
        tier: input.tier,
        type: "SETUP",
        amount: tier.setupFee + tier.monthlyPrice,
        monthlyPrice: tier.monthlyPrice,
        setupFee: tier.setupFee,
        dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
      });

      return {
        invoiceNumber,
        amount: tier.setupFee + tier.monthlyPrice,
        invoice,
      };
    }),
});

/**
 * ============================================================
 * MAIN APP ROUTER
 * ============================================================
 */
export const appRouter = router({
  system: systemRouter,
  auth: authRouter,
  clientDash: clientDashRouter,
  fraud: fraudRouter,
  agents: agentsRouter,
  referral: referralRouter,
  investor: investorRouter,
  admin: adminRouter,
});

export type AppRouter = typeof appRouter;
