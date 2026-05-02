# V-Guard AI v1.0.0 — Master Project Structure

```
vguard-ai/
├── client/
│   └── src/
│       ├── App.tsx                          ← Router utama (6 rute)
│       ├── main.tsx
│       │
│       ├── pages/
│       │   ├── home/
│       │   │   └── index.tsx                ← Landing + Sentinel CS Chatbot
│       │   ├── produk/
│       │   │   └── index.tsx                ← Katalog V-LITE / V-PRO / V-ULTRA
│       │   ├── roi/
│       │   │   └── index.tsx                ← ROI Calculator
│       │   ├── register/
│       │   │   └── index.tsx                ← ✅ Onboarding Form (KYC)
│       │   ├── admin/
│       │   │   └── index.tsx                ← Founder Control Panel
│       │   ├── portal/
│       │   │   ├── index.tsx                ← ✅ Client Login Gate
│       │   │   ├── ClientDashboard.tsx      ← ✅ Dashboard + Fraud Alerts
│       │   │   ├── Transactions.tsx         ← POS Transaction Feed
│       │   │   ├── Agents.tsx               ← AI Agent Status Panel
│       │   │   ├── Referral.tsx             ← Referral Program
│       │   │   └── Investor.tsx             ← Investor Reports
│       │   └── NotFound.tsx
│       │
│       ├── components/
│       │   ├── ui/                          ← shadcn/ui base components
│       │   ├── TierGate.tsx                 ← ✅ Feature gating by tier
│       │   ├── LanguageSwitcher.tsx         ← ✅ ID / EN toggle
│       │   ├── ErrorBoundary.tsx
│       │   ├── FloatingChat.tsx             ← Sentinel CS Widget
│       │   │
│       │   └── admin/
│       │       └── agents/
│       │           ├── visionary/           ← 👁️ CCTV × POS Bridge
│       │           │   ├── index.tsx
│       │           │   ├── config.ts
│       │           │   └── types.ts
│       │           ├── sentinel/            ← 🛡️ CS + Fraud Analyst
│       │           │   ├── index.tsx
│       │           │   ├── config.ts
│       │           │   └── types.ts
│       │           ├── revenue/             ← 💰 Sales & Revenue Intel
│       │           │   ├── index.tsx
│       │           │   ├── config.ts
│       │           │   └── types.ts
│       │           ├── legal/               ← ⚖️ Compliance & Audit
│       │           │   ├── index.tsx
│       │           │   ├── config.ts
│       │           │   └── types.ts
│       │           ├── social/              ← 📢 Social Media Monitor
│       │           │   ├── index.tsx
│       │           │   ├── config.ts
│       │           │   └── types.ts
│       │           ├── logistic/            ← 📦 Inventory & Supply
│       │           │   ├── index.tsx
│       │           │   ├── config.ts
│       │           │   └── types.ts
│       │           ├── hunter/              ← 🎯 Lead Gen & Prospecting
│       │           │   ├── index.tsx
│       │           │   ├── config.ts
│       │           │   └── types.ts
│       │           ├── recruiter/           ← 👥 HR & Talent
│       │           │   ├── index.tsx
│       │           │   ├── config.ts
│       │           │   └── types.ts
│       │           ├── support/             ← 🎧 Customer Support
│       │           │   ├── index.tsx
│       │           │   ├── config.ts
│       │           │   └── types.ts
│       │           └── security/            ← 🔐 Cybersecurity Monitor
│       │               ├── index.tsx
│       │               ├── config.ts
│       │               └── types.ts
│       │
│       ├── contexts/
│       │   ├── AuthContext.tsx              ← User auth + tier state
│       │   ├── LanguageContext.tsx          ← i18n provider (ID/EN)
│       │   └── ThemeContext.tsx             ← Dark/light theme
│       │
│       ├── locales/
│       │   ├── id.json                      ← ✅ Bahasa Indonesia
│       │   └── en.json                      ← English (bilingual)
│       │
│       ├── lib/
│       │   ├── trpc.ts                      ← tRPC client
│       │   └── utils.ts
│       │
│       └── hooks/
│           ├── useAuth.ts
│           ├── useFraudAlerts.ts
│           └── useBridgeSync.ts
│
├── server/
│   ├── index.ts                             ← Express/Fastify entry
│   ├── routes.ts                            ← tRPC router aggregator
│   │
│   ├── bridge/
│   │   └── cctv-pos-bridge.ts               ← ✅ POS × CCTV sync engine
│   │
│   ├── fraud.ts                             ← R1–R4 rules engine
│   ├── fraud.visual.ts                      ← ✅ R5-VISUAL + R6-VISUAL
│   │
│   └── routers/
│       ├── auth.ts                          ← Login, session, KYC approval
│       ├── clients.ts                       ← Client CRUD + KYC workflow
│       ├── bridge.ts                        ← syncPOS tRPC endpoint
│       ├── fraud.ts                         ← Alert feed, rule config
│       └── invoice.ts                       ← Auto-invoice generation
│
├── db/
│   ├── schema.ts                            ← ✅ Drizzle ORM (all tables)
│   ├── index.ts                             ← DB connection
│   └── migrations/                          ← Auto-generated migrations
│
├── shared/
│   └── types.ts                             ← Shared TS interfaces
│
├── public/
│   └── assets/
│       ├── logo.svg
│       └── vguard-plugin-v1.zip             ← Plugin download
│
└── package.json
```

## Tier Feature Matrix

| Feature                    | DEMO | V-LITE | V-PRO | V-ULTRA |
|----------------------------|------|--------|-------|---------|
| Fraud Rules R1–R3          | ✅   | ✅     | ✅    | ✅      |
| Fraud Rules R4             | ❌   | ✅     | ✅    | ✅      |
| Cloud Video Analytics      | ❌   | ❌     | ✅    | ✅      |
| ROI Dashboard              | ❌   | ❌     | ✅    | ✅      |
| CCTV Visual Bridge (R5/R6) | ❌   | ❌     | ❌    | ✅      |
| 10 AI Agents (full)        | ❌   | 2      | 4     | ✅      |
| White-label                | ❌   | ❌     | ❌    | ✅      |
| API Integration            | ❌   | ❌     | ✅    | ✅      |

## KYC Onboarding Workflow

```
Client → /register (form) 
  → Admin reviews → Approve KYC 
  → Auto-generate Invoice 
  → Client pays 
  → Admin input: Plugin Link + UserID + Password 
  → Client access /portal unlocked
```
