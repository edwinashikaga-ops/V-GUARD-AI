# V-Guard AI Intelligence Platform — Development TODO

## Phase 1: Database & Backend Setup ✅ APPROVED

### Database Schema
- [x] Define users table with OAuth integration
- [x] Define clients table with tier assignments
- [x] Define sessions table for Client ID login
- [x] Define transactions table with fraud flags
- [x] Define cashiers table with risk scoring
- [x] Define alerts table for fraud detection
- [x] Define referrals table for commission tracking
- [x] Define invoices table for payment records
- [ ] Generate and apply Drizzle migrations (IN PROGRESS)

### Backend API - Authentication (IN PROGRESS)
- [ ] Implement `auth.login(clientId, password)` procedure
- [ ] Implement `auth.me()` procedure with tier info
- [ ] Implement `auth.logout()` procedure
- [ ] Implement session management with httpOnly cookies
- [ ] Add Client ID validation and hashing
- [ ] Write tests for auth flows

### Backend API - Client Dashboard
- [ ] Implement `client.getDashboard()` with real-time metrics
- [ ] Implement `client.getTransactions(filters)` with pagination
- [ ] Implement `client.getAlerts()` for fraud alerts
- [ ] Implement `client.getCashiers()` with risk scores
- [ ] Add transaction ingest endpoint for POS data
- [ ] Write tests for dashboard procedures

### Backend API - Fraud Detection
- [ ] Implement fraud rule engine (R1-R6)
- [ ] Implement `fraud.scanTransactions(txList)` procedure
- [ ] Implement `fraud.getAnomalies()` procedure
- [ ] Implement `fraud.getRuleStats()` procedure
- [ ] Add real-time anomaly scoring
- [ ] Write tests for each fraud rule

### Backend API - Agents
- [ ] Implement `agents.list()` procedure
- [ ] Implement `agents.getStatus(agentId)` procedure
- [ ] Implement `agents.invoke(agentId, params)` procedure
- [ ] Add agent unlock logic based on tier
- [ ] Add agent status tracking (online/standby/offline)
- [ ] Write tests for agent procedures

### Backend API - Referral Program
- [ ] Implement `referral.generateLink()` procedure
- [ ] Implement `referral.getCommissions()` procedure
- [ ] Implement `referral.getPartners()` procedure
- [ ] Add 10% commission calculation
- [ ] Add referral tracking on client signup
- [ ] Write tests for referral procedures

### Backend API - Investor Area
- [ ] Implement `investor.getMRR()` procedure
- [ ] Implement `investor.getROI()` procedure
- [ ] Implement `investor.getReturns()` procedure
- [ ] Add return history tracking
- [ ] Write tests for investor procedures

### Backend API - Admin
- [ ] Implement `admin.listClients()` procedure
- [ ] Implement `admin.approveClient(clientId)` procedure
- [ ] Implement `admin.generatePaymentLink(clientId, tier)` procedure
- [ ] Add admin-only access control
- [ ] Write tests for admin procedures

---

## Phase 2: Frontend Layout & Navigation

### App Structure
- [ ] Create `App.tsx` with Router and Layout
- [ ] Create `DashboardLayout.tsx` with sidebar navigation
- [ ] Create `Navbar.tsx` with language toggle
- [ ] Create `Footer.tsx` with links
- [ ] Implement responsive design (mobile, tablet, desktop)
- [ ] Add theme provider and dark mode setup

### Public Pages
- [ ] Create `Home.tsx` landing page
- [ ] Create `PricingPage.tsx` with tier cards
- [ ] Create `NotFound.tsx` 404 page
- [ ] Add navigation between public pages

### Portal Pages
- [ ] Create `PortalPage.tsx` with login screen
- [ ] Create `ClientDashboard.tsx` main dashboard
- [ ] Create `TransactionsPage.tsx` detailed history
- [ ] Create `AgentsPage.tsx` agent squad display
- [ ] Create `ReferralDashboard.tsx` commission tracking
- [ ] Create `InvestorDashboard.tsx` MRR and ROI
- [ ] Create `AdminPanel.tsx` client management

---

## Phase 3: Client Dashboard Features

### Dashboard Metrics & Header
- [ ] Display real-time metrics (total omset, transaction count, anomalies)
- [ ] Show live clock with WIB timezone
- [ ] Display system status (online/offline)
- [ ] Show client tier badge with color coding
- [ ] Add connection status for POS systems (MOKA, QRIS, EDC, SAP, iReap)

### Transaction Monitoring
- [ ] Implement transaction table with sorting/filtering
- [ ] Show transaction time, cashier, type, status, amount
- [ ] Highlight anomalous transactions with color coding
- [ ] Add transaction detail modal
- [ ] Implement pagination (20 items per page)
- [ ] Add export to CSV functionality

### Fraud Alerts Panel
- [ ] Display recent alerts with timestamp
- [ ] Show alert type (R1-R6) with icon and color
- [ ] Display affected cashier and transaction amount
- [ ] Add alert detail modal with rule explanation
- [ ] Implement alert dismissal
- [ ] Add alert filtering by type/severity

### Cashier Risk Scoring
- [ ] Display cashier list with risk levels (high/medium/low)
- [ ] Show risk percentage bar chart
- [ ] Color code by risk level (red/amber/green)
- [ ] Add cashier detail modal with transaction history
- [ ] Show VOID count and rate per cashier
- [ ] Implement sorting by risk level

### Agent Squad Display
- [ ] Display all 10 agents in grid layout
- [ ] Show agent name, role, icon, status
- [ ] Implement tier-based locking (show lock icon for locked agents)
- [ ] Add agent detail modal with description
- [ ] Show status indicator (online/standby/offline)
- [ ] Add "Upgrade to unlock" CTA for locked agents

---

## Phase 4: Fraud Detection & Rules

### Fraud Rule Implementation
- [ ] Implement R1: VOID Direct Flag
- [ ] Implement R2: VOID Rate Spike (> 20%)
- [ ] Implement R3: Duplicate Transactions (< 5 min)
- [ ] Implement R4: Balance Mismatch (fisik ≠ sistem)
- [ ] Implement R5: Off-Hours Transactions (< 07:00 or ≥ 23:00)
- [ ] Implement R6: Rapid VOID (> 2 in 10 min)
- [ ] Add confidence scoring for each rule
- [ ] Implement rule combination logic (multiple rules per tx)

### Real-time Anomaly Detection
- [ ] Stream transaction data via WebSocket
- [ ] Scan each transaction against R1-R6 on ingest
- [ ] Create alerts for flagged transactions
- [ ] Update dashboard metrics in real-time
- [ ] Add anomaly confidence threshold (default 70%)

### Fraud Dashboard Widgets
- [ ] Show fraud rule statistics (hits per rule)
- [ ] Display anomaly trend chart (7-day)
- [ ] Show top flagged cashiers
- [ ] Display fraud loss estimation
- [ ] Add fraud prevention ROI calculation

---

## Phase 5: Pricing & Referral Features

### Pricing Page
- [ ] Create pricing card component for each tier
- [ ] Display monthly price and activation fee
- [ ] Show feature list with checkmarks/X marks
- [ ] Implement side-by-side feature comparison
- [ ] Add WhatsApp CTA links for each tier
- [ ] Show popular/hot badges for V-PRO and V-ULTRA
- [ ] Add FAQ section with collapsible items
- [ ] Implement tier comparison toggle (feature view)

### Referral Dashboard
- [ ] Display referral link with copy button
- [ ] Show total commissions earned (10% rate)
- [ ] Display commission history table
- [ ] Show active partners list with signup date
- [ ] Add commission breakdown by tier
- [ ] Implement referral link customization
- [ ] Add referral performance chart (7-day/30-day)
- [ ] Show pending commissions vs paid

### Referral Link Generation
- [ ] Generate unique referral URL per client
- [ ] Track referral source in query params
- [ ] Store referral relationship in database
- [ ] Calculate 10% commission on referred client subscription
- [ ] Auto-approve referral commissions on payment confirmation
- [ ] Send referral bonus notification via WhatsApp

---

## Phase 6: Investor Area & Admin Panel

### Investor Dashboard
- [ ] Display MRR (Monthly Recurring Revenue) metric
- [ ] Show MRR trend chart (3-month, 6-month, 12-month)
- [ ] Display ROI history table with dates and yields
- [ ] Show roadmap with phases (done, active, pending)
- [ ] Display return history with payout dates
- [ ] Add profitability breakdown by tier
- [ ] Show active client count and growth rate

### Admin Panel
- [ ] Display list of all clients with status
- [ ] Show client tier, signup date, MRR contribution
- [ ] Implement client approval workflow
- [ ] Add client tier upgrade/downgrade functionality
- [ ] Display payment status (pending, paid, overdue)
- [ ] Add manual payment link generation
- [ ] Show system-wide fraud statistics
- [ ] Add admin notifications for new signups

---

## Phase 7: Demo Mode & Tier Gating

### Demo Mode Implementation
- [ ] Implement 15-minute countdown timer
- [ ] Add "DEMO MODE" watermark overlay (fixed, rotated)
- [ ] Restrict agent access to 2 agents (Concierge, Watchdog)
- [ ] Lock premium features with upgrade CTAs
- [ ] Show demo timeout warning at 2 minutes
- [ ] Auto-logout on timeout with restart option
- [ ] Track demo session start time in session state

### Tier Gating System
- [ ] Implement `is_feature_unlocked(featureKey, tier)` helper
- [ ] Implement `is_agent_unlocked(agentId, tier)` helper
- [ ] Create `render_locked_card()` component for locked features
- [ ] Create `render_upgrade_banner()` component for inline upsells
- [ ] Add tier badge display with color coding
- [ ] Implement admin bypass for all locks
- [ ] Add tier-based navigation (hide unavailable menu items)

### Upgrade Prompts
- [ ] Show upgrade CTA on locked feature access
- [ ] Generate WhatsApp upgrade link with feature name
- [ ] Display tier requirement and benefits
- [ ] Add "Learn more" link to pricing page
- [ ] Track upgrade prompt clicks for analytics
- [ ] Implement upgrade modal with tier comparison

---

## Phase 8: Bilingual Support & Localization

### Translation System
- [ ] Create `translations.ts` with ID/EN content
- [ ] Implement `useLanguage()` hook
- [ ] Add language toggle in navbar
- [ ] Store language preference in localStorage
- [ ] Support `?lang=en` query parameter
- [ ] Translate all UI text (nav, pages, modals, buttons)
- [ ] Translate fraud rule names and descriptions
- [ ] Translate agent names and roles (keep English as fallback)

### Bilingual Content
- [ ] Translate landing page (hero, features, pricing)
- [ ] Translate portal pages (dashboard, transactions, agents)
- [ ] Translate referral and investor dashboards
- [ ] Translate admin panel
- [ ] Translate error messages and notifications
- [ ] Translate WhatsApp message templates
- [ ] Add RTL support consideration (future)

### Localization Details
- [ ] Format currency as IDR (Rp) with proper separators
- [ ] Format dates as DD/MM/YYYY (ID) or MM/DD/YYYY (EN)
- [ ] Format time as HH:MM:SS WIB
- [ ] Translate month/day names
- [ ] Translate status labels (Aktif, Pending, Offline)
- [ ] Translate fraud rule labels (R1, R2, etc.)

---

## Phase 9: Sentinel CS Chatbot Widget

### Chatbot Component
- [ ] Create floating chatbot widget (bottom-right corner)
- [ ] Implement message display with user/bot distinction
- [ ] Add quick-reply buttons for common questions
- [ ] Show online status indicator
- [ ] Implement chat history in session
- [ ] Add close/minimize button
- [ ] Style with brand colors and animations

### Quick Reply Options
- [ ] "🛡️ Tentang V-Guard" → Product overview
- [ ] "📦 Pilih Paket UMKM" → Tier recommendations
- [ ] "📊 Hitung ROI" → ROI calculation example
- [ ] "📅 Book Demo" → Demo booking instructions
- [ ] Add more options based on user tier

### Chatbot Responses
- [ ] Pre-written responses for each quick reply
- [ ] Include WhatsApp contact link in responses
- [ ] Show pricing info for tier recommendations
- [ ] Display ROI calculation example
- [ ] Add demo booking link
- [ ] Implement response formatting with markdown

---

## Phase 10: Public Landing Page

### Hero Section
- [ ] Create hero banner with headline
- [ ] Add subheadline and value proposition
- [ ] Include CTA buttons (Mulai/Demo)
- [ ] Add background gradient or pattern
- [ ] Display trust badge ("Dipercaya 500+ Bisnis")
- [ ] Make responsive for mobile

### Features Section
- [ ] Display key features with icons
- [ ] Show feature descriptions
- [ ] Add feature benefits
- [ ] Implement feature tabs or carousel
- [ ] Make visually distinct and scannable

### ROI Calculator Modal
- [ ] Create modal with input fields
- [ ] Inputs: omzet (monthly), fraud rate, transaction count
- [ ] Calculate: annual loss, annual cost, savings, ROI, payback period
- [ ] Display results with visual indicators
- [ ] Add WhatsApp CTA with calculated ROI
- [ ] Make calculator mobile-friendly

### Pricing Preview
- [ ] Show 3-5 tier cards on landing page
- [ ] Include monthly price and activation fee
- [ ] Show key features per tier
- [ ] Add "View All Plans" CTA
- [ ] Link to full pricing page

### Testimonials & Social Proof
- [ ] Add client testimonials (3-5)
- [ ] Show client logos or names
- [ ] Display trust metrics (uptime, security, support)
- [ ] Add security badges and certifications

---

## Phase 11: Testing & Quality Assurance

### Unit Tests
- [ ] Test fraud detection rules (R1-R6)
- [ ] Test tier gating logic
- [ ] Test commission calculations
- [ ] Test MRR calculations
- [ ] Test referral link generation
- [ ] Achieve 80%+ code coverage

### Integration Tests
- [ ] Test auth flow (login, logout, session)
- [ ] Test client dashboard data flow
- [ ] Test transaction ingest and fraud scanning
- [ ] Test referral tracking
- [ ] Test admin approval workflow

### E2E Tests
- [ ] Test public landing page flows
- [ ] Test pricing page interactions
- [ ] Test client portal login
- [ ] Test dashboard navigation
- [ ] Test referral link generation
- [ ] Test demo mode timeout

### Performance Testing
- [ ] Measure page load times (< 2s target)
- [ ] Test with 1000+ transactions
- [ ] Test WebSocket connection stability
- [ ] Test database query performance
- [ ] Implement caching strategies

### Accessibility Testing
- [ ] Verify WCAG 2.1 AA compliance
- [ ] Test keyboard navigation
- [ ] Test screen reader compatibility
- [ ] Test color contrast ratios
- [ ] Test form accessibility

### Security Testing
- [ ] Test authentication bypass attempts
- [ ] Test authorization (tier gating)
- [ ] Test SQL injection prevention
- [ ] Test CSRF protection
- [ ] Test rate limiting
- [ ] Verify HTTPS enforcement

---

## Phase 12: Optimization & Deployment

### Frontend Optimization
- [ ] Implement code splitting by route
- [ ] Lazy load heavy components
- [ ] Optimize images and assets
- [ ] Minify CSS and JavaScript
- [ ] Enable gzip compression
- [ ] Implement service worker for offline support

### Backend Optimization
- [ ] Add database query optimization
- [ ] Implement caching (Redis)
- [ ] Add API response compression
- [ ] Optimize fraud scanning algorithm
- [ ] Implement batch processing for bulk operations

### Monitoring & Logging
- [ ] Set up error tracking (Sentry)
- [ ] Implement structured logging
- [ ] Add performance monitoring
- [ ] Set up uptime monitoring
- [ ] Add user analytics tracking

### Deployment Preparation
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Create deployment checklist
- [ ] Document environment variables
- [ ] Create database backup strategy
- [ ] Plan rollback procedures

---

## Phase 13: Final Checkpoint & Delivery

### Pre-Launch Checklist
- [ ] All features implemented and tested
- [ ] Documentation complete (README, API docs, user guide)
- [ ] Security audit passed
- [ ] Performance targets met
- [ ] Accessibility audit passed
- [ ] Mobile responsiveness verified
- [ ] Bilingual support verified
- [ ] Demo mode tested
- [ ] Tier gating verified for all tiers
- [ ] Fraud rules tested with sample data

### Deployment
- [ ] Create final checkpoint
- [ ] Deploy backend to Railway
- [ ] Deploy frontend to Vercel
- [ ] Verify production environment
- [ ] Test all critical flows in production
- [ ] Set up monitoring and alerts
- [ ] Create runbook for incident response

### Documentation
- [ ] Create user guide (client, admin, investor)
- [ ] Create API documentation
- [ ] Create deployment guide
- [ ] Create troubleshooting guide
- [ ] Create SOP for support team

### Launch
- [ ] Announce to stakeholders
- [ ] Send launch email to waitlist
- [ ] Update social media
- [ ] Monitor for issues
- [ ] Gather user feedback
- [ ] Plan post-launch improvements

---

## Notes

- **Color Scheme:** Dark mode (bg: #0B0F1A, accent: #00D4FF, danger: #FF3B5C)
- **Typography:** Rajdhani (headings), Inter (body), JetBrains Mono (data)
- **Fraud Rules:** R1-R6 must be implemented in order of priority (V-LITE first)
- **Agent Names:** Must use exact names as specified (Visionary, Concierge, etc.)
- **Tier Names:** Must use exact names (V-LITE, V-PRO, V-ADVANCE, V-ELITE, V-ULTRA)
- **Commission Rate:** Fixed at 10% for all referrals
- **Demo Duration:** Exactly 15 minutes (900 seconds)
- **WhatsApp Integration:** Use query param encoding for message templates

---

**Last Updated:** 2026-05-02
**Status:** Ready for Phase 1 implementation
