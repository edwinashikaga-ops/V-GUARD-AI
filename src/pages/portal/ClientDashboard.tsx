// client/src/pages/portal/ClientDashboard.tsx
// ─────────────────────────────────────────────────────────────
// V-Guard AI — Client Portal Dashboard
// Features: KPI Cards, Fraud Alert Feed (R1–R6 + Visual),
//           Plugin Download, Agent Status, TierGate gating
// Bilingual: ID / EN
// ─────────────────────────────────────────────────────────────
import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { useLanguage } from "@/contexts/LanguageContext";
import { useAuth } from "@/contexts/AuthContext";
import { TierGate } from "@/components/TierGate";

// ── Types ─────────────────────────────────────────────────────

type AlertRule    = "R1" | "R2" | "R3" | "R4" | "R5-VISUAL" | "R6-VISUAL";
type Severity     = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
type AlertStatus  = "NEW" | "ACKNOWLEDGED" | "RESOLVED" | "FALSE_POSITIVE";

interface FraudAlert {
  id:              number;
  alertCode:       AlertRule;
  ruleName:        string;
  severity:        Severity;
  status:          AlertStatus;
  cashierName:     string;
  transactionType: string;
  amount:          number;
  anomalyScore:    number;
  occurredAt:      string;
  // Visual evidence (R5/R6 only — V-ULTRA)
  cctvThumbnailUrl?: string;
  cctvCapturedAt?:   string;
  visualItemCount?:  number;
  confidenceScore?:  number;
}

interface KPIData {
  totalOmset:        number;
  totalTransactions: number;
  totalAnomalies:    number;
  activeCashiers:    number;
  alertsToday:       number;
  preventedLoss:     number;
  systemStatus:      "ONLINE" | "OFFLINE" | "DEGRADED";
  lastSync:          string;
}

interface ClientCredential {
  userId:       string;
  pluginLink:   string;
  pluginVersion: string;
  tier:         string;
  packageName:  string;
  expiresAt:    string;
}

// ── i18n ─────────────────────────────────────────────────────

const T = {
  id: {
    welcome:       "Selamat datang",
    dashboard:     "Dashboard Utama",
    omset:         "Total Omset",
    transactions:  "Transaksi",
    anomalies:     "Anomali Terdeteksi",
    cashiers:      "Kasir Aktif",
    alertsToday:   "Alert Hari Ini",
    prevented:     "Potensi Kerugian Dicegah",
    systemOnline:  "Sistem Online",
    systemOffline: "Sistem Offline",
    lastSync:      "Sync terakhir",
    credentials:   "Kredensial & Plugin",
    userId:        "User ID",
    copyId:        "Salin",
    copied:        "Tersalin!",
    downloadPlugin:"Download Plugin",
    tierBadge:     "Paket Aktif",
    expiry:        "Aktif hingga",
    alertFeed:     "Feed Alert Fraud",
    noAlerts:      "Tidak ada alert. Sistem aman! ✅",
    markResolved:  "Tandai Selesai",
    viewEvidence:  "Lihat Bukti CCTV",
    agentStatus:   "Status AI Agent",
    upgradeNotice: "Upgrade ke V-ULTRA untuk aktivasi penuh",
    score:         "Skor",
    cashier:       "Kasir",
    txType:        "Tipe",
    amount:        "Nominal",
    time:          "Waktu",
    visual:        "Bukti Visual",
    itemsDetected: "Item Terdeteksi",
    confidence:    "Confidence",
    filterAll:     "Semua",
    filterNew:     "Baru",
    filterCritical:"Kritis",
    logout:        "Keluar",
    portal:        "Portal Klien",
  },
  en: {
    welcome:       "Welcome",
    dashboard:     "Main Dashboard",
    omset:         "Total Revenue",
    transactions:  "Transactions",
    anomalies:     "Anomalies Detected",
    cashiers:      "Active Cashiers",
    alertsToday:   "Alerts Today",
    prevented:     "Potential Loss Prevented",
    systemOnline:  "System Online",
    systemOffline: "System Offline",
    lastSync:      "Last sync",
    credentials:   "Credentials & Plugin",
    userId:        "User ID",
    copyId:        "Copy",
    copied:        "Copied!",
    downloadPlugin:"Download Plugin",
    tierBadge:     "Active Plan",
    expiry:        "Active until",
    alertFeed:     "Fraud Alert Feed",
    noAlerts:      "No alerts. System is safe! ✅",
    markResolved:  "Mark Resolved",
    viewEvidence:  "View CCTV Evidence",
    agentStatus:   "AI Agent Status",
    upgradeNotice: "Upgrade to V-ULTRA for full activation",
    score:         "Score",
    cashier:       "Cashier",
    txType:        "Type",
    amount:        "Amount",
    time:          "Time",
    visual:        "Visual Evidence",
    itemsDetected: "Items Detected",
    confidence:    "Confidence",
    filterAll:     "All",
    filterNew:     "New",
    filterCritical:"Critical",
    logout:        "Logout",
    portal:        "Client Portal",
  },
};

// ── Mock Data (replace with tRPC calls) ───────────────────────

const MOCK_KPI: KPIData = {
  totalOmset:        142_500_000,
  totalTransactions: 3_847,
  totalAnomalies:    12,
  activeCashiers:    4,
  alertsToday:       3,
  preventedLoss:     8_750_000,
  systemStatus:      "ONLINE",
  lastSync:          new Date().toISOString(),
};

const MOCK_ALERTS: FraudAlert[] = [
  {
    id: 1, alertCode: "R6-VISUAL", ruleName: "VOID + Barang Terlihat",
    severity: "CRITICAL", status: "NEW",
    cashierName: "Budi Santoso", transactionType: "VOID",
    amount: 185_000, anomalyScore: 95,
    occurredAt: new Date(Date.now() - 10 * 60000).toISOString(),
    cctvThumbnailUrl: "https://placehold.co/640x360/1e293b/94a3b8?text=CCTV+Frame+R6",
    cctvCapturedAt: new Date(Date.now() - 10 * 60000).toISOString(),
    visualItemCount: 4, confidenceScore: 0.91,
  },
  {
    id: 2, alertCode: "R5-VISUAL", ruleName: "Mismatch Item Visual",
    severity: "HIGH", status: "NEW",
    cashierName: "Siti Rahayu", transactionType: "PENJUALAN",
    amount: 320_000, anomalyScore: 72,
    occurredAt: new Date(Date.now() - 25 * 60000).toISOString(),
    cctvThumbnailUrl: "https://placehold.co/640x360/1e293b/94a3b8?text=CCTV+Frame+R5",
    cctvCapturedAt: new Date(Date.now() - 25 * 60000).toISOString(),
    visualItemCount: 7, confidenceScore: 0.83,
  },
  {
    id: 3, alertCode: "R2", ruleName: "Lonjakan VOID",
    severity: "HIGH", status: "ACKNOWLEDGED",
    cashierName: "Ahmad Fauzi", transactionType: "VOID",
    amount: 95_000, anomalyScore: 65,
    occurredAt: new Date(Date.now() - 65 * 60000).toISOString(),
  },
  {
    id: 4, alertCode: "R1", ruleName: "VOID Langsung",
    severity: "MEDIUM", status: "RESOLVED",
    cashierName: "Dewi Lestari", transactionType: "VOID",
    amount: 45_000, anomalyScore: 35,
    occurredAt: new Date(Date.now() - 180 * 60000).toISOString(),
  },
];

const MOCK_CREDENTIALS: ClientCredential = {
  userId:        "VG-2024-00042",
  pluginLink:    "/assets/vguard-plugin-v1.zip",
  pluginVersion: "v1.4.2",
  tier:          "V-ULTRA",
  packageName:   "V-ULTRA Premium",
  expiresAt:     "2025-12-31",
};

const AGENT_LIST = [
  { id: "visionary",  icon: "👁️",  name: "Visionary",  minTier: "V-ULTRA",  activeFor: ["V-ULTRA"] },
  { id: "sentinel",   icon: "🛡️",  name: "Sentinel",   minTier: "V-LITE",   activeFor: ["V-LITE","V-PRO","V-ADVANCE","V-ELITE","V-ULTRA"] },
  { id: "revenue",    icon: "💰",  name: "Revenue",    minTier: "V-PRO",    activeFor: ["V-PRO","V-ADVANCE","V-ELITE","V-ULTRA"] },
  { id: "legal",      icon: "⚖️",  name: "Legal",      minTier: "V-PRO",    activeFor: ["V-PRO","V-ADVANCE","V-ELITE","V-ULTRA"] },
  { id: "social",     icon: "📢",  name: "Social",     minTier: "V-ADVANCE",activeFor: ["V-ADVANCE","V-ELITE","V-ULTRA"] },
  { id: "logistic",   icon: "📦",  name: "Logistic",   minTier: "V-ADVANCE",activeFor: ["V-ADVANCE","V-ELITE","V-ULTRA"] },
  { id: "hunter",     icon: "🎯",  name: "Hunter",     minTier: "V-ELITE",  activeFor: ["V-ELITE","V-ULTRA"] },
  { id: "recruiter",  icon: "👥",  name: "Recruiter",  minTier: "V-ELITE",  activeFor: ["V-ELITE","V-ULTRA"] },
  { id: "support",    icon: "🎧",  name: "Support",    minTier: "V-ULTRA",  activeFor: ["V-ULTRA"] },
  { id: "security",   icon: "🔐",  name: "Security",   minTier: "V-ULTRA",  activeFor: ["V-ULTRA"] },
];

// ── Helpers ───────────────────────────────────────────────────

function formatRupiah(n: number) {
  if (n >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(1)}M`;
  if (n >= 1_000_000)     return `${(n / 1_000_000).toFixed(1)}Jt`;
  if (n >= 1_000)         return `${(n / 1_000).toFixed(0)}rb`;
  return n.toString();
}

function timeAgo(iso: string, lang: "id" | "en") {
  const mins = Math.floor((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 1)   return lang === "id" ? "Baru saja" : "Just now";
  if (mins < 60)  return lang === "id" ? `${mins} mnt lalu` : `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24)   return lang === "id" ? `${hrs} jam lalu` : `${hrs}h ago`;
  return lang === "id" ? `${Math.floor(hrs/24)} hari lalu` : `${Math.floor(hrs/24)}d ago`;
}

const SEVERITY_CONFIG = {
  CRITICAL: { bg: "bg-red-500/15",    border: "border-red-500/40",    text: "text-red-400",    dot: "bg-red-400"    },
  HIGH:     { bg: "bg-orange-500/15", border: "border-orange-500/40", text: "text-orange-400", dot: "bg-orange-400" },
  MEDIUM:   { bg: "bg-yellow-500/15", border: "border-yellow-500/40", text: "text-yellow-400", dot: "bg-yellow-400" },
  LOW:      { bg: "bg-blue-500/15",   border: "border-blue-500/40",   text: "text-blue-400",   dot: "bg-blue-400"   },
};

const STATUS_CONFIG = {
  NEW:           { label: { id: "Baru",          en: "New"          }, cls: "bg-red-500/20 text-red-400 border-red-500/30"      },
  ACKNOWLEDGED:  { label: { id: "Ditangani",     en: "Acknowledged" }, cls: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30" },
  RESOLVED:      { label: { id: "Selesai",       en: "Resolved"     }, cls: "bg-green-500/20 text-green-400 border-green-500/30"   },
  FALSE_POSITIVE:{ label: { id: "False Positive",en: "False Positive"}, cls: "bg-slate-500/20 text-slate-400 border-slate-500/30" },
};

// ── Sub-components ────────────────────────────────────────────

function KPICard({ icon, label, value, sub, accent }: {
  icon: string; label: string; value: string; sub?: string; accent?: string;
}) {
  return (
    <div className={`bg-slate-900/60 border border-slate-700/50 rounded-2xl p-5 backdrop-blur-sm hover:border-slate-600 transition-all group ${accent ? `hover:border-${accent}-500/50` : ""}`}>
      <div className="flex items-start justify-between mb-3">
        <div className="text-2xl">{icon}</div>
        {sub && <span className="text-xs text-slate-500 font-mono bg-slate-800 px-2 py-0.5 rounded-full">{sub}</span>}
      </div>
      <div className={`text-2xl font-black mb-1 ${accent ? `text-${accent}-400` : "text-white"}`}>{value}</div>
      <div className="text-xs text-slate-400 font-medium">{label}</div>
    </div>
  );
}

function AlertCard({
  alert, lang, onResolve,
}: { alert: FraudAlert; lang: "id" | "en"; onResolve: (id: number) => void }) {
  const [showEvidence, setShowEvidence] = useState(false);
  const sev = SEVERITY_CONFIG[alert.severity];
  const stat = STATUS_CONFIG[alert.status];
  const isVisual = alert.alertCode === "R5-VISUAL" || alert.alertCode === "R6-VISUAL";
  const t = T[lang];

  return (
    <div className={`rounded-2xl border p-4 space-y-3 transition-all ${sev.bg} ${sev.border}`}>
      {/* Header row */}
      <div className="flex items-start justify-between gap-2 flex-wrap">
        <div className="flex items-center gap-2 flex-wrap">
          <div className={`w-2 h-2 rounded-full flex-shrink-0 ${sev.dot} ${alert.status === "NEW" ? "animate-pulse" : ""}`} />
          <span className={`font-mono text-sm font-bold ${sev.text}`}>{alert.alertCode}</span>
          <span className="text-slate-300 text-sm font-medium">{alert.ruleName}</span>
          {isVisual && (
            <span className="px-2 py-0.5 bg-purple-500/20 border border-purple-500/30 text-purple-400 text-xs rounded-full font-mono">
              📷 CCTV
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${stat.cls}`}>
            {stat.label[lang]}
          </span>
          <span className="text-xs font-mono text-slate-500">
            {t.score}: <span className={`font-bold ${sev.text}`}>{alert.anomalyScore}</span>
          </span>
        </div>
      </div>

      {/* Info row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: t.cashier, value: alert.cashierName },
          { label: t.txType,  value: alert.transactionType },
          { label: t.amount,  value: `Rp ${alert.amount.toLocaleString("id-ID")}` },
          { label: t.time,    value: timeAgo(alert.occurredAt, lang) },
        ].map((item) => (
          <div key={item.label}>
            <div className="text-xs text-slate-500 mb-0.5">{item.label}</div>
            <div className="text-sm text-white font-medium">{item.value}</div>
          </div>
        ))}
      </div>

      {/* Visual Evidence (R5/R6 - V-ULTRA only) */}
      {isVisual && alert.cctvThumbnailUrl && (
        <div>
          <button
            onClick={() => setShowEvidence(!showEvidence)}
            className="flex items-center gap-2 text-xs text-purple-400 hover:text-purple-300 font-medium transition-colors"
          >
            <span>📷</span>
            <span>{showEvidence ? "▲" : "▼"} {t.viewEvidence}</span>
          </button>
          {showEvidence && (
            <div className="mt-3 rounded-xl overflow-hidden border border-purple-500/30 bg-slate-950">
              <img
                src={alert.cctvThumbnailUrl}
                alt="CCTV Evidence"
                className="w-full object-cover max-h-52"
              />
              <div className="px-4 py-3 flex items-center justify-between text-xs font-mono">
                <div className="flex gap-4">
                  <span className="text-slate-400">
                    {t.itemsDetected}:{" "}
                    <span className="text-orange-400 font-bold">{alert.visualItemCount}</span>
                  </span>
                  <span className="text-slate-400">
                    {t.confidence}:{" "}
                    <span className="text-green-400 font-bold">
                      {Math.round((alert.confidenceScore ?? 0) * 100)}%
                    </span>
                  </span>
                </div>
                {alert.cctvCapturedAt && (
                  <span className="text-slate-500">
                    {new Date(alert.cctvCapturedAt).toLocaleTimeString("id-ID")}
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      {alert.status === "NEW" && (
        <div className="flex gap-2 pt-1">
          <button
            onClick={() => onResolve(alert.id)}
            className="px-4 py-1.5 bg-green-500/10 border border-green-500/30 text-green-400 text-xs rounded-lg hover:bg-green-500/20 transition-all font-medium"
          >
            ✓ {t.markResolved}
          </button>
        </div>
      )}
    </div>
  );
}

// ── Main Dashboard ────────────────────────────────────────────

export default function ClientDashboard() {
  const { language }    = useLanguage();
  const { user, logout } = useAuth();
  const [, setLocation] = useLocation();
  const lang = (language ?? "id") as "id" | "en";
  const t    = T[lang];

  const [kpi,     setKpi]     = useState<KPIData>(MOCK_KPI);
  const [alerts,  setAlerts]  = useState<FraudAlert[]>(MOCK_ALERTS);
  const [creds]               = useState<ClientCredential>(MOCK_CREDENTIALS);
  const [copied,  setCopied]  = useState(false);
  const [filter,  setFilter]  = useState<"ALL" | "NEW" | "CRITICAL">("ALL");
  const [activeNav, setActiveNav] = useState("dashboard");

  // Simulate live KPI updates
  useEffect(() => {
    const interval = setInterval(() => {
      setKpi((k) => ({
        ...k,
        lastSync: new Date().toISOString(),
        totalTransactions: k.totalTransactions + Math.floor(Math.random() * 3),
      }));
    }, 30_000);
    return () => clearInterval(interval);
  }, []);

  const handleCopyUserId = () => {
    navigator.clipboard.writeText(creds.userId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleResolve = (id: number) => {
    setAlerts((prev) =>
      prev.map((a) => a.id === id ? { ...a, status: "RESOLVED" as AlertStatus } : a)
    );
  };

  const filteredAlerts = alerts.filter((a) => {
    if (filter === "NEW")      return a.status === "NEW";
    if (filter === "CRITICAL") return a.severity === "CRITICAL";
    return true;
  });

  const newCount      = alerts.filter((a) => a.status === "NEW").length;
  const criticalCount = alerts.filter((a) => a.severity === "CRITICAL").length;

  // ── Nav items ─────────────────────────────────────────────

  const navItems = [
    { id: "dashboard",    icon: "⚡", label: t.dashboard },
    { id: "transactions", icon: "📊", label: t.transactions },
    { id: "agents",       icon: "🤖", label: t.agentStatus },
  ];

  // ─────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col">

      {/* ── Top Nav ─────────────────────────────────────────── */}
      <header className="sticky top-0 z-50 bg-slate-950/95 backdrop-blur-md border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 text-xs font-bold">
              VG
            </div>
            <div>
              <div className="text-sm font-bold">V<span className="text-cyan-400">Guard</span> AI</div>
              <div className="text-xs text-slate-500">{t.portal}</div>
            </div>
          </div>

          {/* Nav */}
          <nav className="hidden sm:flex items-center gap-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveNav(item.id)}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeNav === item.id
                    ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                }`}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </button>
            ))}
          </nav>

          {/* Right: tier badge + alerts + user */}
          <div className="flex items-center gap-3">
            {/* Alert count */}
            {newCount > 0 && (
              <div className="flex items-center gap-1.5 px-3 py-1.5 bg-red-500/10 border border-red-500/30 rounded-lg">
                <div className="w-2 h-2 rounded-full bg-red-400 animate-pulse" />
                <span className="text-red-400 text-xs font-bold">{newCount}</span>
              </div>
            )}

            {/* Tier badge */}
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-amber-500/10 border border-amber-500/30 rounded-lg">
              <span className="text-amber-400 text-xs font-bold">👑 {creds.tier}</span>
            </div>

            {/* Logout */}
            <button
              onClick={() => { logout?.(); setLocation("/home"); }}
              className="px-3 py-1.5 rounded-lg border border-slate-700 text-slate-400 hover:text-white hover:border-slate-500 text-xs font-medium transition-all"
            >
              {t.logout}
            </button>
          </div>
        </div>
      </header>

      {/* ── Main Content ─────────────────────────────────────── */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-8 space-y-8">

        {/* Welcome */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-2xl font-black">
              {t.welcome}, <span className="text-cyan-400">{user?.businessName ?? "Klien"}</span> 👋
            </h1>
            <div className="flex items-center gap-2 mt-1">
              <div className={`w-2 h-2 rounded-full ${kpi.systemStatus === "ONLINE" ? "bg-green-400 animate-pulse" : "bg-red-400"}`} />
              <span className="text-sm text-slate-400">
                {kpi.systemStatus === "ONLINE" ? t.systemOnline : t.systemOffline}
                {" · "}{t.lastSync}{" "}
                {new Date(kpi.lastSync).toLocaleTimeString(lang === "id" ? "id-ID" : "en-US")}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="px-3 py-1.5 bg-amber-500/10 border border-amber-500/30 rounded-lg">
              <span className="text-xs text-amber-400 font-bold">👑 {creds.packageName}</span>
            </div>
            <div className="px-3 py-1.5 bg-slate-800 border border-slate-700 rounded-lg">
              <span className="text-xs text-slate-400">{t.expiry}: <span className="text-white">{creds.expiresAt}</span></span>
            </div>
          </div>
        </div>

        {/* ── KPI Grid ──────────────────────────────────────── */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          <KPICard icon="💰" label={t.omset}        value={`Rp ${formatRupiah(kpi.totalOmset)}`}    accent="cyan"   />
          <KPICard icon="🧾" label={t.transactions} value={kpi.totalTransactions.toLocaleString()}  accent="blue"   />
          <KPICard icon="⚠️" label={t.anomalies}    value={kpi.totalAnomalies.toString()}            accent="orange" />
          <KPICard icon="👷" label={t.cashiers}     value={kpi.activeCashiers.toString()}            />
          <KPICard icon="🔔" label={t.alertsToday}  value={kpi.alertsToday.toString()}               accent="red"    />
          <KPICard icon="🛡️" label={t.prevented}    value={`Rp ${formatRupiah(kpi.preventedLoss)}`} accent="green"  />
        </div>

        {/* ── Two-column layout ─────────────────────────────── */}
        <div className="grid lg:grid-cols-3 gap-6">

          {/* ── Fraud Alert Feed (col 2/3) ─────────────────── */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <h2 className="text-lg font-bold">🔔 {t.alertFeed}</h2>
              <div className="flex items-center gap-2">
                {([
                  ["ALL",      t.filterAll,      null         ],
                  ["NEW",      t.filterNew,      newCount     ],
                  ["CRITICAL", t.filterCritical, criticalCount],
                ] as [string, string, number | null][]).map(([key, label, count]) => (
                  <button
                    key={key}
                    onClick={() => setFilter(key as typeof filter)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                      filter === key
                        ? "bg-cyan-500/10 border-cyan-500/30 text-cyan-400"
                        : "border-slate-700 text-slate-400 hover:border-slate-600"
                    }`}
                  >
                    {label}
                    {count !== null && count > 0 && (
                      <span className={`w-4 h-4 rounded-full text-[10px] flex items-center justify-center ${filter === key ? "bg-cyan-500 text-slate-950" : "bg-slate-700 text-slate-300"}`}>
                        {count}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              {filteredAlerts.length > 0 ? (
                filteredAlerts.map((alert) => (
                  <AlertCard
                    key={alert.id}
                    alert={alert}
                    lang={lang}
                    onResolve={handleResolve}
                  />
                ))
              ) : (
                <div className="py-16 text-center text-slate-500 bg-slate-900/40 rounded-2xl border border-slate-800">
                  <div className="text-4xl mb-3">✅</div>
                  <p className="text-sm">{t.noAlerts}</p>
                </div>
              )}
            </div>
          </div>

          {/* ── Right Panel ───────────────────────────────── */}
          <div className="space-y-5">

            {/* Credentials Card */}
            <div className="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-5 space-y-4 backdrop-blur-sm">
              <h3 className="text-base font-bold">🔑 {t.credentials}</h3>

              {/* User ID */}
              <div className="bg-slate-800 rounded-xl p-3 space-y-1">
                <div className="text-xs text-slate-400">{t.userId}</div>
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-cyan-400 font-bold tracking-wider">{creds.userId}</span>
                  <button
                    onClick={handleCopyUserId}
                    className="px-2.5 py-1 bg-slate-700 hover:bg-slate-600 text-xs rounded-lg transition-all font-medium"
                  >
                    {copied ? `✅ ${t.copied}` : t.copyId}
                  </button>
                </div>
              </div>

              {/* Tier */}
              <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-3 space-y-1">
                <div className="text-xs text-slate-400">{t.tierBadge}</div>
                <div className="flex items-center justify-between">
                  <span className="text-amber-400 font-bold">👑 {creds.packageName}</span>
                  <span className="text-xs text-slate-500 font-mono">{creds.pluginVersion}</span>
                </div>
              </div>

              {/* Plugin Download */}
              <a
                href={creds.pluginLink}
                download
                className="flex items-center justify-center gap-2 w-full py-3 bg-cyan-500 hover:bg-cyan-600 text-slate-950 font-bold rounded-xl text-sm transition-all active:scale-95 shadow-[0_0_20px_rgba(34,211,238,0.25)]"
              >
                ⬇️ {t.downloadPlugin}
              </a>
            </div>

            {/* Agent Status Panel */}
            <div className="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-5 space-y-3 backdrop-blur-sm">
              <h3 className="text-base font-bold">🤖 {t.agentStatus}</h3>
              <div className="space-y-2">
                {AGENT_LIST.map((agent) => {
                  const isActive = agent.activeFor.includes(creds.tier);
                  return (
                    <div
                      key={agent.id}
                      className={`flex items-center justify-between px-3 py-2 rounded-lg ${
                        isActive ? "bg-green-500/5 border border-green-500/20" : "bg-slate-800/50 border border-slate-700/30"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span>{agent.icon}</span>
                        <span className={`text-sm font-medium ${isActive ? "text-white" : "text-slate-500"}`}>
                          {agent.name}
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        {isActive ? (
                          <>
                            <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                            <span className="text-green-400 text-xs font-mono">ON</span>
                          </>
                        ) : (
                          <>
                            <div className="w-1.5 h-1.5 rounded-full bg-slate-600" />
                            <span className="text-slate-600 text-xs font-mono">{agent.minTier}</span>
                          </>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Upgrade prompt for non-ULTRA */}
              {creds.tier !== "V-ULTRA" && (
                <div className="mt-2 p-3 bg-purple-950/30 border border-purple-500/30 rounded-xl">
                  <p className="text-xs text-purple-300 text-center">{t.upgradeNotice}</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ── Visionary Agent (V-ULTRA Only) ─────────────────── */}
        <TierGate requiredTier="V-ULTRA">
          <div className="bg-slate-900/60 border border-slate-700/50 rounded-2xl p-5 sm:p-6 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-xl">👁️</div>
              <div>
                <h2 className="text-lg font-bold">Visionary Agent — CCTV × POS Bridge</h2>
                <p className="text-xs text-slate-400 font-mono">Real-time · {creds.userId}</p>
              </div>
              <div className="ml-auto px-3 py-1 bg-green-500/10 border border-green-500/30 rounded-full flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                <span className="text-green-400 text-xs font-mono">LIVE</span>
              </div>
            </div>

            {/* Lazy-load VisionaryAgent component */}
            <div className="text-center py-12 text-slate-500 border border-dashed border-slate-700 rounded-xl">
              <div className="text-3xl mb-3">📷</div>
              <p className="text-sm">
                {lang === "id"
                  ? "VisionaryAgent akan mount di sini setelah WebSocket terhubung."
                  : "VisionaryAgent will mount here after WebSocket connects."}
              </p>
              <p className="text-xs mt-1 font-mono text-slate-600">
                {"<VisionaryAgent clientId={userId} />"}
              </p>
            </div>
            {/* Production: <VisionaryAgent clientId={creds.userId} /> */}
          </div>
        </TierGate>

      </main>

      {/* ── Footer ──────────────────────────────────────────── */}
      <footer className="border-t border-slate-800 py-4 px-6 text-center">
        <p className="text-xs text-slate-600">
          V-Guard AI v1.0.0 · {creds.userId} · {creds.tier}
          {" · "}© {new Date().getFullYear()} V-Guard AI
        </p>
      </footer>
    </div>
  );
}
