import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import datetime
import time
import json
import math

# ═══════════════════════════════════════════════════════════════════════════
# COLOR UTILITY — Plotly requires rgba(), not 8-digit hex
# ═══════════════════════════════════════════════════════════════════════════

def hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert #RRGGBB hex + alpha float (0–1) → 'rgba(R,G,B,A)' string.
    Works with any modern Plotly version that rejects 8-digit hex colors."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# ═══════════════════════════════════════════════════════════════════════════
# V-GUARD AI — Production-Ready SaaS Platform
# Version: 2.0.0 | Build: 2025
# Architecture: Multi-Tier SaaS + Bilingual + AI Intelligence Engine
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="V-GUARD AI — Business Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://vguard.ai/support',
        'About': 'V-GUARD AI — Elite Business Intelligence & Fraud Detection'
    }
)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: TRANSLATION ENGINE — Bilingual ID/EN
# ═══════════════════════════════════════════════════════════════════════════

TRANSLATIONS = {
    "en": {
        # --- GLOBAL ---
        "brand": "V-GUARD AI",
        "tagline": "Elite Business Intelligence & Fraud Detection",
        "language_label": "Language",
        "active_tier": "Active Tier",
        "navigate": "Navigate",
        "status": "System Status",
        "active": "Active",
        "locked": "Locked",
        "upgrade": "Upgrade Now",
        "upgrade_msg": "Upgrade your subscription to unlock this module.",
        "access_denied": "ACCESS DENIED",
        "logout": "Sign Out",
        "settings": "Settings",
        "support": "Support",
        # --- MENU ---
        "menu_dashboard": "Command Center",
        "menu_lite": "V-LITE Monitor",
        "menu_pro": "V-PRO Finance",
        "menu_sight": "V-SIGHT Visual AI",
        "menu_enterprise": "V-ENTERPRISE Corp",
        "menu_ultra": "V-ULTRA Strategy",
        "menu_chat": "AI Consultant",
        # --- DASHBOARD ---
        "dash_title": "GLOBAL COMMAND CENTER",
        "dash_subtitle": "Real-time business intelligence across all nodes",
        "active_nodes": "Active Nodes",
        "fraud_blocked": "Fraud Blocked",
        "revenue_saved": "Revenue Saved",
        "system_health": "System Health",
        "ai_activity": "Real-time AI Activity Feed",
        "threat_map": "Threat Detection Map",
        "recent_alerts": "Recent Alerts",
        "severity": "Severity",
        "location": "Location",
        "type": "Type",
        "time": "Time",
        "ai_insights": "AI Insights",
        "performance_score": "Performance Score",
        "agents_active": "AI Agents Active",
        "data_processed": "Data Processed Today",
        # --- V-LITE ---
        "lite_title": "V-LITE — Transaction Guard",
        "lite_desc": "Basic fraud detection and daily monitoring for SME businesses.",
        "daily_alerts": "Daily Alerts",
        "verified_trans": "Verified Transactions",
        "void_detected": "Void Detected",
        "normal_trans": "Normal Transactions",
        "suspicious": "Suspicious",
        "transaction_log": "Transaction Log",
        "trans_id": "Transaction ID",
        "amount": "Amount",
        "cashier": "Cashier",
        "flag": "Flag",
        "connection_ok": "AI Core connected — Local server synchronized.",
        # --- V-PRO ---
        "pro_title": "V-PRO — Finance Leakage Detector",
        "pro_desc": "Automated finance audit, bank statement AI, and leakage prevention.",
        "leakage_prevented": "Leakage Prevented",
        "audit_score": "Audit Health Score",
        "anomalies": "Anomalies Flagged",
        "bank_sync": "Bank Sync Status",
        "finance_trend": "Finance Leakage Trend",
        "expense_breakdown": "Expense Breakdown",
        "scan_bank": "Run AI Bank Scan",
        "scanning": "Scanning bank statements...",
        "scan_complete": "Scan complete — 3 anomalies detected.",
        # --- V-SIGHT ---
        "sight_title": "V-SIGHT — Visual Behavior Intelligence",
        "sight_desc": "CCTV-integrated AI behavior analysis and zone anomaly detection.",
        "camera_nodes": "Camera Nodes",
        "zones_monitored": "Zones Monitored",
        "anomaly_detected": "Anomaly Detected",
        "behavior_score": "Behavior Risk Score",
        "zone_map": "Zone Activity Map",
        "camera_feed": "Live Camera Feed Simulation",
        "heatmap": "Behavior Heatmap",
        # --- V-ENTERPRISE ---
        "ent_title": "V-ENTERPRISE — Corporate Intelligence",
        "ent_desc": "Multi-branch surveillance, regional fraud detection, and corporate BI.",
        "branches": "Active Branches",
        "total_revenue": "Total Group Revenue",
        "group_fraud": "Group Fraud Rate",
        "top_branch": "Top Performing Branch",
        "branch_compare": "Branch Performance Comparison",
        "regional_map": "Regional Intelligence Map",
        # --- V-ULTRA ---
        "ultra_title": "V-ULTRA — Strategic AI Command",
        "ultra_desc": "Investor-grade predictive analytics, expansion strategy, and AI forecasting.",
        "profit_score": "Profit Optimization Score",
        "market_forecast": "Market Expansion Forecast",
        "investor_report": "AI Investor Report",
        "roi_projection": "ROI Projection",
        "expansion_target": "Expansion Targets",
        "generate_report": "Generate AI Report",
        "generating": "AI generating strategic report...",
        # --- CHAT ---
        "chat_title": "AI Business Consultant",
        "chat_placeholder": "Ask about fraud, finance, or business strategy...",
        "chat_send": "Send",
        "chat_thinking": "V-GUARD AI is analyzing...",
        "chat_greeting": "Hello! I'm your V-GUARD AI Consultant. Ask me anything about fraud detection, financial anomalies, or business strategy.",
        # --- ALERTS ---
        "alert_void": "Void Transaction",
        "alert_duplicate": "Duplicate Entry",
        "alert_high_value": "High-Value Flag",
        "alert_after_hours": "After-Hours Activity",
        "alert_low": "LOW",
        "alert_medium": "MEDIUM",
        "alert_high": "HIGH",
        "alert_critical": "CRITICAL",
    },
    "id": {
        # --- GLOBAL ---
        "brand": "V-GUARD AI",
        "tagline": "Intelijen Bisnis Elite & Deteksi Kecurangan",
        "language_label": "Bahasa",
        "active_tier": "Paket Aktif",
        "navigate": "Navigasi",
        "status": "Status Sistem",
        "active": "Aktif",
        "locked": "Terkunci",
        "upgrade": "Upgrade Sekarang",
        "upgrade_msg": "Upgrade langganan Anda untuk membuka modul ini.",
        "access_denied": "AKSES DITOLAK",
        "logout": "Keluar",
        "settings": "Pengaturan",
        "support": "Dukungan",
        # --- MENU ---
        "menu_dashboard": "Pusat Komando",
        "menu_lite": "Monitor V-LITE",
        "menu_pro": "Keuangan V-PRO",
        "menu_sight": "Visual AI V-SIGHT",
        "menu_enterprise": "Korporat V-ENTERPRISE",
        "menu_ultra": "Strategi V-ULTRA",
        "menu_chat": "Konsultan AI",
        # --- DASHBOARD ---
        "dash_title": "PUSAT KOMANDO GLOBAL",
        "dash_subtitle": "Intelijen bisnis real-time di semua node",
        "active_nodes": "Node Aktif",
        "fraud_blocked": "Kecurangan Diblokir",
        "revenue_saved": "Pendapatan Diselamatkan",
        "system_health": "Kesehatan Sistem",
        "ai_activity": "Feed Aktivitas AI Real-time",
        "threat_map": "Peta Deteksi Ancaman",
        "recent_alerts": "Peringatan Terbaru",
        "severity": "Tingkat",
        "location": "Lokasi",
        "type": "Tipe",
        "time": "Waktu",
        "ai_insights": "Wawasan AI",
        "performance_score": "Skor Kinerja",
        "agents_active": "Agen AI Aktif",
        "data_processed": "Data Diproses Hari Ini",
        # --- V-LITE ---
        "lite_title": "V-LITE — Penjaga Transaksi",
        "lite_desc": "Deteksi kecurangan dasar dan pemantauan harian untuk bisnis UKM.",
        "daily_alerts": "Peringatan Harian",
        "verified_trans": "Transaksi Terverifikasi",
        "void_detected": "Void Terdeteksi",
        "normal_trans": "Transaksi Normal",
        "suspicious": "Mencurigakan",
        "transaction_log": "Log Transaksi",
        "trans_id": "ID Transaksi",
        "amount": "Jumlah",
        "cashier": "Kasir",
        "flag": "Flag",
        "connection_ok": "AI Core terhubung — Server lokal tersinkronisasi.",
        # --- V-PRO ---
        "pro_title": "V-PRO — Detektor Kebocoran Keuangan",
        "pro_desc": "Audit keuangan otomatis, AI rekening koran, dan pencegahan kebocoran.",
        "leakage_prevented": "Kebocoran Dicegah",
        "audit_score": "Skor Kesehatan Audit",
        "anomalies": "Anomali Ditandai",
        "bank_sync": "Status Sinkronisasi Bank",
        "finance_trend": "Tren Kebocoran Keuangan",
        "expense_breakdown": "Rincian Pengeluaran",
        "scan_bank": "Jalankan Pemindaian AI Bank",
        "scanning": "Memindai rekening koran...",
        "scan_complete": "Pemindaian selesai — 3 anomali terdeteksi.",
        # --- V-SIGHT ---
        "sight_title": "V-SIGHT — Intelijen Perilaku Visual",
        "sight_desc": "Analisis perilaku AI terintegrasi CCTV dan deteksi anomali zona.",
        "camera_nodes": "Node Kamera",
        "zones_monitored": "Zona Dipantau",
        "anomaly_detected": "Anomali Terdeteksi",
        "behavior_score": "Skor Risiko Perilaku",
        "zone_map": "Peta Aktivitas Zona",
        "camera_feed": "Simulasi Feed Kamera Live",
        "heatmap": "Heatmap Perilaku",
        # --- V-ENTERPRISE ---
        "ent_title": "V-ENTERPRISE — Intelijen Korporat",
        "ent_desc": "Pengawasan multi-cabang, deteksi kecurangan regional, dan BI korporat.",
        "branches": "Cabang Aktif",
        "total_revenue": "Total Pendapatan Grup",
        "group_fraud": "Tingkat Kecurangan Grup",
        "top_branch": "Cabang Terbaik",
        "branch_compare": "Perbandingan Kinerja Cabang",
        "regional_map": "Peta Intelijen Regional",
        # --- V-ULTRA ---
        "ultra_title": "V-ULTRA — Komando AI Strategis",
        "ultra_desc": "Analitik prediktif kelas investor, strategi ekspansi, dan prakiraan AI.",
        "profit_score": "Skor Optimasi Profit",
        "market_forecast": "Prakiraan Ekspansi Pasar",
        "investor_report": "Laporan Investor AI",
        "roi_projection": "Proyeksi ROI",
        "expansion_target": "Target Ekspansi",
        "generate_report": "Buat Laporan AI",
        "generating": "AI membuat laporan strategis...",
        # --- CHAT ---
        "chat_title": "Konsultan Bisnis AI",
        "chat_placeholder": "Tanya tentang kecurangan, keuangan, atau strategi bisnis...",
        "chat_send": "Kirim",
        "chat_thinking": "V-GUARD AI sedang menganalisis...",
        "chat_greeting": "Halo! Saya Konsultan V-GUARD AI Anda. Tanyakan apa saja tentang deteksi kecurangan, anomali keuangan, atau strategi bisnis.",
        # --- ALERTS ---
        "alert_void": "Transaksi Void",
        "alert_duplicate": "Entri Duplikat",
        "alert_high_value": "Flag Nilai Tinggi",
        "alert_after_hours": "Aktivitas Di Luar Jam",
        "alert_low": "RENDAH",
        "alert_medium": "SEDANG",
        "alert_high": "TINGGI",
        "alert_critical": "KRITIS",
    }
}

def t(key):
    """Translate a key based on active language session state."""
    lang = st.session_state.get("lang", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

TIERS = ["V-LITE", "V-PRO", "V-SIGHT", "V-ENTERPRISE", "V-ULTRA"]
TIER_COLORS = {
    "V-LITE": "#22C55E",
    "V-PRO": "#EAB308",
    "V-SIGHT": "#3B82F6",
    "V-ENTERPRISE": "#8B5CF6",
    "V-ULTRA": "#F43F5E"
}
TIER_ICONS = {
    "V-LITE": "🟢",
    "V-PRO": "🟡",
    "V-SIGHT": "🔵",
    "V-ENTERPRISE": "🟣",
    "V-ULTRA": "🔴"
}

defaults = {
    "tier": "V-LITE",
    "lang": "en",
    "chat_history": [],
    "show_chat": False,
    "scan_running": False,
    "report_generated": False,
    "active_page": "dashboard",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def has_access(required_tier):
    return TIERS.index(st.session_state.tier) >= TIERS.index(required_tier)

def tier_color():
    return TIER_COLORS.get(st.session_state.tier, "#00D1FF")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: GLOBAL CSS — SULTAN DARK UI ENGINE
# ═══════════════════════════════════════════════════════════════════════════

tc = tier_color()
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Syne:wght@700;800&display=swap');

:root {{
    --bg-primary: #050912;
    --bg-secondary: #0B1120;
    --bg-card: #0F1729;
    --bg-glass: rgba(15, 23, 41, 0.85);
    --accent: {tc};
    --accent-dim: {tc}33;
    --accent-glow: {tc}66;
    --text-primary: #E8EDF5;
    --text-secondary: #8B96A8;
    --text-muted: #4A5568;
    --border: rgba(255,255,255,0.06);
    --border-accent: {tc}44;
    --success: #22C55E;
    --warning: #F59E0B;
    --danger: #EF4444;
    --critical: #FF006E;
    --font-display: 'Syne', sans-serif;
    --font-body: 'Space Grotesk', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    --radius: 12px;
    --radius-lg: 20px;
    --shadow-glow: 0 0 30px {tc}22;
    --shadow-card: 0 4px 24px rgba(0,0,0,0.4);
}}

* {{ box-sizing: border-box; }}

/* ── CORE LAYOUT ── */
html, body, [data-testid="stAppViewContainer"] {{
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
}}

[data-testid="stAppViewContainer"]::before {{
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: 
        radial-gradient(ellipse 80% 50% at 20% 0%, {tc}08 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 100%, {tc}05 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}}

[data-testid="block-container"] {{
    padding: 1.5rem 2rem !important;
    max-width: 1600px;
}}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {{
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
    padding: 0 !important;
}}

[data-testid="stSidebar"] > div {{
    padding: 1.5rem 1rem !important;
}}

/* ── SIDEBAR BRANDING ── */
.sidebar-brand {{
    text-align: center;
    padding: 1.5rem 1rem 1rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}}
.sidebar-brand .logo {{
    font-family: var(--font-display);
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: var(--accent);
    text-shadow: 0 0 20px var(--accent-glow);
}}
.sidebar-brand .sub {{
    font-size: 0.7rem;
    color: var(--text-muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 2px;
}}
.tier-badge {{
    display: inline-block;
    background: var(--accent-dim);
    border: 1px solid var(--accent);
    color: var(--accent);
    font-family: var(--font-mono);
    font-size: 0.7rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    margin-top: 8px;
    letter-spacing: 1px;
}}

/* ── METRICS ── */
[data-testid="metric-container"] {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border-accent) !important;
    border-radius: var(--radius) !important;
    padding: 1.2rem 1.5rem !important;
    box-shadow: var(--shadow-card), var(--shadow-glow) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}}
[data-testid="metric-container"]:hover {{
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-card), 0 0 40px var(--accent-glow) !important;
}}
[data-testid="stMetricLabel"] {{
    color: var(--text-secondary) !important;
    font-size: 0.75rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    font-family: var(--font-mono) !important;
}}
[data-testid="stMetricValue"] {{
    color: var(--text-primary) !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    font-family: var(--font-display) !important;
}}
[data-testid="stMetricDelta"] {{
    font-size: 0.8rem !important;
    font-family: var(--font-mono) !important;
}}

/* ── BUTTONS ── */
.stButton > button {{
    background: linear-gradient(135deg, var(--accent), var(--accent)cc) !important;
    color: #000 !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.6rem 1.5rem !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px var(--accent-glow) !important;
    width: 100% !important;
}}
.stButton > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px var(--accent-glow) !important;
    filter: brightness(1.1) !important;
}}

/* ── SELECTBOX ── */
[data-testid="stSelectbox"] > div > div {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border-accent) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
}}

/* ── TEXT INPUTS ── */
[data-testid="stTextInput"] > div > div > input,
[data-testid="stTextArea"] > div > div > textarea {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border-accent) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    padding: 0.7rem 1rem !important;
}}
[data-testid="stTextInput"] > div > div > input:focus,
[data-testid="stTextArea"] > div > div > textarea:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 15px var(--accent-dim) !important;
}}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {{
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
}}
.stDataFrame th {{
    background: var(--bg-secondary) !important;
    color: var(--accent) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.75rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}}
.stDataFrame td {{
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.8rem !important;
    border-color: var(--border) !important;
}}

/* ── ALERTS & INFO BOXES ── */
[data-testid="stAlert"] {{
    border-radius: var(--radius) !important;
    border: 1px solid !important;
    font-family: var(--font-body) !important;
    font-size: 0.85rem !important;
}}

/* ── HEADERS ── */
h1 {{
    font-family: var(--font-display) !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: var(--text-primary) !important;
    letter-spacing: -1px !important;
    line-height: 1.1 !important;
}}
h2 {{
    font-family: var(--font-display) !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: var(--accent) !important;
    letter-spacing: -0.5px !important;
}}
h3 {{
    font-family: var(--font-body) !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}}

/* ── RADIO (SIDEBAR NAV) ── */
[data-testid="stRadio"] > div {{
    gap: 4px !important;
    flex-direction: column !important;
}}
[data-testid="stRadio"] label {{
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: var(--radius) !important;
    padding: 8px 12px !important;
    font-family: var(--font-body) !important;
    font-size: 0.85rem !important;
    color: var(--text-secondary) !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    width: 100% !important;
}}
[data-testid="stRadio"] label:hover {{
    background: var(--accent-dim) !important;
    border-color: var(--border-accent) !important;
    color: var(--text-primary) !important;
}}
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {{
    color: inherit !important;
    margin: 0 !important;
}}

/* ── PROGRESS BAR ── */
[data-testid="stProgress"] > div > div {{
    background: linear-gradient(90deg, var(--accent), var(--accent-glow)) !important;
    border-radius: 99px !important;
}}
[data-testid="stProgress"] > div {{
    background: var(--bg-secondary) !important;
    border-radius: 99px !important;
    height: 6px !important;
}}

/* ── DIVIDER ── */
hr {{ border-color: var(--border) !important; margin: 1.5rem 0 !important; }}

/* ── CARD COMPONENT ── */
.vg-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    box-shadow: var(--shadow-card);
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}}
.vg-card:hover {{
    border-color: var(--border-accent);
    box-shadow: var(--shadow-card), var(--shadow-glow);
}}
.vg-card-title {{
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--accent);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}}

/* ── PAGE HEADER ── */
.page-header {{
    padding: 1.5rem 0 1rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}}
.page-header h1 {{
    margin: 0 0 0.3rem !important;
}}
.page-header .desc {{
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin: 0;
}}

/* ── STATUS BADGE ── */
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 99px;
    font-family: var(--font-mono);
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}}
.badge-success {{ background: #22C55E22; border: 1px solid #22C55E66; color: #22C55E; }}
.badge-warning {{ background: #F59E0B22; border: 1px solid #F59E0B66; color: #F59E0B; }}
.badge-danger  {{ background: #EF444422; border: 1px solid #EF444466; color: #EF4444; }}
.badge-critical {{ background: #FF006E22; border: 1px solid #FF006E66; color: #FF006E; animation: pulse-critical 1.5s infinite; }}
.badge-info    {{ background: var(--accent-dim); border: 1px solid var(--border-accent); color: var(--accent); }}

@keyframes pulse-critical {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.6; }}
}}

/* ── LOCK SCREEN ── */
.lock-screen {{
    text-align: center;
    padding: 4rem 2rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    margin: 2rem 0;
}}
.lock-icon {{
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.6;
}}
.lock-title {{
    font-family: var(--font-display);
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}}
.lock-desc {{
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-bottom: 2rem;
}}

/* ── FLOATING CHAT WIDGET ── */
.chat-fab {{
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent), var(--accent)aa);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    cursor: pointer;
    z-index: 9999;
    box-shadow: 0 8px 25px var(--accent-glow);
    border: 2px solid var(--accent-glow);
    animation: float-bob 3s ease-in-out infinite;
    transition: transform 0.2s ease;
}}
.chat-fab:hover {{ transform: scale(1.1); }}
@keyframes float-bob {{
    0%, 100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(-6px); }}
}}

/* ── CHAT BUBBLE ── */
.chat-msg-user {{
    background: var(--accent-dim);
    border: 1px solid var(--accent);
    border-radius: 12px 12px 4px 12px;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 0.85rem;
    max-width: 80%;
    margin-left: auto;
    color: var(--text-primary);
    font-family: var(--font-body);
}}
.chat-msg-ai {{
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px 12px 12px 4px;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 0.85rem;
    max-width: 85%;
    color: var(--text-primary);
    font-family: var(--font-body);
}}
.chat-ai-label {{
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--accent);
    letter-spacing: 1px;
    margin-bottom: 4px;
}}
.chat-container {{
    max-height: 350px;
    overflow-y: auto;
    padding: 1rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    margin: 1rem 0;
    scrollbar-width: thin;
    scrollbar-color: var(--accent-dim) transparent;
}}

/* ── HEATMAP GRID ── */
.heatmap-grid {{
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    gap: 3px;
    padding: 1rem;
    background: var(--bg-secondary);
    border-radius: var(--radius);
}}
.heatmap-cell {{
    height: 28px;
    border-radius: 4px;
    transition: all 0.3s ease;
}}
.heatmap-cell:hover {{ transform: scale(1.2); z-index: 10; }}

/* ── SEPARATOR ── */
.section-sep {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 1.5rem 0;
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 2px;
    text-transform: uppercase;
}}
.section-sep::before, .section-sep::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}}

/* ── SCROLLBAR ── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: var(--bg-primary); }}
::-webkit-scrollbar-thumb {{ background: var(--accent-dim); border-radius: 99px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--accent); }}

/* ── PLOTLY CHART CONTAINER ── */
[data-testid="stPlotlyChart"] {{
    border-radius: var(--radius) !important;
    overflow: hidden !important;
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
}}

/* ── EXPANDER ── */
[data-testid="stExpander"] {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}}
[data-testid="stExpander"] summary {{
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
}}

/* ── SIDEBAR SELECTBOX ── */
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {{
    background: var(--bg-card) !important;
    border-color: var(--border-accent) !important;
    font-size: 0.85rem !important;
}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: PLOTLY CHART THEME
# ═══════════════════════════════════════════════════════════════════════════

def chart_layout(title="", height=300):
    tc = tier_color()
    return dict(
        plot_bgcolor='rgba(11,17,32,0)',
        paper_bgcolor='rgba(11,17,32,0)',
        font=dict(family='Space Grotesk, sans-serif', color='#8B96A8', size=11),
        title=dict(text=title, font=dict(family='Syne, sans-serif', size=14, color='#E8EDF5'), x=0.02, pad=dict(b=10)),
        xaxis=dict(gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.06)', tickfont=dict(size=10)),
        yaxis=dict(gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.06)', tickfont=dict(size=10)),
        margin=dict(l=40, r=20, t=50, b=30),
        height=height,
        legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='rgba(255,255,255,0.06)', font=dict(size=10))
    )

def accent_color_scale():
    tc = tier_color()
    return [[0, '#050912'], [0.5, hex_to_rgba(tc, 0.4)], [1, tc]]

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: SAMPLE DATA GENERATORS
# ═══════════════════════════════════════════════════════════════════════════

def gen_transactions(n=20):
    random.seed(42)
    flags = [t("alert_void"), t("alert_duplicate"), "✅ OK", "✅ OK", "✅ OK",
             t("alert_high_value"), "✅ OK", t("alert_after_hours")]
    cashiers = ["Rina", "Budi", "Siti", "Dewi", "Ahmad"]
    now = datetime.datetime.now()
    rows = []
    for i in range(n):
        rows.append({
            t("trans_id"): f"TXN-{random.randint(10000,99999)}",
            t("amount"): f"Rp {random.randint(20, 2500) * 1000:,}",
            t("cashier"): random.choice(cashiers),
            t("flag"): random.choice(flags),
            t("time"): (now - datetime.timedelta(minutes=random.randint(0, 480))).strftime("%H:%M"),
        })
    return pd.DataFrame(rows)

def gen_finance_trend(months=12):
    months_en = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    months_id = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]
    m_labels = months_id if st.session_state.lang == "id" else months_en
    base = [15, 22, 18, 30, 25, 40, 35, 28, 45, 38, 52, 48]
    detected = [12, 18, 15, 25, 22, 35, 30, 24, 40, 33, 47, 44]
    return pd.DataFrame({
        t("time"): m_labels,
        "Leakage (Juta Rp)": base,
        "Detected": detected
    })

def gen_branch_data():
    branches = ["Jakarta Pusat","Surabaya","Bandung","Medan","Makassar","Bali","Semarang","Palembang"]
    return pd.DataFrame({
        t("location"): branches,
        "Revenue (M)": [random.randint(80,250) for _ in branches],
        "Fraud Rate (%)": [round(random.uniform(0.5, 4.5), 1) for _ in branches],
        "Score": [random.randint(70, 99) for _ in branches],
    })

def gen_roi_projection():
    quarters = ["Q1 2024","Q2 2024","Q3 2024","Q4 2024","Q1 2025","Q2 2025","Q3 2025","Q4 2025"]
    base = [120, 145, 180, 220, 280, 350, 430, 520]
    optimized = [b * random.uniform(1.15, 1.35) for b in base]
    return pd.DataFrame({
        "Quarter": quarters,
        "Baseline (M)": base,
        "AI-Optimized (M)": [round(o) for o in optimized]
    })

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: AI CHAT ENGINE (MOCK — ready for Claude API hook)
# ═══════════════════════════════════════════════════════════════════════════

AI_RESPONSES = {
    "en": [
        "Based on your transaction data, I detect a 3.2% void rate this week — above the 2% industry benchmark. I recommend reviewing cashier activity during the 14:00–16:00 window.",
        "Your finance audit shows Rp 4.2M in unmatched bank entries over the last 30 days. This is a common leakage pattern — likely in petty cash or supplier payments.",
        "V-GUARD AI predicts a 15% revenue increase if you activate the V-PRO Finance module for automated reconciliation.",
        "Anomaly detected: 3 high-value transactions were processed outside business hours. This pattern matches internal fraud signatures with 87% confidence.",
        "Your system health is excellent at 99.8%. I recommend scheduling a full audit report for your next board meeting.",
    ],
    "id": [
        "Berdasarkan data transaksi Anda, saya mendeteksi tingkat void 3,2% minggu ini — di atas benchmark industri 2%. Saya sarankan meninjau aktivitas kasir pada jam 14:00–16:00.",
        "Audit keuangan Anda menunjukkan Rp 4,2 Juta entri bank yang tidak cocok dalam 30 hari terakhir. Ini pola kebocoran umum — kemungkinan di kas kecil atau pembayaran supplier.",
        "V-GUARD AI memprediksi peningkatan pendapatan 15% jika Anda mengaktifkan modul Keuangan V-PRO untuk rekonsiliasi otomatis.",
        "Anomali terdeteksi: 3 transaksi bernilai tinggi diproses di luar jam kerja. Pola ini cocok dengan tanda tangan penipuan internal dengan keyakinan 87%.",
        "Kesehatan sistem Anda sangat baik di 99,8%. Saya sarankan menjadwalkan laporan audit lengkap untuk rapat direksi berikutnya.",
    ]
}

def get_ai_response():
    lang = st.session_state.get("lang", "en")
    return random.choice(AI_RESPONSES.get(lang, AI_RESPONSES["en"]))

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: SIDEBAR LAYOUT
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    # BRANDING
    tc = tier_color()
    icon = TIER_ICONS.get(st.session_state.tier, "🛡️")
    st.markdown(f"""
    <div class="sidebar-brand">
        <div class="logo">🛡️ V-GUARD AI</div>
        <div class="sub">Elite Intelligence Platform</div>
        <div class="tier-badge">{icon} {st.session_state.tier}</div>
    </div>
    """, unsafe_allow_html=True)

    # LANGUAGE TOGGLE
    lang_opts = ["🇬🇧 English", "🇮🇩 Indonesia"]
    lang_map = {"🇬🇧 English": "en", "🇮🇩 Indonesia": "id"}
    lang_reverse = {"en": "🇬🇧 English", "id": "🇮🇩 Indonesia"}
    selected_lang = st.selectbox(
        t("language_label"),
        lang_opts,
        index=lang_opts.index(lang_reverse[st.session_state.lang]),
        key="lang_select"
    )
    st.session_state.lang = lang_map[selected_lang]

    # TIER SELECTOR
    tier_display = [f"{TIER_ICONS[t2]} {t2}" for t2 in TIERS]
    tier_map = {f"{TIER_ICONS[t2]} {t2}": t2 for t2 in TIERS}
    tier_rev = {t2: f"{TIER_ICONS[t2]} {t2}" for t2 in TIERS}
    selected_tier_disp = st.selectbox(
        t("active_tier"),
        tier_display,
        index=TIERS.index(st.session_state.tier),
        key="tier_select"
    )
    st.session_state.tier = tier_map[selected_tier_disp]

    st.markdown("---")

    # NAVIGATION
    st.markdown(f"<p style='font-size:0.7rem;color:var(--text-muted);letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;font-family:var(--font-mono)'>{t('navigate')}</p>", unsafe_allow_html=True)

    nav_options = [
        f"⬛ {t('menu_dashboard')}",
        f"🟢 {t('menu_lite')}",
        f"🟡 {t('menu_pro')}",
        f"🔵 {t('menu_sight')}",
        f"🟣 {t('menu_enterprise')}",
        f"🔴 {t('menu_ultra')}",
        f"💬 {t('menu_chat')}",
    ]
    menu = st.radio("", nav_options, label_visibility="collapsed")

    st.markdown("---")

    # SYSTEM STATUS
    st.markdown(f"""
    <div class="vg-card" style="padding:1rem">
        <div class="vg-card-title">{t('status')}</div>
        <div style="display:flex;flex-direction:column;gap:6px;margin-top:8px">
            <div style="display:flex;justify-content:space-between;font-size:0.78rem">
                <span style="color:var(--text-secondary)">AI Engine</span>
                <span class="badge badge-success">● Online</span>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.78rem">
                <span style="color:var(--text-secondary)">DB Sync</span>
                <span class="badge badge-success">● Synced</span>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.78rem">
                <span style="color:var(--text-secondary)">Cloud</span>
                <span class="badge badge-info">● {t('active')}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # FOOTER
    st.markdown(f"""
    <div style="margin-top:auto;padding-top:1rem;text-align:center">
        <p style="font-size:0.65rem;color:var(--text-muted);font-family:var(--font-mono)">
            V-GUARD AI v2.0 · Build 2025<br>
            © 2025 V-Guard Technologies
        </p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 8: PAGE ROUTING
# ═══════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────
# PAGE A: COMMAND CENTER DASHBOARD
# ─────────────────────────────────────────────
if t('menu_dashboard') in menu:
    st.markdown(f"""
    <div class="page-header">
        <h1>🛡️ {t('dash_title')}</h1>
        <p class="desc">{t('dash_subtitle')}</p>
    </div>
    """, unsafe_allow_html=True)

    # KPI ROW
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(t("active_nodes"), "1,284", "+12")
    c2.metric(t("fraud_blocked"), "312", "99%")
    c3.metric(t("revenue_saved"), "Rp 42.5M", "+15%")
    c4.metric(t("system_health"), "99.8%", "Stable")
    c5.metric(t("agents_active"), "10 / 10", "All Online")

    st.markdown(f'<div class="section-sep">{t("ai_activity")}</div>', unsafe_allow_html=True)

    col_chart, col_alerts = st.columns([3, 2])

    with col_chart:
        # REAL-TIME ACTIVITY CHART
        tc = tier_color()
        hours = [f"{i:02d}:00" for i in range(24)]
        threats = [random.randint(5, 80) for _ in hours]
        resolved = [max(0, t2 - random.randint(0, 10)) for t2 in threats]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hours, y=threats, name="Threats Detected",
            fill='tozeroy', line=dict(color=tc, width=2),
            fillcolor=hex_to_rgba(tc, 0.13), mode='lines'
        ))
        fig.add_trace(go.Scatter(
            x=hours, y=resolved, name="Resolved",
            line=dict(color='#22C55E', width=1.5, dash='dot'),
            mode='lines'
        ))
        fig.update_layout(**chart_layout(t("ai_activity"), height=280))
        st.plotly_chart(fig, use_container_width=True)

    with col_alerts:
        st.markdown(f"#### {t('recent_alerts')}")
        alert_data = [
            {"type": t("alert_void"), "loc": "Surabaya", "sev": "HIGH", "time": "14:32"},
            {"type": t("alert_duplicate"), "loc": "Jakarta", "sev": "MEDIUM", "time": "13:15"},
            {"type": t("alert_after_hours"), "loc": "Bandung", "sev": "CRITICAL", "time": "02:44"},
            {"type": t("alert_high_value"), "loc": "Medan", "sev": "HIGH", "time": "11:08"},
            {"type": t("alert_void"), "loc": "Bali", "sev": "LOW", "time": "09:52"},
        ]
        sev_badge = {
            "CRITICAL": "badge-critical",
            "HIGH": "badge-danger",
            "MEDIUM": "badge-warning",
            "LOW": "badge-success"
        }
        sev_label = {
            "CRITICAL": t("alert_critical"),
            "HIGH": t("alert_high"),
            "MEDIUM": t("alert_medium"),
            "LOW": t("alert_low"),
        }
        for a in alert_data:
            badge_class = sev_badge.get(a["sev"], "badge-info")
            label = sev_label.get(a["sev"], a["sev"])
            st.markdown(f"""
            <div class="vg-card" style="padding:0.8rem 1rem;margin-bottom:0.5rem">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                        <div style="font-size:0.82rem;font-weight:600;color:var(--text-primary)">{a['type']}</div>
                        <div style="font-size:0.72rem;color:var(--text-muted);font-family:var(--font-mono)">{a['loc']} · {a['time']}</div>
                    </div>
                    <span class="badge {badge_class}">{label}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f'<div class="section-sep">{t("ai_insights")}</div>', unsafe_allow_html=True)

    col_donut, col_bar, col_gauge = st.columns(3)

    with col_donut:
        tc = tier_color()
        fig_d = go.Figure(go.Pie(
            values=[312, 28, 8, 4],
            labels=["Resolved", "Investigating", "False Positive", "Critical"],
            hole=0.65,
            marker=dict(colors=[tc, '#F59E0B', '#22C55E', '#EF4444']),
            textfont=dict(size=10),
            hoverinfo='label+percent'
        ))
        fig_d.add_annotation(text="Total<br><b>352</b>", x=0.5, y=0.5,
                             font=dict(size=12, color='#E8EDF5', family='Syne'), showarrow=False)
        fig_d.update_layout(**chart_layout(t("fraud_blocked"), height=240))
        st.plotly_chart(fig_d, use_container_width=True)

    with col_bar:
        tc = tier_color()
        agents = ["Liaison", "Vision", "Finance", "Pattern", "Predictor"]
        scores = [98, 94, 97, 91, 88]
        fig_b = go.Figure(go.Bar(
            x=scores, y=agents, orientation='h',
            marker=dict(
                color=scores,
                colorscale=[[0, hex_to_rgba(tc, 0.33)], [1, tc]],
                showscale=False
            ),
            text=[f"{s}%" for s in scores],
            textposition='inside',
            textfont=dict(size=10, color='#000')
        ))
        fig_b.update_layout(**chart_layout(t("agents_active"), height=240))
        st.plotly_chart(fig_b, use_container_width=True)

    with col_gauge:
        tc = tier_color()
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=99.8,
            number=dict(suffix="%", font=dict(family='Syne', size=32, color='#E8EDF5')),
            gauge=dict(
                axis=dict(range=[0, 100], tickfont=dict(size=9, color='#8B96A8')),
                bar=dict(color=tc, thickness=0.7),
                bgcolor='rgba(0,0,0,0)',
                bordercolor='rgba(255,255,255,0.06)',
                steps=[
                    dict(range=[0, 60], color='#EF444422'),
                    dict(range=[60, 85], color='#F59E0B22'),
                    dict(range=[85, 100], color='#22C55E22')
                ]
            ),
            title=dict(text=t("system_health"), font=dict(family='Space Grotesk', size=12, color='#8B96A8'))
        ))
        fig_g.update_layout(**chart_layout("", height=240))
        st.plotly_chart(fig_g, use_container_width=True)


# ─────────────────────────────────────────────
# PAGE B: V-LITE MONITORING
# ─────────────────────────────────────────────
elif t('menu_lite') in menu:
    st.markdown(f"""
    <div class="page-header">
        <h1>🟢 {t('lite_title')}</h1>
        <p class="desc">{t('lite_desc')}</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("daily_alerts"), random.randint(5, 20), "+3")
    c2.metric(t("verified_trans"), "842", "99.6%")
    c3.metric(t("void_detected"), "7", "-2")
    c4.metric(t("suspicious"), "3", "High")

    st.success(f"✔ {t('connection_ok')}")

    col_tx, col_chart = st.columns([2, 3])

    with col_tx:
        st.markdown(f"#### {t('transaction_log')}")
        df = gen_transactions(12)
        flag_col = t("flag")

        def colorize_flag(val):
            if "OK" in str(val): return f'<span class="badge badge-success">{val}</span>'
            elif t("alert_void") in str(val) or t("alert_duplicate") in str(val):
                return f'<span class="badge badge-danger">{val}</span>'
            elif t("alert_high_value") in str(val): return f'<span class="badge badge-warning">{val}</span>'
            elif t("alert_after_hours") in str(val): return f'<span class="badge badge-critical">{val}</span>'
            return val

        html_rows = ""
        for _, row in df.iterrows():
            html_rows += f"""
            <tr>
                <td style="font-family:var(--font-mono);font-size:0.75rem;color:var(--text-muted)">{row[t('trans_id')]}</td>
                <td style="font-size:0.8rem;color:var(--text-primary)">{row[t('amount')]}</td>
                <td style="font-size:0.8rem;color:var(--text-secondary)">{row[t('cashier')]}</td>
                <td>{colorize_flag(row[t('flag')])}</td>
                <td style="font-family:var(--font-mono);font-size:0.75rem;color:var(--text-muted)">{row[t('time')]}</td>
            </tr>"""

        st.markdown(f"""
        <div class="vg-card" style="padding:0">
            <table style="width:100%;border-collapse:collapse">
                <thead>
                    <tr style="background:var(--bg-secondary)">
                        <th style="padding:8px 12px;text-align:left;font-family:var(--font-mono);font-size:0.65rem;color:var(--accent);letter-spacing:1.5px;border-bottom:1px solid var(--border)">{t('trans_id').upper()}</th>
                        <th style="padding:8px 12px;text-align:left;font-family:var(--font-mono);font-size:0.65rem;color:var(--accent);letter-spacing:1.5px;border-bottom:1px solid var(--border)">{t('amount').upper()}</th>
                        <th style="padding:8px 12px;text-align:left;font-family:var(--font-mono);font-size:0.65rem;color:var(--accent);letter-spacing:1.5px;border-bottom:1px solid var(--border)">{t('cashier').upper()}</th>
                        <th style="padding:8px 12px;text-align:left;font-family:var(--font-mono);font-size:0.65rem;color:var(--accent);letter-spacing:1.5px;border-bottom:1px solid var(--border)">{t('flag').upper()}</th>
                        <th style="padding:8px 12px;text-align:left;font-family:var(--font-mono);font-size:0.65rem;color:var(--accent);letter-spacing:1.5px;border-bottom:1px solid var(--border)">{t('time').upper()}</th>
                    </tr>
                </thead>
                <tbody>{html_rows}</tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col_chart:
        tc = tier_color()
        hours = [f"{i:02d}:00" for i in range(8, 23)]
        normal = [random.randint(50, 200) for _ in hours]
        flagged = [random.randint(0, 15) for _ in hours]

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.7, 0.3])
        fig.add_trace(go.Bar(x=hours, y=normal, name=t("normal_trans"), marker_color=hex_to_rgba(tc, 0.4)), row=1, col=1)
        fig.add_trace(go.Bar(x=hours, y=flagged, name=t("suspicious"), marker_color='#EF4444'), row=1, col=1)
        fig.add_trace(go.Scatter(x=hours, y=[f/n*100 if n > 0 else 0 for f, n in zip(flagged, normal)],
                                 name="Fraud %", line=dict(color='#F59E0B', width=2), fill='tozeroy',
                                 fillcolor='#F59E0B22'), row=2, col=1)
        fig.update_layout(**chart_layout(t("transaction_log"), height=400))
        st.plotly_chart(fig, use_container_width=True)

    # PROGRESS BARS
    st.markdown(f'<div class="section-sep">AI Agent Status</div>', unsafe_allow_html=True)
    agents_lite = [("Liaison Agent", 98), ("Pattern Detector", 92), ("Alert Engine", 96)]
    cols = st.columns(len(agents_lite))
    for i, (name, val) in enumerate(agents_lite):
        with cols[i]:
            st.markdown(f"""
            <div class="vg-card" style="padding:1rem">
                <div class="vg-card-title">{name}</div>
                <div style="font-size:1.5rem;font-weight:700;color:var(--accent);font-family:var(--font-display)">{val}%</div>
                <div style="font-size:0.72rem;color:var(--text-muted)">Operational</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(val / 100)

# ─────────────────────────────────────────────
# PAGE C: V-PRO FINANCE — TIER LOCKED
# ─────────────────────────────────────────────
elif t('menu_pro') in menu:
    if not has_access("V-PRO"):
        st.markdown(f"""
        <div class="lock-screen">
            <div class="lock-icon">🔒</div>
            <div class="lock-title">{t('access_denied')}</div>
            <div class="lock-desc">{t('upgrade_msg')}<br><br>
                <strong style="color:var(--accent)">V-PRO</strong> — Finance Audit · Bank Sync · Leakage Detection
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🚀 {t('upgrade')} V-PRO"):
            st.session_state.tier = "V-PRO"
            st.rerun()
    else:
        st.markdown(f"""
        <div class="page-header">
            <h1>🟡 {t('pro_title')}</h1>
            <p class="desc">{t('pro_desc')}</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(t("leakage_prevented"), "Rp 4.2M", "+22%")
        c2.metric(t("audit_score"), "94/100", "+3")
        c3.metric(t("anomalies"), "14", "This Month")
        c4.metric(t("bank_sync"), "✅ Live", "3 Banks")

        col_btn, col_status = st.columns([2, 3])
        with col_btn:
            if st.button(f"🔍 {t('scan_bank')}", key="scan_btn"):
                st.session_state.scan_running = True

        if st.session_state.scan_running:
            with st.spinner(t("scanning")):
                time.sleep(1.5)
            st.success(f"✅ {t('scan_complete')}")
            st.session_state.scan_running = False

        col_trend, col_pie = st.columns([3, 2])

        with col_trend:
            tc = tier_color()
            df_fin = gen_finance_trend()
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_fin[t("time")], y=df_fin["Leakage (Juta Rp)"],
                name="Total Leakage", fill='tozeroy', fillcolor=hex_to_rgba(tc, 0.13),
                line=dict(color=tc, width=2.5)
            ))
            fig.add_trace(go.Scatter(
                x=df_fin[t("time")], y=df_fin["Detected"],
                name="AI Detected", line=dict(color='#22C55E', width=2, dash='dot')
            ))
            fig.update_layout(**chart_layout(t("finance_trend"), height=300))
            st.plotly_chart(fig, use_container_width=True)

        with col_pie:
            tc = tier_color()
            cats = ["Petty Cash", "Supplier", "Payroll", "Operations", "Unknown"]
            vals = [28, 35, 15, 12, 10]
            fig_p = go.Figure(go.Pie(
                labels=cats, values=vals, hole=0.55,
                marker=dict(colors=[tc, '#F59E0B', '#EF4444', '#22C55E', '#8B5CF6']),
                textfont=dict(size=9)
            ))
            fig_p.update_layout(**chart_layout(t("expense_breakdown"), height=300))
            st.plotly_chart(fig_p, use_container_width=True)

        # ANOMALY TABLE
        st.markdown(f"#### ⚠️ {t('anomalies')}")
        anomaly_data = {
            "Date": ["2025-01-14", "2025-01-12", "2025-01-10", "2025-01-08", "2025-01-06"],
            "Category": ["Petty Cash", "Supplier", "Payroll", "Operations", "Petty Cash"],
            "Amount": ["Rp 840,000", "Rp 2,100,000", "Rp 450,000", "Rp 1,200,000", "Rp 620,000"],
            "Status": [t("alert_critical"), t("alert_high"), t("alert_medium"), t("alert_high"), t("alert_medium")],
        }
        st.dataframe(pd.DataFrame(anomaly_data), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# PAGE D: V-SIGHT VISUAL AI — TIER LOCKED
# ─────────────────────────────────────────────
elif t('menu_sight') in menu:
    if not has_access("V-SIGHT"):
        st.markdown(f"""
        <div class="lock-screen">
            <div class="lock-icon">📷</div>
            <div class="lock-title">{t('access_denied')}</div>
            <div class="lock-desc">{t('upgrade_msg')}<br><br>
                <strong style="color:#3B82F6">V-SIGHT</strong> — CCTV Integration · Behavior Analysis · Zone Monitoring
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🚀 {t('upgrade')} V-SIGHT"):
            st.session_state.tier = "V-SIGHT"
            st.rerun()
    else:
        st.markdown(f"""
        <div class="page-header">
            <h1>🔵 {t('sight_title')}</h1>
            <p class="desc">{t('sight_desc')}</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(t("camera_nodes"), "24 Active", "+2")
        c2.metric(t("zones_monitored"), "8 Zones", "All Live")
        c3.metric(t("anomaly_detected"), "3 Today", "⚠️ Zone 3")
        c4.metric(t("behavior_score"), "72 / 100", "Medium Risk")

        # CAMERA FEED SIMULATION
        col_feed, col_zone = st.columns([3, 2])
        with col_feed:
            tc = tier_color()
            st.markdown(f"""
            <div class="vg-card" style="padding:0;overflow:hidden">
                <div style="background:var(--bg-secondary);padding:8px 12px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--border)">
                    <span style="font-family:var(--font-mono);font-size:0.7rem;color:{tc};letter-spacing:1px">CAM-03 · ZONE A · LIVE</span>
                    <span class="badge badge-critical">● REC</span>
                </div>
                <div style="background:linear-gradient(135deg,#0B1120 0%,#0F1729 100%);height:240px;display:flex;align-items:center;justify-content:center;position:relative">
                    <div style="position:absolute;top:12px;left:12px;font-family:var(--font-mono);font-size:0.65rem;color:{tc};opacity:0.7">
                        2025-01-14 14:32:08 WIB
                    </div>
                    <div style="text-align:center;opacity:0.5">
                        <div style="font-size:3rem">📹</div>
                        <div style="font-family:var(--font-mono);font-size:0.7rem;color:var(--text-muted)">{t('camera_feed')}</div>
                    </div>
                    <div style="position:absolute;bottom:12px;right:12px">
                        <span class="badge badge-danger">⚠ ANOMALY DETECTED</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_zone:
            # ZONE ACTIVITY HEATMAP
            st.markdown(f"#### 🔥 {t('heatmap')}")
            zones = ["Zone A", "Zone B", "Zone C", "Zone D", "Zone E", "Zone F", "Zone G", "Zone H"]
            risk_vals = [random.randint(10, 100) for _ in zones]
            tc = tier_color()

            fig_h = go.Figure(go.Heatmap(
                z=[risk_vals],
                x=zones,
                colorscale=[[0, '#0F1729'], [0.5, hex_to_rgba(tc, 0.53)], [1, '#EF4444']],
                showscale=True,
                text=[[f"{v}%" for v in risk_vals]],
                texttemplate="%{text}",
                textfont=dict(size=9)
            ))
            fig_h.update_layout(**chart_layout(t("zone_map"), height=140))
            fig_h.update_layout(xaxis=dict(tickfont=dict(size=9)))
            st.plotly_chart(fig_h, use_container_width=True)

            # CAMERA NODE LIST
            st.markdown("#### 📋 Camera Nodes")
            for i, (zone, risk) in enumerate(zip(zones[:5], risk_vals[:5])):
                color = "#EF4444" if risk > 70 else ("#F59E0B" if risk > 40 else "#22C55E")
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid var(--border)">
                    <span style="font-size:0.8rem;color:var(--text-secondary)">CAM-0{i+1} · {zone}</span>
                    <span style="font-family:var(--font-mono);font-size:0.75rem;color:{color}">{risk}%</span>
                </div>
                """, unsafe_allow_html=True)

        # BEHAVIOR TIMELINE
        st.markdown(f'<div class="section-sep">Behavior Event Timeline</div>', unsafe_allow_html=True)
        tc = tier_color()
        hours = [f"{h:02d}:{m:02d}" for h in range(8, 18) for m in [0, 30]]
        behavior = [random.randint(0, 15) for _ in hours]
        fig_t = go.Figure()
        fig_t.add_trace(go.Scatter(
            x=hours, y=behavior, mode='lines+markers',
            line=dict(color=tc, width=2),
            marker=dict(size=6, color=tc, line=dict(width=1, color='#050912')),
            fill='tozeroy', fillcolor=hex_to_rgba(tc, 0.08), name="Events"
        ))
        fig_t.update_layout(**chart_layout("Behavior Event Frequency", height=220))
        st.plotly_chart(fig_t, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE E: V-ENTERPRISE — TIER LOCKED
# ─────────────────────────────────────────────
elif t('menu_enterprise') in menu:
    if not has_access("V-ENTERPRISE"):
        st.markdown(f"""
        <div class="lock-screen">
            <div class="lock-icon">🏢</div>
            <div class="lock-title">{t('access_denied')}</div>
            <div class="lock-desc">{t('upgrade_msg')}<br><br>
                <strong style="color:#8B5CF6">V-ENTERPRISE</strong> — Multi-Branch · Regional BI · Corporate Audit
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🚀 {t('upgrade')} V-ENTERPRISE"):
            st.session_state.tier = "V-ENTERPRISE"
            st.rerun()
    else:
        st.markdown(f"""
        <div class="page-header">
            <h1>🟣 {t('ent_title')}</h1>
            <p class="desc">{t('ent_desc')}</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(t("branches"), "8 Cities", "+2 New")
        c2.metric(t("total_revenue"), "Rp 1.4B", "+18%")
        c3.metric(t("group_fraud"), "1.8%", "-0.4%")
        c4.metric(t("top_branch"), "Jakarta Pusat", "⭐ 97/100")

        df_branch = gen_branch_data()
        tc = tier_color()

        col_bar, col_table = st.columns([3, 2])
        with col_bar:
            fig = px.bar(
                df_branch, x=t("location"), y="Revenue (M)",
                color="Score",
                color_continuous_scale=[[0, '#EF4444'], [0.5, '#F59E0B'], [1, tc]],
                title=t("branch_compare")
            )
            fig.update_layout(**chart_layout(t("branch_compare"), height=320))
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)

        with col_table:
            st.markdown(f"#### {t('branch_compare')}")
            st.dataframe(df_branch, use_container_width=True, hide_index=True)

        # SCATTER MAP SIMULATION
        st.markdown(f'<div class="section-sep">{t("regional_map")}</div>', unsafe_allow_html=True)
        lat = [-6.2, -7.25, -6.9, 3.58, -5.14, -8.67, -6.97, -2.99]
        lon = [106.8, 112.75, 107.6, 98.67, 119.43, 115.22, 110.42, 104.75]
        city_names = ["Jakarta", "Surabaya", "Bandung", "Medan", "Makassar", "Bali", "Semarang", "Palembang"]
        fraud_rates = [1.2, 2.4, 1.8, 3.1, 2.7, 1.1, 1.9, 2.2]

        fig_map = px.scatter_mapbox(
            lat=lat, lon=lon, hover_name=city_names,
            size=[50]*8, color=fraud_rates,
            color_continuous_scale=[[0, tc], [0.5, '#F59E0B'], [1, '#EF4444']],
            size_max=20, zoom=4, mapbox_style="carto-darkmatter",
            labels={"color": "Fraud Rate %"},
            title=t("regional_map")
        )
        fig_map.update_layout(**chart_layout(t("regional_map"), height=380))
        st.plotly_chart(fig_map, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE F: V-ULTRA STRATEGY — TIER LOCKED
# ─────────────────────────────────────────────
elif t('menu_ultra') in menu:
    if not has_access("V-ULTRA"):
        st.markdown(f"""
        <div class="lock-screen">
            <div class="lock-icon">🏆</div>
            <div class="lock-title">{t('access_denied')}</div>
            <div class="lock-desc">{t('upgrade_msg')}<br><br>
                <strong style="color:#F43F5E">V-ULTRA</strong> — Strategic AI · Investor Reports · Market Forecasting
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🚀 {t('upgrade')} V-ULTRA"):
            st.session_state.tier = "V-ULTRA"
            st.rerun()
    else:
        st.markdown(f"""
        <div class="page-header">
            <h1>🔴 {t('ultra_title')}</h1>
            <p class="desc">{t('ultra_desc')}</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(t("profit_score"), "87 / 100", "+5 pts")
        c2.metric(t("roi_projection"), "Rp 8.4B", "Next 12M")
        c3.metric(t("expansion_target"), "12 Cities", "2025 Plan")
        c4.metric("MRR", "Rp 420M", "+28% MoM")

        # ROI PROJECTION CHART
        tc = tier_color()
        df_roi = gen_roi_projection()

        col_roi, col_radar = st.columns([3, 2])
        with col_roi:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_roi["Quarter"], y=df_roi["Baseline (M)"],
                name="Baseline", line=dict(color='#8B96A8', width=1.5, dash='dot')
            ))
            fig.add_trace(go.Scatter(
                x=df_roi["Quarter"], y=df_roi["AI-Optimized (M)"],
                name="AI-Optimized", fill='tonexty', fillcolor=hex_to_rgba(tc, 0.13),
                line=dict(color=tc, width=2.5)
            ))
            fig.update_layout(**chart_layout(t("roi_projection"), height=300))
            st.plotly_chart(fig, use_container_width=True)

        with col_radar:
            dimensions = ["Market Fit", "Scalability", "Tech Moat", "Revenue", "Team", "Growth"]
            vals = [92, 88, 95, 84, 90, 87]
            vals_closed = vals + [vals[0]]
            dims_closed = dimensions + [dimensions[0]]

            fig_r = go.Figure(go.Scatterpolar(
                r=vals_closed, theta=dims_closed,
                fill='toself', fillcolor=hex_to_rgba(tc, 0.13),
                line=dict(color=tc, width=2),
                marker=dict(size=6, color=tc)
            ))
            fig_r.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=8, color='#8B96A8'), gridcolor='rgba(255,255,255,0.06)'),
                    angularaxis=dict(tickfont=dict(size=9, color='#E8EDF5'), gridcolor='rgba(255,255,255,0.06)'),
                    bgcolor='rgba(0,0,0,0)'
                ),
                **chart_layout("Investor Score Radar", height=300)
            )
            st.plotly_chart(fig_r, use_container_width=True)

        # GENERATE REPORT BUTTON
        st.markdown(f'<div class="section-sep">{t("investor_report")}</div>', unsafe_allow_html=True)
        col_gen, col_info = st.columns([1, 2])
        with col_gen:
            if st.button(f"📊 {t('generate_report')}"):
                with st.spinner(t("generating")):
                    time.sleep(2)
                st.session_state.report_generated = True

        if st.session_state.report_generated:
            st.success("✅ AI Investor Report Generated Successfully")
            with st.expander(f"📄 {t('investor_report')} — Preview"):
                lang = st.session_state.lang
                if lang == "id":
                    st.markdown("""
**LAPORAN INVESTOR V-GUARD AI — Q1 2025**

**Ringkasan Eksekutif**
V-GUARD AI mengoperasikan platform SaaS intelijen bisnis multi-tier yang telah mencegah total **Rp 42,5M kebocoran bisnis** di 1.284 node aktif dalam kuartal ini.

**Metrik Kunci**
- MRR saat ini: **Rp 420M** (+28% MoM)
- ARR run-rate: **Rp 5,04B**
- Pelanggan aktif: **847 bisnis** (UKM ke Korporat)
- NPS Score: **72** (Kelas Dunia)

**Keunggulan Kompetitif**
Platform AI kami mengoperasikan 10 Agen AI yang terintegrasi antara CCTV, Kasir, dan Cloud — menghasilkan latensi deteksi **<200ms** dengan akurasi **99,2%**.

**Proyeksi 2025**
Target ARR: **Rp 12B** melalui ekspansi ke 12 kota dan peluncuran V-ULTRA Enterprise.
                    """)
                else:
                    st.markdown("""
**V-GUARD AI INVESTOR REPORT — Q1 2025**

**Executive Summary**
V-GUARD AI operates a multi-tier SaaS business intelligence platform that has prevented **Rp 42.5M in business leakage** across 1,284 active nodes this quarter.

**Key Metrics**
- Current MRR: **Rp 420M** (+28% MoM)
- ARR run-rate: **Rp 5.04B**
- Active customers: **847 businesses** (SME to Corporate)
- NPS Score: **72** (World Class)

**Competitive Advantage**
Our AI platform operates 10 integrated AI Agents across CCTV, POS, and Cloud — delivering **<200ms** detection latency with **99.2%** accuracy.

**2025 Projection**
Target ARR: **Rp 12B** through expansion to 12 cities and V-ULTRA Enterprise launch.
                    """)

        # MARKET EXPANSION FORECAST
        st.markdown(f"#### 🌍 {t('market_forecast')}")
        tc = tier_color()
        months_f = ["Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec","Jan'26"]
        mrr = [420, 480, 540, 620, 700, 790, 880, 960, 1040, 1150, 1280, 1400]
        clients = [847, 920, 1010, 1120, 1250, 1400, 1570, 1720, 1890, 2050, 2280, 2500]

        fig_f = make_subplots(specs=[[{"secondary_y": True}]])
        fig_f.add_trace(go.Bar(x=months_f, y=mrr, name="MRR (Juta Rp)", marker_color=hex_to_rgba(tc, 0.67)), secondary_y=False)
        fig_f.add_trace(go.Scatter(x=months_f, y=clients, name="Active Clients",
                                   line=dict(color='#22C55E', width=2), mode='lines+markers',
                                   marker=dict(size=5)), secondary_y=True)
        fig_f.update_layout(**chart_layout(t("market_forecast"), height=320))
        st.plotly_chart(fig_f, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE G: AI CHAT CONSULTANT
# ─────────────────────────────────────────────
elif t('menu_chat') in menu:
    st.markdown(f"""
    <div class="page-header">
        <h1>💬 {t('chat_title')}</h1>
        <p class="desc">{t('chat_placeholder')}</p>
    </div>
    """, unsafe_allow_html=True)

    col_chat, col_tips = st.columns([3, 2])

    with col_chat:
        # INITIALIZE CHAT HISTORY
        if not st.session_state.chat_history:
            st.session_state.chat_history = [
                {"role": "ai", "content": t("chat_greeting")}
            ]

        # DISPLAY CHAT HISTORY
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f'<div class="chat-msg-user">{msg["content"]}</div>'
            else:
                chat_html += f'''
                <div>
                    <div class="chat-ai-label">🛡️ V-GUARD AI</div>
                    <div class="chat-msg-ai">{msg["content"]}</div>
                </div>'''
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)

        # INPUT ROW
        user_input = st.text_input(
            "", placeholder=t("chat_placeholder"),
            key="chat_input", label_visibility="collapsed"
        )
        col_send, col_clear = st.columns([3, 1])
        with col_send:
            if st.button(f"➤ {t('chat_send')}", key="send_btn"):
                if user_input.strip():
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    with st.spinner(t("chat_thinking")):
                        time.sleep(0.8)
                    response = get_ai_response()
                    st.session_state.chat_history.append({"role": "ai", "content": response})
                    st.rerun()
        with col_clear:
            if st.button("🗑️ Clear", key="clear_btn"):
                st.session_state.chat_history = [{"role": "ai", "content": t("chat_greeting")}]
                st.rerun()

    with col_tips:
        st.markdown(f"""
        <div class="vg-card">
            <div class="vg-card-title">Quick Questions</div>
            <div style="margin-top:0.8rem;display:flex;flex-direction:column;gap:8px">
        """, unsafe_allow_html=True)

        quick_q_en = [
            "Why is my void rate high?",
            "How to detect duplicate transactions?",
            "What is my fraud risk score?",
            "Show me leakage prevention tips",
            "Analyze my cashier performance",
        ]
        quick_q_id = [
            "Mengapa tingkat void saya tinggi?",
            "Cara mendeteksi transaksi duplikat?",
            "Berapa skor risiko kecurangan saya?",
            "Tampilkan tips pencegahan kebocoran",
            "Analisis kinerja kasir saya",
        ]
        quick_qs = quick_q_id if st.session_state.lang == "id" else quick_q_en

        for q in quick_qs:
            if st.button(q, key=f"qq_{q[:15]}"):
                st.session_state.chat_history.append({"role": "user", "content": q})
                response = get_ai_response()
                st.session_state.chat_history.append({"role": "ai", "content": response})
                st.rerun()

        st.markdown("""</div></div>""", unsafe_allow_html=True)

        # AI AGENT INFO
        st.markdown(f"""
        <div class="vg-card" style="margin-top:1rem">
            <div class="vg-card-title">AI Engine Info</div>
            <div style="margin-top:0.8rem">
                <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--border)">
                    <span style="font-size:0.8rem;color:var(--text-secondary)">Model</span>
                    <span style="font-family:var(--font-mono);font-size:0.75rem;color:var(--accent)">V-GUARD v2.0</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--border)">
                    <span style="font-size:0.8rem;color:var(--text-secondary)">Context</span>
                    <span style="font-family:var(--font-mono);font-size:0.75rem;color:var(--accent)">Business BI</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--border)">
                    <span style="font-size:0.8rem;color:var(--text-secondary)">Latency</span>
                    <span style="font-family:var(--font-mono);font-size:0.75rem;color:#22C55E">&lt;200ms</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:5px 0">
                    <span style="font-size:0.8rem;color:var(--text-secondary)">Status</span>
                    <span class="badge badge-success">● Online</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 9: FLOATING CHAT WIDGET (Global — appears on all pages)
# ═══════════════════════════════════════════════════════════════════════════

tc = tier_color()
st.markdown(f"""
<div class="chat-fab" title="{t('chat_title')}" onclick="window.location.href='?page=chat'">
    💬
</div>
<style>
.chat-fab {{
    background: linear-gradient(135deg, {tc}, {tc}cc) !important;
    box-shadow: 0 8px 25px {tc}66 !important;
    border-color: {tc}66 !important;
}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 10: GLOBAL FOOTER
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("---")
col_f1, col_f2, col_f3, col_f4 = st.columns(4)

with col_f1:
    st.markdown(f"""
    <div style="font-family:var(--font-mono);font-size:0.7rem;color:var(--text-muted)">
        <strong style="color:var(--accent)">V-GUARD AI</strong><br>
        Elite Intelligence Platform<br>
        v2.0.0 · Build 2025
    </div>
    """, unsafe_allow_html=True)

with col_f2:
    st.markdown(f"""
    <div style="font-family:var(--font-mono);font-size:0.7rem;color:var(--text-muted)">
        <strong style="color:var(--text-secondary)">ACTIVE TIER</strong><br>
        {TIER_ICONS.get(st.session_state.tier,'🛡️')} {st.session_state.tier}<br>
        {tier_color()}
    </div>
    """, unsafe_allow_html=True)

with col_f3:
    st.markdown(f"""
    <div style="font-family:var(--font-mono);font-size:0.7rem;color:var(--text-muted)">
        <strong style="color:var(--text-secondary)">SYSTEM</strong><br>
        AI Agents: 10/10 ● Online<br>
        Uptime: 99.98% · 30 days
    </div>
    """, unsafe_allow_html=True)

with col_f4:
    now = datetime.datetime.now()
    st.markdown(f"""
    <div style="font-family:var(--font-mono);font-size:0.7rem;color:var(--text-muted);text-align:right">
        <strong style="color:var(--text-secondary)">SESSION</strong><br>
        {now.strftime('%Y-%m-%d %H:%M:%S')}<br>
        Lang: {st.session_state.lang.upper()} · WIB
    </div>
    """, unsafe_allow_html=True)
