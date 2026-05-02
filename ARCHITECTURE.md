# V-Guard AI Intelligence Platform — Architecture & Development Plan

## Project Overview

**V-Guard AI** is a multi-tier SaaS fraud detection and business intelligence platform designed for Indonesian SMEs and enterprises. The platform features real-time transaction monitoring, AI-powered fraud detection, and role-based dashboards for clients, referral agents, investors, and administrators.

**Tech Stack:**
- **Frontend:** React 19 + TypeScript + Tailwind CSS 4 (Vercel)
- **Backend:** Express.js + tRPC + Drizzle ORM (Railway)
- **Database:** MySQL/TiDB
- **Authentication:** Manus OAuth + Client ID login
- **Real-time:** WebSocket for transaction updates
- **Storage:** S3 for file uploads

---

## 1. Core Data Model

### Users & Authentication
- **users** table: Standard OAuth users (admin, owner)
- **clients** table: Business clients with tier assignments
- **sessions** table: Session management for Client ID login

### Business Data
- **transactions** table: POS transaction records with fraud flags
- **cashiers** table: Cashier profiles with risk scoring
- **alerts** table: Fraud detection alerts
- **referrals** table: Referral program tracking
- **invoices** table: Payment invoices for tier upgrades

### Tier System
```
DEMO (0)        → 15-min preview, 2 agents (Concierge, Watchdog)
V-LITE (1)      → 4 agents, basic fraud rules (R1-R3)
V-PRO (2)       → All 10 agents, advanced rules (R1-R6), bank audit
V-ADVANCE (3)   → CCTV integration, multi-branch, real-time dashboard
V-ELITE (4)     → Dedicated server, forensic deep scan, custom SOP
V-ULTRA (5)     → White-label, neural network, SAP B1 export
ADMIN (99)      → Full system access
```

---

## 2. Backend Architecture (Express + tRPC)

### API Routes Structure
```
/api/trpc/
  ├── auth.*              (login, logout, me)
  ├── client.*            (dashboard, transactions, alerts)
  ├── fraud.*             (detection rules, anomaly scoring)
  ├── agents.*            (agent status, unlocking)
  ├── referral.*          (links, commissions, partners)
  ├── investor.*          (MRR, ROI, returns)
  ├── pricing.*           (tier info, payment links)
  └── admin.*             (client management, system monitoring)

/api/socket              (WebSocket for real-time updates)
/api/webhooks/           (Payment confirmations, external integrations)
```

### Key Procedures (tRPC)

**Authentication:**
- `auth.login(clientId, password)` → Session token
- `auth.me()` → Current user with tier info
- `auth.logout()` → Clear session

**Client Dashboard:**
- `client.getDashboard()` → Real-time metrics, transactions, alerts
- `client.getTransactions(filters)` → Paginated transaction list
- `client.getAlerts()` → Recent fraud alerts
- `client.getCashiers()` → Cashier risk scores

**Fraud Detection:**
- `fraud.scanTransactions(txList)` → Apply R1-R6 rules
- `fraud.getAnomalies()` → Detected anomalies with confidence
- `fraud.getRuleStats()` → Rule hit counts by type

**Agents:**
- `agents.list()` → All 10 agents with unlock status
- `agents.getStatus(agentId)` → Real-time agent status
- `agents.invoke(agentId, params)` → Trigger agent action

**Referral:**
- `referral.generateLink()` → Create unique referral URL
- `referral.getCommissions()` → 10% commission tracking
- `referral.getPartners()` → Referred clients list

**Investor:**
- `investor.getMRR()` → Monthly recurring revenue
- `investor.getROI()` → Return on investment metrics
- `investor.getReturns()` → Historical return table

**Admin:**
- `admin.listClients()` → All clients with status
- `admin.approveClient(clientId)` → Activate pending client
- `admin.generatePaymentLink(clientId, tier)` → WhatsApp invoice

---

## 3. Frontend Architecture (React + Tailwind)

### Page Structure
```
/                       → Public landing page (hero, features, ROI calc)
/pricing                → Tier comparison, WhatsApp CTAs
/portal                 → Client login (Client ID input)
/portal/dashboard       → Main client dashboard (tier-gated)
/portal/transactions    → Detailed transaction history
/portal/agents          → AI agent squad display
/portal/referral        → Referral dashboard (commission tracking)
/portal/investor        → Investor area (MRR, ROI, returns)
/admin                  → Admin panel (client management)
```

### Component Hierarchy
```
App
├── Layout (navbar, sidebar, footer)
├── Router
│   ├── HomePage
│   │   ├── HeroSection
│   │   ├── FeaturesSection
│   │   ├── ROICalculator (modal)
│   │   ├── PricingPreview
│   │   └── SentinelCS (chatbot)
│   ├── PricingPage
│   │   ├── PricingCard (x5)
│   │   └── FeatureComparison
│   ├── PortalPage
│   │   ├── LoginScreen (Client ID)
│   │   └── PortalDashboard
│   │       ├── Sidebar (navigation)
│   │       ├── ClientDashboard
│   │       │   ├── MetricsHeader
│   │       │   ├── TransactionTable
│   │       │   ├── AlertsPanel
│   │       │   ├── CashierRiskScores
│   │       │   └── AgentSquad
│   │       ├── ReferralDashboard
│   │       ├── InvestorDashboard
│   │       └── AdminPanel
│   └── NotFound
└── Modals
    ├── UpgradeModal
    ├── DemoTimeoutModal
    └── ROICalculatorModal
```

### Design System
- **Color Palette:** Dark mode (bg: #0B0F1A, accent: #00D4FF, danger: #FF3B5C)
- **Typography:** Rajdhani (headings), Inter (body), JetBrains Mono (data)
- **Components:** shadcn/ui + custom Tailwind utilities
- **Responsive:** Mobile-first, tablet & desktop breakpoints

---

## 4. Fraud Detection Engine (R1-R6)

| Rule | Name | Condition | Min Tier | Color |
|------|------|-----------|----------|-------|
| R1 | VOID Direct Flag | Any VOID transaction | V-LITE | #FF3B5C |
| R2 | VOID Rate Spike | VOID % > 20% per cashier | V-LITE | #FF3B5C |
| R3 | Duplicate Tx | Same cashier + amount < 5 min | V-LITE | #FFAB00 |
| R4 | Balance Mismatch | Saldo fisik ≠ saldo sistem | V-PRO | #FFAB00 |
| R5 | Off-Hours Tx | Time < 07:00 or ≥ 23:00 WIB | V-PRO | #7B2FFF |
| R6 | Rapid VOID | > 2 VOIDs in 10 minutes | V-PRO | #FF3B5C |

**Implementation:**
- Rules stored in `FRAUD_RULES_ALL` constant
- Scanned on transaction ingest via `fraud.scanTransactions()`
- Flagged transactions create alerts in real-time
- UI shows rule violations with confidence scores

---

## 5. AI Agent Squad (10 Agents)

| ID | Name | Role | Icon | Min Tier |
|----|------|------|------|----------|
| 1 | Visionary | CCTV Visual Intelligence | 👁️ | V-ADVANCE |
| 2 | Concierge | CS Intelligence | 🤝 | V-LITE |
| 3 | GrowthHacker | Marketing Automation | 📣 | V-LITE |
| 4 | Liaison | POS Integration | 🔗 | V-PRO |
| 5 | Analyst | Financial Forensic | 🏦 | V-PRO |
| 6 | Stockmaster | Inventory OCR | 📦 | V-PRO |
| 7 | Watchdog | Fraud Detector | 🐕 | V-LITE |
| 8 | Sentinel | Infra Monitor | 🖥️ | V-PRO |
| 9 | Legalist | Compliance | ⚖️ | V-PRO |
| 10 | Treasurer | Gross Revenue Monitor | 💰 | V-LITE |

**Display:**
- Agent cards show name, role, status (online/standby/offline)
- Locked agents show tier requirement + upgrade CTA
- Each agent has a dedicated detail view (future expansion)

---

## 6. Tier Gating & Feature Access

**Feature Tier Map:**
```
fraud_rules_r1_r2_r3    → V-LITE
fraud_rules_r4_r5_r6    → V-PRO
bank_audit              → V-PRO
ocr_invoice             → V-PRO
cctv_ai_live            → V-ADVANCE
multi_branch            → V-ADVANCE
dedicated_server        → V-ELITE
forensic_deep_scan      → V-ELITE
white_label             → V-ULTRA
neural_network          → V-ULTRA
```

**Implementation:**
- `is_feature_unlocked(featureKey, tier)` helper function
- `is_agent_unlocked(agentId, tier)` for agent access
- Locked features show `render_locked_card()` with upgrade CTA
- Admin bypasses all locks

---

## 7. Demo Mode & Tier Gating

**Demo Behavior:**
- 15-minute countdown timer
- Watermark overlay ("DEMO MODE")
- Access to 2 agents only (Concierge, Watchdog)
- Locked-card upsells for premium features
- Auto-logout on timeout with restart option

**Session State:**
```
mode: "PUBLIC" | "DEMO" | "PRODUCTION" | "ADMIN"
current_tier: "V-LITE" | "V-PRO" | ... | null
demo_start_time: ISO timestamp
demo_tier_preview: "V-LITE" (default demo tier)
```

---

## 8. Referral Program

**Commission Structure:**
- 10% flat rate on all referred client subscriptions
- Tracked via `referrals` table (referrer_id, referred_id, commission_amount)
- Referral link format: `https://v-guard-ai.com/?ref={clientId}&source=referral`
- Dashboard shows: total commissions, active partners, commission history

---

## 9. Investor Area

**Metrics Displayed:**
- **MRR (Monthly Recurring Revenue):** Sum of active client subscriptions
- **ROI History:** Table of returns by date with yield %
- **Roadmap:** Phases (done, active, pending) with descriptions
- **Return History:** Detailed payout records

---

## 10. Bilingual Support (ID/EN)

**Translation Structure:**
```
translations = {
  id: {
    nav: { ... },
    beranda: { title, subtitle, features, ... },
    harga: { title, subtitle, faq, ... },
    portal: { ... },
    investor: { ... },
  },
  en: { ... }
}
```

**Implementation:**
- `useLanguage()` hook for current language
- Language toggle in navbar
- Query param `?lang=en` to set language
- Stored in localStorage for persistence

---

## 11. Development Workflow

### Phase 1: Database & Backend
1. Define schema in `drizzle/schema.ts`
2. Generate migrations with `pnpm drizzle-kit generate`
3. Apply migrations via `webdev_execute_sql`
4. Implement tRPC procedures in `server/routers.ts`
5. Write tests in `server/*.test.ts`

### Phase 2: Frontend Layout
1. Create `App.tsx` with Router and Layout
2. Build `DashboardLayout` with sidebar navigation
3. Implement `Home.tsx` landing page
4. Add `PortalPage` with login screen

### Phase 3: Feature Implementation
1. Client dashboard with transaction monitoring
2. Fraud detection engine integration
3. Agent squad display with tier gating
4. Pricing page with feature comparison
5. Referral & investor dashboards
6. Demo mode & upgrade prompts
7. Bilingual support
8. Chatbot widget

### Phase 4: Testing & Optimization
1. Unit tests for fraud detection rules
2. E2E tests for auth flows
3. Performance optimization (lazy loading, code splitting)
4. Accessibility audit (WCAG 2.1 AA)
5. Mobile responsiveness testing

---

## 12. Deployment Strategy

**Frontend (Vercel):**
- Deploy from GitHub on every push to `main`
- Environment: `VITE_API_URL=https://api.railway.app`
- Auto-scaling, CDN, edge functions

**Backend (Railway):**
- Deploy from GitHub on every push to `main`
- Environment: `DATABASE_URL`, `JWT_SECRET`, OAuth credentials
- Auto-restart on crash, health checks
- WebSocket support via Socket.io

**Database (Railway MySQL):**
- Managed MySQL instance
- Automated backups, point-in-time recovery
- SSL connection required

---

## 13. Security Considerations

- **Authentication:** OAuth + Client ID + session cookies (httpOnly, secure)
- **Authorization:** Role-based access control (RBAC) via tier system
- **Data Protection:** Encrypted at rest (AES-256), in transit (TLS 1.3)
- **Rate Limiting:** 100 req/min per IP for public endpoints
- **CSRF Protection:** Token validation on state-changing operations
- **Input Validation:** Zod schemas on all tRPC inputs
- **SQL Injection:** Parameterized queries via Drizzle ORM

---

## 14. Monitoring & Analytics

- **Error Tracking:** Sentry integration
- **Performance:** New Relic APM
- **Logs:** Structured logging to ELK stack
- **Uptime:** Pingdom monitoring
- **User Analytics:** Manus Analytics (built-in)

---

## 15. Future Enhancements

- [ ] CCTV stream integration with Visionary agent
- [ ] Real-time POS data sync via Liaison agent
- [ ] Bank reconciliation automation via Analyst agent
- [ ] Invoice OCR via Stockmaster agent
- [ ] WhatsApp Business API integration for alerts
- [ ] Mobile app (React Native)
- [ ] Advanced reporting & BI dashboards
- [ ] Machine learning fraud prediction model
- [ ] Multi-currency support
- [ ] Custom branding (white-label for V-ULTRA)

---

**Last Updated:** 2026-05-02
**Version:** 1.0.0
