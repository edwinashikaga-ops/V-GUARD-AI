import streamlit as st
import os
import urllib.parse
import random
import string
import pandas as pd

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# ============================================================================
# 1. PENGATURAN AI & KEAMANAN
# ============================================================================
gemini_key = os.environ.get("GEMINI_API_KEY")
ai_status_msg = "Mode Offline"
model_vguard = None

if gemini_key and GENAI_AVAILABLE:
    try:
        genai.configure(api_key=gemini_key)
        model_vguard = genai.GenerativeModel('gemini-1.5-flash')
        ai_status_msg = "Connected"
    except Exception:
        ai_status_msg = "Error Connection"

# ============================================================================
# 2. KONFIGURASI HALAMAN
# ============================================================================
st.set_page_config(
    page_title="V-Guard AI Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inisialisasi session state
defaults = {
    "admin_logged_in": False,
    "system_status": "Healthy",
    "db_umum": [],
    "api_cost_total": 0.0,
    "show_demo": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================================
# 3. FUNGSI HELPER
# ============================================================================
def get_sample_transaksi():
    import datetime
    now = datetime.datetime.now()
    data = {
        "ID_Transaksi": ["TRX-001","TRX-002","TRX-003","TRX-004","TRX-005","TRX-006","TRX-007","TRX-008"],
        "Cabang":       ["Outlet Sudirman","Outlet Sudirman","Resto Central","Cabang Tangerang","Outlet Sudirman","Resto Central","Cabang Tangerang","Outlet Sudirman"],
        "Kasir":        ["Budi","Budi","Sari","Andi","Budi","Sari","Andi","Dewi"],
        "Jumlah":       [150000,150000,500000,200000,150000,300000,50000,75000],
        "Waktu":        [
            now - datetime.timedelta(minutes=2),
            now - datetime.timedelta(minutes=3),
            now - datetime.timedelta(hours=1),
            now - datetime.timedelta(hours=2),
            now - datetime.timedelta(minutes=4),
            now - datetime.timedelta(hours=3),
            now - datetime.timedelta(hours=5),
            now - datetime.timedelta(minutes=10),
        ],
        "Status":       ["VOID","NORMAL","NORMAL","NORMAL","VOID","NORMAL","NORMAL","NORMAL"],
        "Saldo_Fisik":  [0,150000,480000,200000,0,300000,45000,75000],
        "Saldo_Sistem": [150000,150000,500000,200000,150000,300000,50000,75000],
    }
    return pd.DataFrame(data)

def scan_fraud_lokal(df_trx):
    void_df = df_trx[df_trx["Status"] == "VOID"].copy()
    df_sorted = df_trx.sort_values(["Kasir","Jumlah","Waktu"])
    df_sorted["selisih_menit"] = (
        df_sorted.groupby(["Kasir","Jumlah"])["Waktu"].diff().dt.total_seconds().div(60)
    )
    fraud_df = df_sorted[df_sorted["selisih_menit"] < 5].copy()
    df_trx = df_trx.copy()
    df_trx["selisih_saldo"] = df_trx["Saldo_Sistem"] - df_trx["Saldo_Fisik"]
    suspicious_df = df_trx[df_trx["selisih_saldo"] != 0].copy()
    return {"void": void_df, "fraud": fraud_df, "suspicious": suspicious_df}

def hitung_budget_guard(db_umum, api_cost_total):
    total_omset = sum(
        int("".join(filter(str.isdigit, str(k.get("Nilai Kontrak","0"))))) or 0
        for k in db_umum
    ) or 32_500_000
    batas_anggaran = total_omset * 0.20
    persen_terpakai = (api_cost_total / batas_anggaran * 100) if batas_anggaran > 0 else 0
    return total_omset, batas_anggaran, persen_terpakai, persen_terpakai >= 80

def buat_link_wa_alert(nama_cabang, nomor="6282122190885"):
    pesan = f"⚠️ ALERT V-GUARD: Terdeteksi aktivitas mencurigakan pada Kasir [{nama_cabang}]. Segera cek sistem!"
    return f"https://wa.me/{nomor}?text={urllib.parse.quote(pesan)}"

WA_NUMBER    = "6282122190885"
WA_LINK_DEMO = f"https://wa.me/{WA_NUMBER}?text={urllib.parse.quote('Halo Pak Erwin, saya ingin Book Demo V-Guard AI.')}"
WA_LINK_KONSUL = f"https://wa.me/{WA_NUMBER}?text={urllib.parse.quote('Halo Pak Erwin, saya ingin konsultasi mengenai V-Guard AI.')}"

# ============================================================================
# 4. CSS GLOBAL — Dark Cyber Security Theme
# ============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;700&display=swap');

:root {
    --bg-primary:   #060b14;
    --bg-secondary: #0d1626;
    --bg-card:      #101c2e;
    --bg-hover:     #162035;
    --accent:       #00d4ff;
    --accent2:      #0091ff;
    --accent3:      #7b2fff;
    --danger:       #ff3b5c;
    --success:      #00e676;
    --warning:      #ffab00;
    --text-primary: #e8f4ff;
    --text-muted:   #7a9bbf;
    --border:       #1e3352;
    --border-glow:  #00d4ff44;
    --gold:         #ffd700;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
    background-color: var(--bg-primary) !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #08111f 0%, #0d1a2e 100%) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

.main .block-container { padding: 0 !important; max-width: 100% !important; }

.stButton > button {
    background: linear-gradient(135deg, var(--accent2), var(--accent)) !important;
    color: #000 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    border: none !important;
    border-radius: 6px !important;
    height: 46px !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.5px !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 0 20px var(--border-glow) !important; }
.stButton > button[kind="secondary"] { background: transparent !important; color: var(--accent) !important; border: 1px solid var(--accent) !important; }

a[data-testid="stLinkButton"] button {
    background: linear-gradient(135deg, #25D366, #128C7E) !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 10px var(--border-glow) !important;
}

.stSelectbox > div > div, .stRadio > div { background-color: transparent !important; }

[data-testid="stMetric"] { background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; padding: 16px !important; }
[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: var(--accent) !important; font-family: 'Rajdhani', sans-serif !important; font-size: 28px !important; }

.stTabs [data-baseweb="tab-list"] { background: var(--bg-secondary) !important; border-bottom: 1px solid var(--border) !important; }
.stTabs [data-baseweb="tab"] { color: var(--text-muted) !important; font-family: 'Rajdhani', sans-serif !important; font-weight: 600 !important; font-size: 15px !important; }
.stTabs [aria-selected="true"] { color: var(--accent) !important; border-bottom: 2px solid var(--accent) !important; }

[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 8px !important; }
.stAlert { border-radius: 8px !important; border-left: 3px solid !important; }
[data-testid="stExpander"] { border: 1px solid var(--border) !important; border-radius: 8px !important; background: var(--bg-card) !important; }
.stProgress > div > div > div { background: linear-gradient(90deg, var(--accent2), var(--accent)) !important; }
hr { border-color: var(--border) !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── Hero ── */
.hero-section {
    background: linear-gradient(135deg, #060b14 0%, #0a1628 50%, #080f1e 100%);
    padding: 60px 48px 48px;
    position: relative;
    overflow: hidden;
    border-bottom: 1px solid var(--border);
}
.hero-section::before {
    content: '';
    position: absolute; top: -50%; right: -10%;
    width: 600px; height: 600px;
    background: radial-gradient(circle, #00d4ff11 0%, transparent 70%);
    pointer-events: none;
}
.hero-section::after {
    content: '';
    position: absolute; bottom: -30%; left: 20%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, #7b2fff0a 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, #00d4ff22, #0091ff22);
    border: 1px solid var(--accent);
    color: var(--accent) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    padding: 4px 14px;
    border-radius: 20px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 20px;
}
.hero-title {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 58px !important;
    font-weight: 700 !important;
    line-height: 1.1 !important;
    color: var(--text-primary) !important;
    margin-bottom: 8px !important;
}
.hero-title .accent { color: var(--accent) !important; }
.hero-subtitle {
    font-size: 19px !important;
    color: var(--text-muted) !important;
    line-height: 1.7 !important;
    max-width: 520px;
    margin-bottom: 36px !important;
}

/* ── Pain Cards ── */
.pain-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 12px;
    border-left: 3px solid var(--danger);
    transition: all 0.2s ease;
}
.pain-card:hover { border-color: var(--accent); background: var(--bg-hover); }
.pain-icon { font-size: 22px; margin-bottom: 6px; }
.pain-title { font-family: 'Rajdhani', sans-serif !important; font-size: 16px !important; font-weight: 700 !important; color: var(--text-primary) !important; }
.pain-desc  { font-size: 13px !important; color: var(--text-muted) !important; margin-top: 4px; }

/* ── Stat Cards ── */
.stat-card {
    background: linear-gradient(135deg, var(--bg-card), var(--bg-secondary));
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 28px 20px;
    text-align: center;
}
.stat-number {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 44px !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, var(--accent), var(--accent3));
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}
.stat-label { font-size: 13px !important; color: var(--text-muted) !important; margin-top: 4px; }

/* ── Feature Cards ── */
.feature-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    height: 100%;
    transition: all 0.3s ease;
}
.feature-card:hover { border-color: var(--accent); transform: translateY(-3px); box-shadow: 0 8px 30px #00d4ff11; }
.feature-icon  { font-size: 30px; margin-bottom: 12px; }
.feature-title { font-family: 'Rajdhani', sans-serif !important; font-size: 17px !important; font-weight: 700 !important; color: var(--text-primary) !important; margin-bottom: 8px; }
.feature-desc  { font-size: 13px !important; color: var(--text-muted) !important; line-height: 1.6; }

/* ── Testimonial ── */
.testimonial-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    border-left: 3px solid var(--accent);
}
.testimonial-text   { font-size: 14px !important; color: var(--text-primary) !important; line-height: 1.7; font-style: italic; margin-bottom: 16px; }
.testimonial-author { font-family: 'Rajdhani', sans-serif !important; font-size: 15px !important; font-weight: 700 !important; color: var(--accent) !important; }
.testimonial-role   { font-size: 12px !important; color: var(--text-muted) !important; }
.stars { color: var(--gold) !important; font-size: 14px; margin-bottom: 10px; }

/* ── Section Wrappers ── */
.section-header    { font-family: 'Rajdhani', sans-serif !important; font-size: 36px !important; font-weight: 700 !important; color: var(--text-primary) !important; text-align: center; margin-bottom: 8px !important; }
.section-subheader { font-size: 16px !important; color: var(--text-muted) !important; text-align: center; margin-bottom: 36px !important; }
.section-accent    { color: var(--accent) !important; }
.section-wrapper     { padding: 56px 48px; border-bottom: 1px solid var(--border); }
.section-wrapper-alt { padding: 56px 48px; background: var(--bg-secondary); border-bottom: 1px solid var(--border); }

/* ── Demo Mockup ── */
.demo-mockup { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 16px; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-muted); line-height: 1.8; }
.demo-dot    { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; }
.demo-red    { background: #ff5f57; }
.demo-yellow { background: #febc2e; }
.demo-green  { background: #28c840; }

/* ── WA Float ── */
.wa-float {
    position: fixed; bottom: 28px; right: 28px; z-index: 9999;
    background: #25D366; color: white !important;
    border-radius: 50px; padding: 14px 22px;
    font-family: 'Rajdhani', sans-serif; font-size: 15px; font-weight: 700;
    text-decoration: none !important;
    display: flex; align-items: center; gap: 8px;
    box-shadow: 0 6px 24px #25D36655;
    transition: all 0.3s ease; letter-spacing: 0.5px;
}
.wa-float:hover { transform: translateY(-3px); box-shadow: 0 12px 32px #25D36688; color: white !important; }

/* ── Login Card ── */
.login-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; padding: 36px; max-width: 440px; margin: 0 auto; }

/* ── Admin ── */
.admin-metric     { background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; text-align: center; }
.admin-metric-val { font-family: 'Rajdhani', sans-serif !important; font-size: 32px !important; font-weight: 700 !important; color: var(--accent) !important; }
.admin-metric-lbl { font-size: 12px !important; color: var(--text-muted) !important; margin-top: 4px; }

/* ── ROI ── */
.roi-result-big { font-family: 'Rajdhani', sans-serif !important; font-size: 48px !important; font-weight: 700 !important; line-height: 1 !important; }
.roi-label      { font-size: 13px !important; color: var(--text-muted) !important; }

/* ── Page Title ── */
.page-title    { font-family: 'Rajdhani', sans-serif !important; font-size: 34px !important; font-weight: 700 !important; color: var(--text-primary) !important; margin-bottom: 4px !important; }
.page-subtitle { font-size: 15px !important; color: var(--text-muted) !important; margin-bottom: 32px !important; }

/* ── Sidebar Logo ── */
.sidebar-logo    { font-family: 'Rajdhani', sans-serif !important; font-size: 24px !important; font-weight: 700 !important; color: var(--accent) !important; letter-spacing: 1px; text-align: center; }
.sidebar-tagline { font-size: 11px !important; color: var(--text-muted) !important; text-align: center; letter-spacing: 2px; text-transform: uppercase; }

/* ── Status Dot ── */
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--success); margin-right: 6px; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.4;} }

/* ════════════════════════════════════════════════════════
   PRODUK & HARGA — Invisible Tech Strategy
   ════════════════════════════════════════════════════════ */

.tier-badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 10px;
}
.badge-entry { background:#00d4ff18; color:#00d4ff!important; border:1px solid #00d4ff55; }
.badge-pro   { background:#0091ff18; color:#6ac8ff!important; border:1px solid #0091ff55; }
.badge-sight { background:#7b2fff18; color:#b49fff!important; border:1px solid #7b2fff55; }
.badge-ent   { background:#00e67618; color:#00e676!important; border:1px solid #00e67655; }
.badge-ultra { background:#ffd70018; color:#ffd700!important; border:1px solid #ffd70055; }

.pkg-card {
    background: #101c2e;
    border: 1px solid #1e3352;
    border-radius: 14px;
    padding: 22px 18px 20px;
    display: flex; flex-direction: column; gap: 0;
    height: 100%;
    transition: all 0.3s ease;
    position: relative;
}
.pkg-card:hover { border-color: #00d4ff; box-shadow: 0 0 28px #00d4ff11; transform: translateY(-4px); }
.pkg-card.ultra {
    background: linear-gradient(160deg, #12100a 0%, #1a1500 60%, #0e0e0e 100%);
    border: 1px solid #ffd70055;
}
.pkg-card.ultra:hover { border-color: #ffd700; box-shadow: 0 0 32px #ffd70022; }
.pkg-card.popular-card { border: 1.5px solid #0091ff; }

.hot-label {
    position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
    background: linear-gradient(135deg, #0091ff, #00d4ff);
    color: #000 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 10px !important; font-weight: 700 !important;
    padding: 3px 14px; border-radius: 20px; letter-spacing: 1px; white-space: nowrap;
}
.ultra-label {
    position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
    background: linear-gradient(135deg, #b8860b, #ffd700);
    color: #000 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 10px !important; font-weight: 700 !important;
    padding: 3px 14px; border-radius: 20px; letter-spacing: 1px; white-space: nowrap;
}

.pkg-name       { font-family: 'Rajdhani', sans-serif !important; font-size: 20px !important; font-weight: 700 !important; color: #e8f4ff !important; letter-spacing: 0.5px; margin-bottom: 2px; }
.pkg-name.ultra { color: #ffd700 !important; }
.pkg-focus      { font-size: 11px !important; color: #7a9bbf !important; line-height: 1.4; margin-bottom: 14px; }

.pkg-price        { font-family: 'Rajdhani', sans-serif !important; font-size: 26px !important; font-weight: 700 !important; color: #00d4ff !important; margin-bottom: 2px; }
.pkg-price.ultra  { color: #ffd700 !important; }
.pkg-period       { font-size: 11px !important; color: #7a9bbf !important; margin-bottom: 4px; }
.pkg-setup        { font-size: 11px !important; color: #4a6a8a !important; margin-bottom: 14px; }
.pkg-divider      { border: none; border-top: 1px solid #1e3352; margin: 12px 0; }

.pkg-feature            { font-size: 12px !important; color: #9ab8d4 !important; padding: 4px 0; display: flex; align-items: flex-start; gap: 7px; line-height: 1.4; }
.pkg-feature .ck        { color: #00e676 !important; flex-shrink: 0; font-size: 11px; }
.pkg-feature.ultra-feat { color: #d4b84a !important; }
.pkg-feature.ultra-feat .ck { color: #ffd700 !important; }

.agent-row  { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 12px; }
.agent-pill { font-family: 'JetBrains Mono', monospace !important; font-size: 9px !important; padding: 3px 8px; border-radius: 20px; background: #0d1a2e; border: 1px solid #1e3352; color: #7a9bbf !important; display: flex; align-items: center; gap: 4px; }
.agent-pill .dot       { width:6px; height:6px; border-radius:50%; background:#00e676; flex-shrink:0; }
.agent-pill.ultra-pill { background: #1a1500; border-color: #ffd70033; color: #d4b84a !important; }
.agent-pill.ultra-pill .dot { background: #ffd700; }

.comp-section-title { font-family: 'Rajdhani', sans-serif !important; font-size: 28px !important; font-weight: 700 !important; color: #e8f4ff !important; margin-bottom: 4px !important; }
.comp-section-sub   { font-size: 14px !important; color: #7a9bbf !important; margin-bottom: 28px !important; }

.agent-comp-card { background: #101c2e; border: 1px solid #1e3352; border-radius: 10px; padding: 16px 18px; margin-bottom: 10px; }
.agent-comp-name { font-family: 'Rajdhani', sans-serif !important; font-size: 15px !important; font-weight: 700 !important; color: #00d4ff !important; margin-bottom: 3px; }
.agent-comp-role { font-size: 12px !important; color: #7a9bbf !important; margin-bottom: 8px; }

.tier-dot      { display: inline-block; font-size: 10px !important; padding: 2px 8px; border-radius: 10px; margin-right: 4px; font-family: 'JetBrains Mono', monospace !important; }
.td-lite  { background:#00d4ff11; color:#00d4ff!important; border:1px solid #00d4ff33; }
.td-pro   { background:#0091ff11; color:#6ac8ff!important; border:1px solid #0091ff33; }
.td-sight { background:#7b2fff11; color:#b49fff!important; border:1px solid #7b2fff33; }
.td-ent   { background:#00e67611; color:#00e676!important; border:1px solid #00e67633; }
.td-ultra { background:#ffd70011; color:#ffd700!important; border:1px solid #ffd70033; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 5. FLOATING WHATSAPP BUTTON
# ============================================================================
st.markdown(f"""
<a class="wa-float" href="{WA_LINK_KONSUL}" target="_blank">
    <span>💬</span> Chat WhatsApp
</a>
""", unsafe_allow_html=True)

# ============================================================================
# 6. SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div style='padding: 20px 0 16px; border-bottom: 1px solid #1e3352; margin-bottom: 16px;'>
        <div class='sidebar-logo'>🛡️ V-GUARD AI</div>
        <div class='sidebar-tagline'>Digital Business Auditor</div>
    </div>
    """, unsafe_allow_html=True)

    if os.path.exists("erwin.jpg"):
        st.image("erwin.jpg", use_container_width=True)
        st.markdown("""
        <div style='text-align:center; margin: 10px 0 16px;'>
            <p style='color:#e8f4ff; font-weight:bold; margin-bottom:2px; font-size:14px;'>Erwin Sinaga</p>
            <p style='color:#7a9bbf; font-size:12px;'>Founder & CEO</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<p style='color:#7a9bbf; font-size:11px; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:8px;'>Navigasi</p>", unsafe_allow_html=True)

    menu = st.radio(
        "",
        ["🏠 Beranda", "📦 Produk & Harga", "📊 Kalkulator ROI", "🔑 Portal Klien"],
        label_visibility="collapsed",
    )

    st.markdown("<hr style='border-color:#1e3352; margin: 16px 0;'>", unsafe_allow_html=True)

    with st.expander("🔒 Admin Access"):
        if not st.session_state.admin_logged_in:
            admin_pw = st.text_input("Access Code", type="password", key="sidebar_admin_pw")
            if st.button("Masuk", key="btn_admin_login"):
                if admin_pw == "w1nbju8282":
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Access Code Salah!")
        else:
            st.success("✅ Admin Aktif")
            if st.button("🚪 Log Out", key="btn_logout"):
                st.session_state.admin_logged_in = False
                st.rerun()
            menu = "⚙️ Admin Control Center"

    st.markdown(f"""
    <div style='margin-top:16px; padding:12px; background:#101c2e; border-radius:8px; border:1px solid #1e3352;'>
        <span class='status-dot'></span>
        <span style='font-size:12px; color:#7a9bbf;'>AI Engine: <b style='color:#00d4ff;'>{ai_status_msg}</b></span>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.admin_logged_in:
    menu = "⚙️ Admin Control Center"

# ============================================================================
# 7. BERANDA
# ============================================================================
if menu == "🏠 Beranda":

    st.markdown("""
    <div class="hero-section">
        <div class="hero-badge">🛡️ &nbsp; AI-Powered Fraud Detection &nbsp; · &nbsp; 24/7 Autonomous</div>
        <div class="hero-title">
            Hentikan <span class="accent">Kebocoran</span><br>
            Bisnis Anda.<br>
            Sekarang.
        </div>
        <div class="hero-subtitle">
            V-Guard AI mengawasi setiap Rupiah di kasir, stok, dan rekening bank Anda
            secara otomatis — mendeteksi kecurangan sebelum Anda menyadarinya.
        </div>
    </div>
    """, unsafe_allow_html=True)

    cta_col1, cta_col2, cta_col3 = st.columns([1.2, 1.2, 3])
    with cta_col1:
        st.link_button("🚀 Book Demo Gratis", WA_LINK_DEMO, use_container_width=True)
    with cta_col2:
        if st.button("📊 Hitung Kerugian Saya", use_container_width=True, type="secondary"):
            st.session_state["go_roi"] = True
            st.rerun()

    st.markdown("<div style='height:48px;'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-wrapper'>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    for col, (num, lbl) in zip([s1, s2, s3, s4], [
        ("88%", "Kebocoran Berhasil Dicegah"),
        ("24/7", "Monitoring Otomatis"),
        ("< 5 Dtk", "Deteksi Real-Time"),
        ("5 Tier", "Solusi untuk Semua Skala"),
    ]):
        with col:
            st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-number'>{num}</div>
                <div class='stat-label'>{lbl}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='section-wrapper-alt'>
        <div class='section-header'>Apakah Anda Mengalami <span class='section-accent'>Ini?</span></div>
        <div class='section-subheader'>Tanda-tanda "The Invisible Leak" yang diam-diam menguras bisnis Anda</div>
    </div>
    """, unsafe_allow_html=True)

    pain_col1, pain_col2, pain_col3 = st.columns(3)
    pains = [
        ("💸","Omzet Besar, Uang Tidak Sinkron","Laporan kasir dan mutasi bank selalu berbeda. Entah ke mana selisihnya pergi."),
        ("📦","Stok Hilang Misterius","Barang keluar tapi tidak ada di laporan penjualan. Supplier menagih tapi tidak ada catatan masuk."),
        ("👁️","Tidak Bisa Pantau Semua Cabang","Anda tidak bisa ada di mana-mana. Tanpa CCTV AI, staf tahu kapan bisa 'bermain'."),
        ("🔄","Void & Diskon Mencurigakan","Transaksi sering di-void setelah pelanggan pergi. Diskon diberikan tanpa otorisasi."),
        ("💤","Laporan Manual yang Melelahkan","Setiap malam cocokkan angka manual. Sabtu-Minggu pun tidak tenang karena laporan menunggu."),
        ("📅","Piutang Macet, Arus Kas Terganggu","Tagihan ke pelanggan terlambat ditagih. Invoice H-30 baru diingat di H+15."),
    ]
    for col, group in zip([pain_col1, pain_col2, pain_col3], [pains[:2], pains[2:4], pains[4:]]):
        with col:
            for icon, title, desc in group:
                st.markdown(f"""
                <div class='pain-card'>
                    <div class='pain-icon'>{icon}</div>
                    <div class='pain-title'>{title}</div>
                    <div class='pain-desc'>{desc}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class='section-wrapper'>
        <div class='section-header'>Ekosistem <span class='section-accent'>V-Guard</span></div>
        <div class='section-subheader'>Satu platform, semua celah kecurangan tertutup secara otomatis</div>
    </div>
    """, unsafe_allow_html=True)

    fc = st.columns(3)
    for i, (icon, title, desc) in enumerate([
        ("🔗","Auto Data Integration","Tarik data langsung dari mesin kasir via IP/API. Tanpa input manual CSV."),
        ("🚨","Anomaly Detection Engine","Tandai VOID, refund, dan diskon mencurigakan secara otomatis dalam hitungan detik."),
        ("🏦","Bank Statement Audit","Cocokkan laporan kasir dengan mutasi bank secara otomatis. Selisih langsung terdeteksi."),
        ("📹","Visual Cashier Audit (CCTV)","Tampilkan teks transaksi tepat di atas rekaman CCTV real-time. Bukti visual tak terbantahkan."),
        ("📦","Smart Inventory (OCR)","Update stok otomatis via drag-and-drop invoice. Supplier vs penjualan selalu sinkron."),
        ("📲","WhatsApp Fraud Alarm","Notifikasi instan ke ponsel Owner saat anomali terdeteksi. Tidak perlu buka laptop."),
    ]):
        with fc[i % 3]:
            st.markdown(f"""
            <div class='feature-card'>
                <div class='feature-icon'>{icon}</div>
                <div class='feature-title'>{title}</div>
                <div class='feature-desc'>{desc}</div>
            </div>""", unsafe_allow_html=True)
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='section-wrapper-alt'>
        <div class='section-header'>Lihat <span class='section-accent'>Dashboard</span> V-Guard</div>
        <div class='section-subheader'>Tampilan real-time monitoring langsung dari browser Anda</div>
    </div>
    """, unsafe_allow_html=True)

    demo_col1, demo_col2 = st.columns([1.6, 1])
    with demo_col1:
        st.markdown("""
        <div class='demo-mockup'>
            <div style='margin-bottom:12px;'>
                <span class='demo-dot demo-red'></span>
                <span class='demo-dot demo-yellow'></span>
                <span class='demo-dot demo-green'></span>
                <span style='margin-left:12px; color:#7a9bbf; font-size:11px;'>v-guard.ai / sentinel-dashboard</span>
            </div>
            <span style='color:#7b2fff;'>●</span> [SENTINEL AI] — Fraud Scanner aktif...<br>
            <span style='color:#00d4ff;'>▸</span> Scanning 8 transaksi terakhir...<br>
            <span style='color:#ff3b5c;'>⚠</span> [ALERT] VOID terdeteksi: TRX-001 — Kasir: Budi — Rp 150.000<br>
            <span style='color:#ff3b5c;'>⚠</span> [ALERT] VOID terdeteksi: TRX-005 — Kasir: Budi — Rp 150.000<br>
            <span style='color:#ffab00;'>▸</span> Pola duplikat dalam 2 menit — Outlet Sudirman<br>
            <span style='color:#ff3b5c;'>⚠</span> [ALERT] Selisih saldo: TRX-003 — Rp 20.000 hilang<br>
            <span style='color:#00e676;'>✓</span> WhatsApp Alert dikirim ke Owner (6282xxxxxx)<br>
            <span style='color:#00d4ff;'>▸</span> AI Deep Scan selesai — 3 anomali dilaporkan<br>
            <span style='color:#00e676;'>✓</span> Laporan PDF dibuat otomatis — 04:00 WIB<br>
            <span style='color:#7a9bbf;'>_</span>
        </div>
        """, unsafe_allow_html=True)
    with demo_col2:
        st.markdown("<div style='padding: 24px 0;'><p style='color:#7a9bbf; font-size:13px;'>Sentinel AI bekerja 24 jam:</p></div>", unsafe_allow_html=True)
        for icon, val, lbl in [("🔍","3 Anomali","Terdeteksi malam ini"),("📲","1 Alert","Dikirim ke Owner"),("📊","100%","Audit Coverage"),("⚡","0.2ms","Response Time")]:
            st.markdown(f"""
            <div style='background:#101c2e; border:1px solid #1e3352; border-radius:8px;
                        padding:14px 18px; margin-bottom:10px; display:flex; align-items:center; gap:16px;'>
                <span style='font-size:22px;'>{icon}</span>
                <div>
                    <div style='font-family:Rajdhani,sans-serif; font-size:20px; font-weight:700; color:#00d4ff;'>{val}</div>
                    <div style='font-size:12px; color:#7a9bbf;'>{lbl}</div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    _, cta_center, _ = st.columns([1,1,1])
    with cta_center:
        st.link_button("🚀 Book Demo Langsung", WA_LINK_DEMO, use_container_width=True)

    st.markdown("""
    <div class='section-wrapper'>
        <div class='section-header'>Kata Mereka yang <span class='section-accent'>Sudah Merasakan</span></div>
        <div class='section-subheader'>Bisnis nyata, penghematan nyata</div>
    </div>
    """, unsafe_allow_html=True)

    t1, t2, t3 = st.columns(3)
    for col, (text, author, role, result) in zip([t1,t2,t3],[
        ("Sebelum pakai V-Guard, saya tidak pernah tahu kasir saya melakukan void hampir setiap malam. Sekarang semuanya ter-record dan saya bisa tidur tenang.",
         "Bpk. Timotius M.","Owner Kafe & Resto, Jakarta Selatan","Menghemat ±Rp 8 Juta/bulan"),
        ("Stok saya sering selisih tapi saya kira itu wajar. Ternyata ada kebocoran dari supplier. V-Guard langsung deteksi di hari pertama pemasangan.",
         "Ibu Riana S.","Pemilik Minimarket, 3 Cabang Tangerang","Selisih stok turun 94%"),
        ("Fitur H-7 reminder invoice sangat membantu cash flow saya. Tidak ada lagi piutang yang lupa ditagih lebih dari seminggu. Revenue collection naik signifikan.",
         "Bpk. Doni A.","Distributor FMCG, Bekasi","Collection rate +31%"),
    ]):
        with col:
            st.markdown(f"""
            <div class='testimonial-card'>
                <div class='stars'>★★★★★</div>
                <div class='testimonial-text'>"{text}"</div>
                <div class='testimonial-author'>{author}</div>
                <div class='testimonial-role'>{role}</div>
                <div style='margin-top:12px; padding:8px 12px; background:#00d4ff11;
                            border-radius:6px; font-size:12px; color:#00d4ff;
                            font-family:JetBrains Mono, monospace;'>✓ {result}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style='background: linear-gradient(135deg, #0d1a2e, #0a1628);
                padding: 48px; text-align: center; border-top: 1px solid #1e3352;'>
        <div style='font-family:Rajdhani,sans-serif; font-size:36px; font-weight:700; color:#e8f4ff; margin-bottom:12px;'>
            Siap Menutup Kebocoran Bisnis Anda?
        </div>
        <div style='font-size:15px; color:#7a9bbf; margin-bottom:28px;'>
            Konsultasi gratis 30 menit dengan tim V-Guard AI. Tidak ada kewajiban apapun.
        </div>
    </div>
    """, unsafe_allow_html=True)
    _, cta1, cta2, _ = st.columns([1,1,1,1])
    with cta1:
        st.link_button("📅 Book Demo Gratis", WA_LINK_DEMO, use_container_width=True)
    with cta2:
        st.link_button("💬 Chat Sekarang", WA_LINK_KONSUL, use_container_width=True)


# ============================================================================
# 8. PRODUK & HARGA — Invisible Tech Strategy (5 Tier)
# ============================================================================
elif menu == "📦 Produk & Harga":

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("<div style='padding: 40px 48px 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='margin-bottom: 6px;'>
        <span class='hero-badge'>📦 &nbsp; Ekosistem V-Guard AI &nbsp;·&nbsp; 5 Tier Perlindungan</span>
    </div>
    <div class='page-title'>Pilih Tingkat <span style='color:#00d4ff;'>Perlindungan</span> Bisnis Anda</div>
    <div class='page-subtitle' style='max-width:680px;'>
        Dari UMKM 1 kasir hingga korporasi multi-cabang — setiap tier mengaktifkan agen AI yang tepat
        untuk menutup kebocoran secara presisi tanpa ekspos teknologi ke kompetitor.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Data Paket ────────────────────────────────────────────────────────────
    PACKAGES = [
        {
            "key": "LITE", "name": "V-LITE",
            "badge_cls": "badge-entry", "badge_txt": "Entry Level",
            "focus": "Fondasi keamanan digital untuk usaha satu kasir",
            "price": "Rp 150rb", "period": "/ bulan", "setup": "Biaya pasang: Rp 250rb",
            "popular": False, "ultra": False,
            "features": [
                "Deteksi VOID & Transaksi Cancel",
                "Daily AI Summary via WhatsApp",
                "Dashboard Web Real-Time",
                "Laporan Kebocoran Otomatis",
                "Support Teknis via WhatsApp",
            ],
            "agents": [("🔍","The Auditor"),("🤝","The Liaison")],
            "wa_msg": "Halo Admin, saya ingin berlangganan paket *V-LITE* V-Guard AI. Mohon informasi selanjutnya.",
        },
        {
            "key": "PRO", "name": "V-PRO",
            "badge_cls": "badge-pro", "badge_txt": "Pro",
            "focus": "Otomasi admin, stok, & audit bank tanpa input manual",
            "price": "Rp 450rb", "period": "/ bulan", "setup": "Biaya pasang: Rp 750rb",
            "popular": True, "ultra": False,
            "features": [
                "Semua fitur V-LITE",
                "VCS Secure Integration (kasir otomatis)",
                "Bank Statement Audit Otomatis",
                "Input Invoice via OCR (PDF/Foto)",
                "Laporan PDF Terjadwal",
                "Support Prioritas 24/7",
            ],
            "agents": [("🔍","The Auditor"),("🤝","The Liaison"),("✍️","The Scribe")],
            "wa_msg": "Halo Admin, saya ingin berlangganan paket *V-PRO* V-Guard AI. Mohon informasi selanjutnya.",
        },
        {
            "key": "SIGHT", "name": "V-SIGHT",
            "badge_cls": "badge-sight", "badge_txt": "Pengawas Aktif",
            "focus": "Mata AI pengawas aktif — visual, stok & multi-cabang",
            "price": "Rp 1,2jt", "period": "/ bulan", "setup": "Biaya pasang: Rp 3,5jt",
            "popular": False, "ultra": False,
            "features": [
                "Semua fitur V-PRO",
                "V-Guard Proprietary Vision Engine (CCTV AI)",
                "Visual Cashier Audit — overlay transaksi real-time",
                "WhatsApp Fraud Alarm Instan 🚨",
                "H-7 Auto Collection Reminder",
                "Multi-Cabang Centralized Dashboard",
            ],
            "agents": [("🔍","The Auditor"),("🤝","The Liaison"),("✍️","The Scribe"),("👁️","The Visionary"),("🐕","The Watchdog")],
            "wa_msg": "Halo Admin, saya ingin berlangganan paket *V-SIGHT* V-Guard AI. Mohon informasi selanjutnya.",
        },
        {
            "key": "ENT", "name": "V-ENTERPRISE",
            "badge_cls": "badge-ent", "badge_txt": "Korporasi",
            "focus": "Kedaulatan data penuh — server privat & AI forensik",
            "price": "Mulai Rp 3,5jt", "period": "/ bulan", "setup": "Biaya pasang: Rp 10jt",
            "popular": False, "ultra": False,
            "features": [
                "Semua fitur V-SIGHT",
                "V-Guard Deep Learning Intelligence (Forensik AI)",
                "Dedicated Private Server",
                "Custom AI SOP per Divisi",
                "On-site Implementation Support",
                "Executive SLA 99.9% Uptime",
            ],
            "agents": [("🔍","The Auditor"),("🤝","The Liaison"),("✍️","The Scribe"),("👁️","The Visionary"),("🐕","The Watchdog"),("⚙️","The Automator"),("🧪","The Simulator")],
            "wa_msg": "Halo Admin, saya ingin berlangganan paket *V-ENTERPRISE* V-Guard AI. Mohon informasi selanjutnya.",
        },
        {
            "key": "ULTRA", "name": "V-ULTRA",
            "badge_cls": "badge-ultra", "badge_txt": "Executive",
            "focus": "Executive Dashboard & White-Label — 10 Elite AI Squad aktif penuh",
            "price": "Custom Quote", "period": "Harga khusus korporasi", "setup": "Konsultasi strategis gratis",
            "popular": False, "ultra": True,
            "features": [
                "Seluruh ekosistem V-ENTERPRISE",
                "White-Label Platform (brand perusahaan Anda)",
                "Executive BI Dashboard — C-Level View",
                "V-Guard Secure Liaison Protocol (integrasi ERP)",
                "10 Elite AI Squad aktif serentak",
                "Dedicated AI Strategist (personal account manager)",
            ],
            "agents": [("🔍","The Auditor"),("👁️","The Visionary"),("✍️","The Scribe"),("📣","The Growth Hacker"),("🤝","The Liaison"),("🧪","The Simulator"),("⚙️","The Automator"),("🐕","The Watchdog"),("🧠","The Core Brain"),("👔","The Concierge")],
            "wa_msg": "Halo Admin, saya ingin mendapatkan penawaran eksklusif paket *V-ULTRA* V-Guard AI. Mohon jadwalkan konsultasi strategis.",
        },
    ]

    # ── 5 Kartu Produk ────────────────────────────────────────────────────────
    st.markdown("<div style='padding: 28px 40px 12px;'>", unsafe_allow_html=True)
    cols = st.columns(5, gap="small")

    for col, pkg in zip(cols, PACKAGES):
        with col:
            agent_html = "".join([
                f"<div class='{'agent-pill ultra-pill' if pkg['ultra'] else 'agent-pill'}'>"
                f"<div class='dot'></div>{icon} {aname}</div>"
                for icon, aname in pkg["agents"]
            ])
            feat_cls  = "pkg-feature ultra-feat" if pkg["ultra"] else "pkg-feature"
            feat_html = "".join([
                f"<div class='{feat_cls}'><span class='ck'>✓</span>{f}</div>"
                for f in pkg["features"]
            ])
            label_html = ""
            if pkg["popular"]:
                label_html = "<div class='hot-label'>⭐ TERLARIS</div>"
            elif pkg["ultra"]:
                label_html = "<div class='ultra-label'>👑 EKSKLUSIF</div>"

            card_cls  = "pkg-card ultra" if pkg["ultra"] else ("pkg-card popular-card" if pkg["popular"] else "pkg-card")
            name_cls  = "pkg-name ultra" if pkg["ultra"] else "pkg-name"
            price_cls = "pkg-price ultra" if pkg["ultra"] else "pkg-price"
        html_content = f"""
        <div class='{card_cls}'>
            {label_html}
            <div class='{name_cls}'>{pkg['name']}</div>
            <div class='{price_cls}'>{pkg['price']}</div>
            <div class='pkg-setup'>{pkg['setup']}</div>
            <hr class='pricing-divider'>
            <div class='pkg-features'>{feat_html}</div>
            <a href='{whatsapp_url}' class='{btn_cls}' target='_blank'>{btn_text}</a>
            <div style='font-size:10px; color:#4a6a8a; font-family:monospace; margin-top:10px;'>
                    V-GUARD SECURE PROTOCOL v1.0
            </div>
        """ # <--- INI ADALAH PENUTUP YANG BIKIN ERROR JIKA HILANG
        st.markdown(html_content, unsafe_allow_html=True)
            <div class='{card_cls}'>
                {label_html}
                <div><span class='tier-badge {pkg["badge_cls"]}'>{pkg["badge_txt"]}</span></div>
                <div class='{name_cls}'>{pkg["name"]}</div>
                <div class='pkg-focus'>{pkg["focus"]}</div>
                <hr class='pkg-divider'>
                <div class='{price_cls}'>{pkg["price"]}</div>
                <div class='pkg-period'>{pkg["period"]}</div>
                <div class='pkg-setup'>{pkg["setup"]}</div>
                <hr class='pkg-divider'>
                {feat_html}
                <hr class='pkg-divider'>
                <div style='font-size:10px; color:#4a6a8a; font-family:JetBrains Mono,monospace;
                            text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;'>
                    Agent Squad Aktif
                </div>
                <div class='agent-row'>{agent_html}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            wa_url = f"https://wa.me/{WA_NUMBER}?text={urllib.parse.quote(pkg['wa_msg'])}"

            if pkg["ultra"]:
                st.markdown(f"""
                <a href="{wa_url}" target="_blank" style="display:block; width:100%;
                   background: linear-gradient(135deg, #b8860b, #ffd700, #b8860b);
                   color: #000 !important; font-family: Rajdhani, sans-serif;
                   font-size: 13px; font-weight: 700; border-radius: 7px;
                   padding: 12px 10px; text-align: center; text-decoration: none;
                   letter-spacing: 0.5px; box-shadow: 0 4px 20px #ffd70033;">
                    👔 Hubungi Admin
                </a>
                """, unsafe_allow_html=True)
            else:
                st.link_button(f"Berlangganan {pkg['name']}", wa_url, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Catatan Invisible Tech ─────────────────────────────────────────────────
    st.markdown("""
    <div style='padding: 0 48px 8px;'>
        <div style='background:#0a1220; border:1px solid #1e3352; border-radius:8px;
                    padding:14px 20px; font-size:11px; color:#4a6a8a;
                    font-family:JetBrains Mono, monospace; line-height:1.8;'>
            🛡️ &nbsp;Seluruh teknologi deteksi, visi, dan analitik yang beroperasi di dalam platform V-Guard AI
            adalah <b style='color:#7a9bbf;'>proprietary intellectual property</b> dari V-Guard AI Intelligence.
            Tidak ada ketergantungan pada platform pihak ketiga yang terbuka.
            Arsitektur bersifat <b style='color:#7a9bbf;'>air-gapped optional</b> pada tier Enterprise ke atas.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)

    # ── 10 Elite AI Squad ─────────────────────────────────────────────────────
    st.markdown("""
    <div style='padding: 0 48px;'>
        <div class='comp-section-title'>
            🤖 10 Elite AI Squad — <span style='color:#00d4ff;'>Siapa & Bertugas Apa?</span>
        </div>
        <div class='comp-section-sub'>
            Setiap paket mengaktifkan kombinasi agen yang berbeda. Semakin tinggi tier,
            semakin banyak agen yang beroperasi secara serentak — 24/7, tanpa supervisi manual.
        </div>
    </div>
    """, unsafe_allow_html=True)

    AGENTS = [
        {
            "icon":"🔍","name":"The Auditor","role":"Pemindai Integritas Transaksi",
            "desc":"Memverifikasi setiap transaksi kasir terhadap pola anomali, VOID mencurigakan, dan duplikasi dalam rentang waktu sempit menggunakan V-Guard Deep Learning Intelligence.",
            "tiers":["LITE","PRO","SIGHT","ENT","ULTRA"],
        },
        {
            "icon":"🤝","name":"The Liaison","role":"Pengirim Notifikasi & Laporan",
            "desc":"Mengelola seluruh komunikasi otomatis ke Owner: daily summary, fraud alarm real-time, dan invoice reminder melalui V-Guard Secure Liaison Protocol.",
            "tiers":["LITE","PRO","SIGHT","ENT","ULTRA"],
        },
        {
            "icon":"✍️","name":"The Scribe","role":"Otomasi Dokumen & Admin",
            "desc":"Membaca invoice supplier via metode pengenalan karakter cerdas, mengupdate stok secara otomatis, membuat laporan PDF terjadwal, dan merekonsiliasi catatan tanpa input manual.",
            "tiers":["PRO","SIGHT","ENT","ULTRA"],
        },
        {
            "icon":"👁️","name":"The Visionary","role":"Analis Visual Cashier (CCTV AI)",
            "desc":"Mengoperasikan V-Guard Proprietary Vision Engine untuk mengoverlay data transaksi secara real-time di atas rekaman kamera kasir. Bukti visual tak terbantahkan.",
            "tiers":["SIGHT","ENT","ULTRA"],
        },
        {
            "icon":"🐕","name":"The Watchdog","role":"Penjaga Anomali Real-Time",
            "desc":"Beroperasi 24/7 memantau ambang batas yang dikonfigurasi Owner. Memicu alarm WhatsApp instan saat pola mencurigakan terdeteksi, sebelum kerugian terjadi.",
            "tiers":["SIGHT","ENT","ULTRA"],
        },
        {
            "icon":"⚙️","name":"The Automator","role":"Orkestrator Alur Kerja Bisnis",
            "desc":"Mengotomasi alur kerja berulang lintas divisi: pengingat piutang H-7, rekonsiliasi cabang, distribusi laporan ke tim, dan trigger aksi berbasis kondisi data.",
            "tiers":["ENT","ULTRA"],
        },
        {
            "icon":"🧪","name":"The Simulator","role":"Modeler Skenario & Risiko",
            "desc":"Mensimulasikan dampak finansial dari berbagai skenario operasional menggunakan V-Guard Deep Learning Intelligence — membantu manajemen membuat keputusan berbasis data.",
            "tiers":["ENT","ULTRA"],
        },
        {
            "icon":"📣","name":"The Growth Hacker","role":"Analis Performa Revenue",
            "desc":"Mengidentifikasi produk terlaris, tren penjualan musiman, dan peluang upsell berdasarkan data transaksi historis. Rekomendasi strategi pertumbuhan otomatis.",
            "tiers":["ULTRA"],
        },
        {
            "icon":"🧠","name":"The Core Brain","role":"Strategist AI Eksekutif",
            "desc":"Agen orkestrasi tingkat tertinggi. Mengintegrasikan output semua agen lain, menyaring insight kritis, dan menyajikannya dalam Executive Dashboard untuk C-Level.",
            "tiers":["ULTRA"],
        },
        {
            "icon":"👔","name":"The Concierge","role":"Koordinator White-Label & Klien",
            "desc":"Mengelola kustomisasi platform: branding, SLA, onboarding klien baru (untuk reseller), dan personalisasi alur kerja per entitas bisnis.",
            "tiers":["ULTRA"],
        },
    ]

    TIER_MAP = {
        "LITE":  ("td-lite","V-LITE"),
        "PRO":   ("td-pro","V-PRO"),
        "SIGHT": ("td-sight","V-SIGHT"),
        "ENT":   ("td-ent","V-ENT"),
        "ULTRA": ("td-ultra","V-ULTRA"),
    }

    st.markdown("<div style='padding: 0 48px 56px;'>", unsafe_allow_html=True)
    agent_col_a, agent_col_b = st.columns(2, gap="large")

    for i, agent in enumerate(AGENTS):
        col = agent_col_a if i % 2 == 0 else agent_col_b
        with col:
            tiers_html = "".join([
                f"<span class='tier-dot {TIER_MAP[t][0]}'>{TIER_MAP[t][1]}</span>"
                for t in agent["tiers"]
            ])
            st.markdown(f"""
            <div class='agent-comp-card'>
                <div class='agent-comp-name'>{agent["icon"]} {agent["name"]}</div>
                <div class='agent-comp-role'>{agent["role"]}</div>
                <div style='font-size:12px; color:#7a9bbf; line-height:1.6; margin-bottom:10px;'>{agent["desc"]}</div>
                <div>
                    <span style='font-size:10px; color:#4a6a8a; font-family:JetBrains Mono,monospace; margin-right:6px;'>AKTIF DI:</span>
                    {tiers_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Final CTA Strip ───────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #0d1a2e, #0a1222);
                padding: 40px 48px; text-align: center; border-top: 1px solid #1e3352;'>
        <div style='font-family:Rajdhani,sans-serif; font-size:30px; font-weight:700; color:#e8f4ff; margin-bottom:10px;'>
            Tidak yakin paket mana yang tepat?
        </div>
        <div style='font-size:14px; color:#7a9bbf; margin-bottom:24px;'>
            Tim V-Guard AI akan membantu Anda memilih kombinasi agen yang paling efisien
            untuk skala bisnis dan anggaran Anda — gratis, tanpa tekanan.
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, cta_left, cta_right, _ = st.columns([1,1,1,1])
    with cta_left:
        wa_konsul_url = f"https://wa.me/{WA_NUMBER}?text={urllib.parse.quote('Halo Pak Erwin, saya ingin konsultasi memilih paket V-Guard AI yang tepat untuk bisnis saya.')}"
        st.link_button("💬 Konsultasi Pemilihan Paket", wa_konsul_url, use_container_width=True)
    with cta_right:
        st.link_button("📅 Book Demo Gratis", WA_LINK_DEMO, use_container_width=True)


# ============================================================================
# 9. KALKULATOR ROI
# ============================================================================
elif menu == "📊 Kalkulator ROI":
    st.markdown("<div style='padding: 40px 48px;'>", unsafe_allow_html=True)
    st.markdown("<div class='page-title'>📊 Kalkulator <span style='color:#00d4ff;'>Kerugian & ROI</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Hitung berapa banyak Rupiah yang bocor dari bisnis Anda setiap bulan</div>", unsafe_allow_html=True)

    roi_l, roi_r = st.columns([1, 1.2], gap="large")

    with roi_l:
        st.markdown("<div style='background:#101c2e; border:1px solid #1e3352; border-radius:14px; padding:28px;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-family:Rajdhani,sans-serif; font-size:18px; font-weight:700; color:#e8f4ff; margin-bottom:20px;'>📋 Data Bisnis Anda</p>", unsafe_allow_html=True)
        omzet   = st.number_input("Omzet Bulanan (Rp)", value=100_000_000, step=5_000_000, format="%d")
        jenis   = st.selectbox("Jenis Bisnis", ["Kafe / Resto","Retail / Minimarket","Gudang / Distributor","Korporasi Multi-Cabang"])
        cabang  = st.number_input("Jumlah Kasir / Cabang", value=1, min_value=1, max_value=100)
        leak    = st.slider("Estimasi % Kebocoran (Fraud, Void, Stok)", 1, 25, 5)
        paket_rec = st.selectbox("Paket yang Diminati", [
            "V-LITE (Rp 150rb/bln)","V-PRO (Rp 450rb/bln)",
            "V-SIGHT (Rp 1,2Jt/bln)","V-ENTERPRISE (Mulai Rp 3,5Jt/bln)","V-ULTRA (Custom)",
        ])
        paket_cost_map = {
            "V-LITE (Rp 150rb/bln)": 150000,
            "V-PRO (Rp 450rb/bln)":  450000,
            "V-SIGHT (Rp 1,2Jt/bln)": 1200000,
            "V-ENTERPRISE (Mulai Rp 3,5Jt/bln)": 3500000,
            "V-ULTRA (Custom)": 0,
        }
        biaya_vguard = paket_cost_map[paket_rec]
        st.markdown("</div>", unsafe_allow_html=True)

    with roi_r:
        loss_monthly  = omzet * (leak / 100)
        loss_yearly   = loss_monthly * 12
        saved_monthly = loss_monthly * 0.88
        saved_yearly  = saved_monthly * 12
        net_roi       = saved_monthly - biaya_vguard if biaya_vguard > 0 else saved_monthly
        roi_pct       = (net_roi / biaya_vguard * 100) if biaya_vguard > 0 else 0
        payback_days  = (biaya_vguard / saved_monthly * 30) if saved_monthly > 0 and biaya_vguard > 0 else 0

        st.markdown(f"""
        <div style='background:#0d1a2e; border:1px solid #ff3b5c55; border-left:3px solid #ff3b5c;
                    border-radius:14px; padding:24px; margin-bottom:16px;'>
            <div class='roi-label'>⚠️ Estimasi Kebocoran per Bulan</div>
            <div class='roi-result-big' style='color:#ff3b5c;'>Rp {loss_monthly:,.0f}</div>
            <div class='roi-label' style='margin-top:6px;'>Per tahun: <b style='color:#ff3b5c;'>Rp {loss_yearly:,.0f}</b></div>
        </div>
        <div style='background:#0d1a2e; border:1px solid #00e67655; border-left:3px solid #00e676;
                    border-radius:14px; padding:24px; margin-bottom:16px;'>
            <div class='roi-label'>✅ Estimasi Penyelamatan dengan V-Guard (88%)</div>
            <div class='roi-result-big' style='color:#00e676;'>Rp {saved_monthly:,.0f}</div>
            <div class='roi-label' style='margin-top:6px;'>Per tahun: <b style='color:#00e676;'>Rp {saved_yearly:,.0f}</b></div>
        </div>
        """, unsafe_allow_html=True)

        r1, r2, r3, r4, r5 = st.columns(5)
        with r1:
            st.markdown(f"""
            <div class='stat-card' style='padding:18px;'>
                <div style='font-family:Rajdhani,sans-serif; font-size:26px; font-weight:700; color:#00d4ff;'>Rp {net_roi:,.0f}</div>
                <div class='stat-label'>Net ROI / Bulan</div>
            </div>""", unsafe_allow_html=True)
        with r2:
            st.markdown(f"""
            <div class='stat-card' style='padding:18px;'>
                <div style='font-family:Rajdhani,sans-serif; font-size:26px; font-weight:700; color:#00d4ff;'>{'∞' if roi_pct == 0 else f'{roi_pct:.0f}%'}</div>
                <div class='stat-label'>Return on Investment</div>
            </div>""", unsafe_allow_html=True)
        with r3:
            st.markdown(f"""
            <div class='stat-card' style='padding:18px;'>
                <div style='font-family:Rajdhani,sans-serif; font-size:26px; font-weight:700; color:#00d4ff;'>{'—' if payback_days == 0 else f'{payback_days:.0f} Hari'}</div>
                <div class='stat-label'>Balik Modal</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        wa_roi_text = urllib.parse.quote(
            f"Halo Pak Erwin, saya sudah coba kalkulator ROI V-Guard.\n"
            f"Omzet saya Rp {omzet:,.0f}/bln, estimasi kebocoran {leak}%.\n"
            f"Saya tertarik dengan paket {paket_rec}. Bisa dibantu konsultasi?"
        )
        st.link_button("📲 Konsultasi Hasil ROI via WhatsApp", f"https://wa.me/{WA_NUMBER}?text={wa_roi_text}", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================================
# 10. PORTAL KLIEN
# ============================================================================
elif menu == "🔑 Portal Klien":
    st.markdown("<div style='padding: 40px 48px;'>", unsafe_allow_html=True)
    st.markdown("<div class='page-title'>🔑 Portal <span style='color:#00d4ff;'>Klien</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Login ke dashboard monitoring Anda atau daftar sebagai klien baru</div>", unsafe_allow_html=True)

    url_sheets = "https://docs.google.com/spreadsheets/d/17OJpYRGTWdQ0ZldSxp-3HdyW4AN_RKuJkCWVpYbtNE8/edit?usp=sharing"
    df_clients = None
    try:
        from streamlit_gsheets import GSheetsConnection
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_clients = conn.read(spreadsheet=url_sheets, ttl="0")
    except Exception:
        pass

    tab_log, tab_reg = st.tabs(["🔐 Login Dashboard","📝 Daftar / Order Baru"])

    with tab_log:
        st.markdown("<div style='max-width:480px; margin: 32px auto;'>", unsafe_allow_html=True)
        st.markdown("""
        <div class='login-card'>
            <div style='text-align:center; margin-bottom:24px;'>
                <div style='font-size:40px;'>🛡️</div>
                <div style='font-family:Rajdhani,sans-serif; font-size:22px; font-weight:700; color:#e8f4ff;'>Masuk ke Sentinel Dashboard</div>
                <div style='font-size:13px; color:#7a9bbf; margin-top:4px;'>Masukkan kredensial yang dikirim saat aktivasi</div>
            </div>
        </div>""", unsafe_allow_html=True)

        user_id_input = st.text_input("User ID Klien", placeholder="Contoh: VGD-V-PRO-123")
        password      = st.text_input("Password", type="password", placeholder="Password dari email aktivasi")
        btn_login     = st.button("🚀 Masuk ke Dashboard", type="primary", use_container_width=True)

        if btn_login:
            if df_clients is not None and user_id_input in df_clients["UserID"].values:
                client_info  = df_clients[df_clients["UserID"] == user_id_input].iloc[0]
                paket_aktif  = client_info["Paket"]
                status_klien = client_info["Status"]
                nama_klien_login = client_info["Nama Klien"]

                if status_klien == "Aktif":
                    st.success(f"✅ Selamat Datang, **{nama_klien_login}**! Lisensi **{paket_aktif}** Anda Aktif.")
                    st.divider()
                    link_map = {
                        "V-LITE":       "https://vguard-ai.railway.app/lite-vision",
                        "V-PRO":        "https://vguard-ai.railway.app/pro-audit",
                        "V-SIGHT":      "https://vguard-ai.railway.app/sight-live",
                        "V-ENTERPRISE": "https://vguard-ai.railway.app/enterprise-core",
                        "V-ULTRA":      "https://vguard-ai.railway.app/ultra-exec",
                    }
                    url_tujuan = link_map.get(paket_aktif, "#")
                    st.link_button(f"🚀 Buka Panel {paket_aktif}", url_tujuan, use_container_width=True)
                    st.divider()
                    m1, m2, m3 = st.columns(5)
                    if paket_aktif == "V-LITE":
                        m1.metric("Kasir","Online"); m2.metric("Fraud Alert","0"); m3.info("Daily Summary Mode")
                    elif paket_aktif == "V-PRO":
                        m1.metric("VCS Sync","Active"); m2.metric("Audit","Clear"); m3.metric("Protected Rev.","Rp 1.2M")
                    elif paket_aktif == "V-SIGHT":
                        m1.metric("CCTV AI","Streaming"); m2.metric("Anomali","0"); m3.metric("Visual Audit","100%")
                    elif paket_aktif in ("V-ENTERPRISE","V-ULTRA"):
                        m1.metric("Forensic","99.9%"); m2.metric("Integrity","Secure"); m3.metric("Drift","0%")
                else:
                    st.error("⚠️ Akun belum AKTIF. Selesaikan pembayaran atau hubungi Admin.")
                    st.link_button("📲 Aktivasi via WhatsApp", f"https://wa.me/{WA_NUMBER}")
            else:
                if btn_login:
                    st.error("❌ User ID tidak ditemukan atau database tidak tersedia.")
                    st.caption("Pastikan User ID sesuai yang dikirim saat aktivasi, atau hubungi Admin.")

        st.markdown("</div>", unsafe_allow_html=True)

    with tab_reg:
        reg_l, reg_r = st.columns([1.3, 1], gap="large")

        with reg_l:
            st.markdown("<div style='margin-top:16px;'>", unsafe_allow_html=True)
            with st.form("pendaftaran_umum"):
                st.markdown("<p style='font-family:Rajdhani,sans-serif; font-size:18px; font-weight:700; color:#e8f4ff; margin-bottom:4px;'>📋 Form Pendaftaran Klien</p>", unsafe_allow_html=True)
                nama_klien = st.text_input("Nama Lengkap / Owner *")
                nama_usaha = st.text_input("Nama Usaha *")
                no_hp      = st.text_input("Nomor WhatsApp (Aktif) *", placeholder="Contoh: 62812xxxx")
                upload_ktp = st.file_uploader("Upload Foto KTP (Verifikasi)", type=["png","jpg","jpeg"])
                produk     = st.selectbox("Pilih Paket Aktivasi *", ["V-LITE","V-PRO","V-SIGHT","V-ENTERPRISE","V-ULTRA"])

                with st.expander("📄 Syarat & Ketentuan"):
                    st.markdown("""
**1. Pembayaran:** Aktivasi dimulai setelah biaya diverifikasi Admin.
**2. Keamanan Data:** Data terenkripsi, tidak disebarkan ke pihak ketiga.
**3. Refund Policy:** Tidak ada refund setelah sistem aktif.
**4. Support:** Technical support 24/7 via WhatsApp.
                    """)

                setuju_tc = st.checkbox("Saya telah membaca dan menyetujui Syarat & Ketentuan.")
                submit    = st.form_submit_button("🚀 Daftar & Dapatkan Akses AI", type="primary", use_container_width=True)

                if submit:
                    if setuju_tc and nama_klien and no_hp and nama_usaha:
                        st.session_state.db_umum.append({
                            "Nama Klien": nama_klien, "Produk": produk,
                            "Status": "🛡️ Menunggu Pembayaran",
                            "WhatsApp": no_hp, "Nama Usaha": nama_usaha, "Nilai Kontrak": "0",
                        })
                        try:
                            from streamlit_gsheets import GSheetsConnection
                            conn = st.connection("gsheets", type=GSheetsConnection)
                            data_baru     = pd.DataFrame([{"Nama Klien": nama_klien, "Produk": produk, "Status": "⏳ Pending", "Nilai Kontrak": "Proses"}])
                            existing_data = conn.read(worksheet="Pendaftaran", ttl=0)
                            updated_df    = pd.concat([existing_data, data_baru], ignore_index=True)
                            conn.update(worksheet="Pendaftaran", data=updated_df)
                        except Exception:
                            pass
                        st.success(f"✅ Pendaftaran berhasil! Invoice akan dikirim ke WhatsApp **{no_hp}** dalam 1x24 jam.")
                        st.balloons()
                    else:
                        st.error("❌ Mohon isi semua field wajib (*) dan setujui T&C.")
            st.markdown("</div>", unsafe_allow_html=True)

        with reg_r:
            st.markdown("""
            <div style='margin-top:44px; background:#101c2e; border:1px solid #1e3352; border-radius:14px; padding:24px;'>
                <div style='font-family:Rajdhani,sans-serif; font-size:17px; font-weight:700; color:#e8f4ff; margin-bottom:16px;'>
                    ✅ Setelah Mendaftar:
                </div>
            </div>
            """, unsafe_allow_html=True)
            for icon, step in [
                ("1️⃣","Invoice dikirim via WhatsApp dalam 1×24 jam"),
                ("2️⃣","Transfer ke rekening yang tertera di invoice"),
                ("3️⃣","Konfirmasi pembayaran ke Admin"),
                ("4️⃣","Tim V-Guard setup & aktivasi sistem Anda"),
                ("5️⃣","Kredensial login dikirim & training singkat"),
            ]:
                st.markdown(f"""
                <div style='display:flex; gap:12px; align-items:flex-start; margin-bottom:12px;'>
                    <span style='font-size:18px;'>{icon}</span>
                    <span style='font-size:13px; color:#7a9bbf; line-height:1.5;'>{step}</span>
                </div>""", unsafe_allow_html=True)

            st.markdown("<div style='margin-top:20px;'>", unsafe_allow_html=True)
            st.link_button("📲 Tanya Langsung via WA", WA_LINK_KONSUL, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================================
# 11. ADMIN CONTROL CENTER
# ============================================================================
elif menu == "⚙️ Admin Control Center":
    if not st.session_state.admin_logged_in:
        st.warning("⚠️ Halaman ini hanya untuk Admin. Gunakan panel Login di sidebar.")
        st.stop()

    st.markdown("<div style='padding: 32px 48px;'>", unsafe_allow_html=True)
    st.markdown("<div class='page-title'>⚙️ Admin <span style='color:#00d4ff;'>Control Center</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Founder Edition — V-Guard AI Intelligence</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("---")
        menu_admin = st.selectbox("Admin Menu", [
            "Dashboard Utama",
            "Aktivasi Nasabah Baru",
            "Monitoring & Fraud Scanner",
            "Database Klien",
        ])

    # ── Dashboard Utama ──────────────────────────────────────────────────────
    if menu_admin == "Dashboard Utama":
        a1, a2, a3, a4 = st.columns(4)
        for col, (val, lbl) in zip([a1,a2,a3,a4],[
            (str(len(st.session_state.db_umum)), "Total Klien"),
            ("Rp 45.2 Jt","Pendapatan Bulan Ini"),
            ("99.8%","System Uptime"),
            (ai_status_msg,"AI Engine"),
        ]):
            with col:
                st.markdown(f"""
                <div class='admin-metric'>
                    <div class='admin-metric-val'>{val}</div>
                    <div class='admin-metric-lbl'>{lbl}</div>
                </div>""", unsafe_allow_html=True)

        st.divider()
        st.subheader("🛡️ Elite AI Squad — 10 Agents Status")
        ag1, ag2, ag3, ag4, ag5 = st.columns(5)
        with ag1: st.success("🔍 The Auditor — Active")
        with ag2: st.success("👁️ The Visionary — Active")
        with ag3: st.success("📣 The Growth Hacker — Active")
        with ag4: st.success("🤝 The Liaison — Active")
        with ag5: st.success("✍️ The Scribe — Active")
        ag6, ag7, ag8, ag9, ag10 = st.columns(5)
        with ag6:  st.info("🧪 The Simulator — Standby")
        with ag7:  st.info("⚙️ The Automator — Standby")
        with ag8:  st.info("🐕 The Watchdog — Standby")
        with ag9:  st.info("🧠 The Core Brain — Standby")
        with ag10: st.info("👔 The Concierge — Standby")

    # ── Aktivasi Nasabah Baru ────────────────────────────────────────────────
    elif menu_admin == "Aktivasi Nasabah Baru":
        st.subheader("📋 Antrean Aktivasi Klien")
        if not st.session_state.db_umum:
            st.info("Belum ada pendaftar baru di sesi ini.")
        else:
            df_real = pd.DataFrame(st.session_state.db_umum)
            st.dataframe(df_real, use_container_width=True)
            st.divider()
            k_pil = st.selectbox("Pilih Klien untuk Diproses", df_real["Nama Klien"].tolist())
            d_sel = df_real[df_real["Nama Klien"] == k_pil].iloc[0]
            col_inv, col_act = st.columns(2)
            harga_map = {
                "V-LITE":"Rp 150.000","V-PRO":"Rp 450.000",
                "V-SIGHT":"Rp 1.200.000","V-ENTERPRISE":"Rp 3.500.000","V-ULTRA":"Custom",
            }
            nom = harga_map.get(d_sel["Produk"],"Rp 150.000")

            with col_inv:
                st.subheader("💰 Kirim Tagihan")
                inv_text = f"🛡️ *INVOICE V-GUARD*\nYth. *{k_pil}*\nPaket: {d_sel['Produk']}\nTotal: {nom}\nTransfer ke BCA 3450074658 a.n Erwin Sinaga."
                st.link_button("📲 Kirim Invoice via WhatsApp", f"https://wa.me/{WA_NUMBER}?text={urllib.parse.quote(inv_text)}")

            with col_act:
                st.subheader("✅ Aktivasi Klien")
                if st.button(f"Aktifkan {k_pil}", type="primary"):
                    try:
                        random_num  = "".join(random.choices(string.digits, k=3))
                        new_userid  = f"VGD-{d_sel['Produk']}-{random_num}"
                        new_password = f"vguard{random_num}"
                        link_map = {
                            "V-LITE":"https://vguard-ai.railway.app/lite",
                            "V-PRO":"https://vguard-ai.railway.app/pro",
                            "V-SIGHT":"https://vguard-ai.railway.app/sight",
                            "V-ENTERPRISE":"https://vguard-ai.railway.app/enterprise",
                            "V-ULTRA":"https://vguard-ai.railway.app/ultra",
                        }
                        url_tujuan = link_map.get(d_sel["Produk"],"#")
                        pesan_wa   = (
                            f"🛡️ *AKTIVASI V-GUARD BERHASIL* 🛡️\n\nHalo Pak *{k_pil}*,\n"
                            f"Sentinel AI paket *{d_sel['Produk']}* AKTIF.\n\n"
                            f"🔑 *DATA AKSES:*\n- User ID: `{new_userid}`\n- Password: `{new_password}`\n\n"
                            f"🌐 Dashboard: {url_tujuan}\n\nSimpan data ini baik-baik."
                        )
                        st.success("✅ ID Berhasil Dibuat!")
                        st.code(f"User ID: {new_userid}  |  Password: {new_password}")
                        st.link_button("📲 Kirim Data Login ke Klien", f"https://wa.me/{WA_NUMBER}?text={urllib.parse.quote(pesan_wa)}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ── Monitoring & Fraud Scanner ───────────────────────────────────────────
    elif menu_admin == "Monitoring & Fraud Scanner":
        st.subheader("💰 AI Budget Guard")
        total_omset, batas_anggaran, persen_terpakai, status_warning = hitung_budget_guard(
            st.session_state.db_umum, st.session_state.api_cost_total
        )
        bg1, bg2, bg3 = st.columns(3)
        bg1.metric("Total Omset Kontrak",     f"Rp {total_omset:,.0f}")
        bg2.metric("Batas Anggaran API (20%)",f"Rp {batas_anggaran:,.0f}")
        bg3.metric("Biaya API Terpakai",      f"Rp {st.session_state.api_cost_total:,.0f}", delta=f"{persen_terpakai:.1f}%")
        st.progress(min(persen_terpakai / 100, 1.0))
        if status_warning:
            st.warning(f"⚠️ BUDGET ALERT: {persen_terpakai:.1f}% dari batas. Optimalkan frekuensi AI.")
        else:
            st.success(f"✅ Anggaran AI aman — {persen_terpakai:.1f}% terpakai.")

        st.divider()
        st.subheader("🛡️ Sentinel Fraud Scanner")
        df_trx    = get_sample_transaksi()
        hasil_scan = scan_fraud_lokal(df_trx)
        n_void, n_fraud, n_sus = len(hasil_scan["void"]), len(hasil_scan["fraud"]), len(hasil_scan["suspicious"])

        fs1, fs2, fs3 = st.columns(3)
        fs1.metric("🚫 Void/Cancel",    n_void,  delta="Tidak Wajar" if n_void  else "Aman")
        fs2.metric("🔁 Duplikat Kasir", n_fraud, delta="Terdeteksi"  if n_fraud else "Aman")
        fs3.metric("💸 Selisih Saldo",  n_sus,   delta="Anomali"     if n_sus   else "Aman")

        tab_v, tab_f, tab_s = st.tabs(["🚫 VOID/Cancel","🔁 Duplikat","💸 Selisih Saldo"])
        with tab_v:
            if not hasil_scan["void"].empty:
                st.error("⚠️ Transaksi VOID mencurigakan ditemukan!")
                st.dataframe(hasil_scan["void"][["ID_Transaksi","Cabang","Kasir","Jumlah","Waktu","Status"]], use_container_width=True)
            else:
                st.success("✅ Tidak ada VOID mencurigakan.")
        with tab_f:
            if not hasil_scan["fraud"].empty:
                st.error("⚠️ Pola duplikat dalam < 5 menit terdeteksi!")
                st.dataframe(hasil_scan["fraud"][["ID_Transaksi","Cabang","Kasir","Jumlah","selisih_menit"]], use_container_width=True)
            else:
                st.success("✅ Tidak ada pola duplikat.")
        with tab_s:
            if not hasil_scan["suspicious"].empty:
                st.error("⚠️ Selisih saldo fisik vs sistem ditemukan!")
                st.dataframe(hasil_scan["suspicious"][["ID_Transaksi","Cabang","Kasir","Saldo_Fisik","Saldo_Sistem","selisih_saldo"]], use_container_width=True)
            else:
                st.success("✅ Saldo seimbang.")

        if model_vguard:
            if st.button("🤖 Jalankan AI Deep Scan", type="primary"):
                with st.spinner("🧠 Sentinel AI menganalisis..."):
                    try:
                        prompt = f"""Anda adalah Sentinel Fraud AI V-Guard. Analisis data transaksi berikut dan berikan:
1. Indikasi Void/Cancel tidak wajar
2. Pola transaksi duplikat/mencurigakan
3. Selisih saldo fisik vs sistem
4. Rekomendasi tindakan Owner
Data: {df_trx.to_string(index=False)}
Jawab dalam format poin-poin ringkas."""
                        response = model_vguard.generate_content(prompt)
                        st.session_state.api_cost_total += 200
                        st.markdown("### 🤖 Hasil AI Deep Scan:")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Error AI: {e}")
        else:
            st.info("ℹ️ Sambungkan AI API Key untuk Deep Scan.")

        st.divider()
        st.subheader("🚨 Owner Alert System")
        ada_ancaman = n_void > 0 or n_fraud > 0 or n_sus > 0
        if ada_ancaman:
            st.error("🚨 FRAUD TERDETEKSI — Kirim peringatan ke Owner sekarang!")
            cabang_set = set()
            for df_part in hasil_scan.values():
                if not df_part.empty and "Cabang" in df_part.columns:
                    cabang_set.update(df_part["Cabang"].unique())
            for cabang in sorted(cabang_set):
                st.link_button(f"📲 Alert Owner — {cabang}", buat_link_wa_alert(cabang), use_container_width=True)
        else:
            st.success("✅ Tidak ada ancaman aktif.")

        st.divider()
        st.subheader("🧠 The Core Brain — AI Strategist")
        user_query = st.text_area("Konsultasi Strategi:", key="admin_query")
        if st.button("Jalankan AI Audit"):
            if model_vguard and user_query:
                with st.spinner("🧠 Menganalisis..."):
                    try:
                        context  = f"Anda adalah Core Brain V-Guard. Jawab Founder Erwin Sinaga secara taktis: {user_query}"
                        response = model_vguard.generate_content(context)
                        st.session_state.api_cost_total += 200
                        st.markdown("### 🤖 Respon AI:")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Error AI: {e}")
            else:
                st.warning("⚠️ Masukkan query dan pastikan API Key terpasang.")

    # ── Database Klien ───────────────────────────────────────────────────────
    elif menu_admin == "Database Klien":
        st.subheader("🗄️ Database Klien V-Guard")
        if st.session_state.db_umum:
            df_db = pd.DataFrame(st.session_state.db_umum)
            st.dataframe(df_db, use_container_width=True)
            csv = df_db.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Database (CSV)", data=csv, file_name="vguard_clients.csv", mime="text/csv")
        else:
            st.info("Database masih kosong di sesi ini.")

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================================
# 12. FOOTER
# ============================================================================
st.markdown("""
<div style='background:#060b14; border-top:1px solid #1e3352; padding:28px 48px;
            display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;'>
    <div>
        <span style='font-family:Rajdhani,sans-serif; font-size:18px; font-weight:700; color:#00d4ff;'>🛡️ V-Guard AI Intelligence</span>
        <span style='color:#7a9bbf; font-size:12px; margin-left:12px;'>Founder Edition ©2026</span>
    </div>
    <div style='font-size:12px; color:#7a9bbf;'>
        Digitizing Trust · Eliminating Leakage · Protecting Every Rupiah
    </div>
</div>
""", unsafe_allow_html=True)
