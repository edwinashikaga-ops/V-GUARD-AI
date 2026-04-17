# =============================================================================
# V-GUARD AI INTELLIGENCE — app.py  (V-GUARD AI Ecosystem ©2026)
# Full Rewrite — Professional SaaS Edition
# =============================================================================

import streamlit as st
import os
import urllib.parse
import hashlib
import pandas as pd
import datetime
import time
import re
import json
import random

# =============================================================================
# 1. MULTI-CHANNEL TRACKING
# =============================================================================
_qp = st.query_params
if "tracking_ref" not in st.session_state:
    st.session_state["tracking_ref"]    = _qp.get("ref",    "")
if "tracking_source" not in st.session_state:
    st.session_state["tracking_source"] = _qp.get("source", "organic")

# =============================================================================
# 2. AI ENGINE — Google Gemini
# =============================================================================
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

_google_key   = None
ai_status     = "offline"
model_vguard  = None

try:
    _google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    _google_key = None

if _google_key and GENAI_AVAILABLE:
    try:
        genai.configure(api_key=_google_key)
        model_vguard = genai.GenerativeModel("gemini-1.5-flash")
        ai_status    = "online"
    except Exception:
        pass

# =============================================================================
# 3. PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="V-Guard AI Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# 4. SESSION STATE DEFAULTS
# =============================================================================
_DEFAULTS = {
    "admin_logged_in":      False,
    "db_umum":              [],          # list of client dicts
    "db_pengajuan":         [],          # list of pending orders from portal
    "api_cost_total":       0.0,
    "cs_chat_history":      [],
    "agent_kill_switch":    {},
    "detected_package":     None,
    "pending_quick":        None,
    "client_logged_in":     False,
    "client_data":          None,
    "chat_widget_open":     False,
    "agent_logs":           [],
    "fraud_scan_results":   None,
    "investor_pw_ok":       False,
    "portal_form_submitted": False,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# =============================================================================
# 5. CONSTANTS
# =============================================================================
WA_NUMBER      = "6282122190885"
WA_LINK_DEMO   = "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote("Halo Pak Erwin, saya ingin Book Demo V-Guard AI.")
WA_LINK_KONSUL = "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote("Halo Pak Erwin, saya ingin konsultasi mengenai V-Guard AI.")
BASE_APP_URL   = "https://v-guard-ai.streamlit.app"

PRODUCT_LINKS = {
    "V-LITE":    BASE_APP_URL + "/?menu=Produk+%26+Harga#v-lite",
    "V-PRO":     BASE_APP_URL + "/?menu=Produk+%26+Harga#v-pro",
    "V-ADVANCE": BASE_APP_URL + "/?menu=Produk+%26+Harga#v-advance",
    "V-ELITE":   BASE_APP_URL + "/?menu=Produk+%26+Harga#v-elite",
    "V-ULTRA":   BASE_APP_URL + "/?menu=Produk+%26+Harga#v-ultra",
}
ORDER_LINKS = {
    "V-LITE":    "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote("Halo Pak Erwin, saya ingin order Paket V-LITE. Mohon kirimkan invoice."),
    "V-PRO":     "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote("Halo Pak Erwin, saya ingin order Paket V-PRO. Mohon kirimkan invoice."),
    "V-ADVANCE": "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote("Halo Pak Erwin, saya ingin order Paket V-ADVANCE. Mohon kirimkan invoice."),
    "V-ELITE":   "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote("Halo Pak Erwin, saya ingin order Paket V-ELITE. Mohon kirimkan invoice."),
    "V-ULTRA":   "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote("Halo Pak Erwin, saya ingin konsultasi Paket V-ULTRA (Enterprise Custom)."),
}
HARGA_MAP = {
    "V-LITE":    ("Rp 150.000",         "Rp 250.000"),
    "V-PRO":     ("Rp 450.000",         "Rp 750.000"),
    "V-ADVANCE": ("Rp 1.200.000",       "Rp 3.500.000"),
    "V-ELITE":   ("Mulai Rp 3.500.000", "Rp 10.000.000"),
    "V-ULTRA":   ("Custom",             "Konsultasi"),
}
HARGA_NUMERIK = {
    "V-LITE": 150_000, "V-PRO": 450_000, "V-ADVANCE": 1_200_000,
    "V-ELITE": 3_500_000, "V-ULTRA": 0,
}
SOURCE_MAP = {
    "whatsapp": "WhatsApp", "facebook": "Facebook", "linkedin": "LinkedIn",
    "tiktok": "TikTok", "instagram": "Instagram", "youtube": "YouTube",
    "organic": "Organik / Langsung",
}

# 10 AI Agents
AI_AGENTS = [
    {"id":1,  "name":"Visionary",   "role":"Strategic AI Architect",       "icon":"🧠", "desc":"Memetakan strategi keamanan bisnis & skenario ROI jangka panjang."},
    {"id":2,  "name":"Concierge",   "role":"Customer Intelligence AI",     "icon":"🤝", "desc":"Mendeteksi kebutuhan klien & merekomendasikan paket secara proaktif."},
    {"id":3,  "name":"Sentinel CS", "role":"24/7 AI Sales Consultant",     "icon":"🛡️", "desc":"Chatbot penjualan utama — aktif di seluruh halaman."},
    {"id":4,  "name":"Liaison",     "role":"Fraud Intelligence Engine",    "icon":"🔍", "desc":"Filter lokal anomali/void/fraud sebelum dikirim ke API — hemat 80% biaya."},
    {"id":5,  "name":"Auditor",     "role":"Bank Statement AI",            "icon":"🏦", "desc":"Rekonsiliasi otomatis laporan kasir vs mutasi rekening bank."},
    {"id":6,  "name":"Stockmaster", "role":"Inventory Intelligence AI",    "icon":"📦", "desc":"Baca invoice supplier via OCR & update stok real-time tanpa input manual."},
    {"id":7,  "name":"VisualEye",   "role":"CCTV Overlay AI",              "icon":"📹", "desc":"Render teks transaksi langsung di atas feed CCTV real-time."},
    {"id":8,  "name":"WhisperBot",  "role":"WhatsApp Notification AI",     "icon":"📲", "desc":"Kirim alarm fraud & laporan harian ke Owner via WhatsApp otomatis."},
    {"id":9,  "name":"Collector",   "role":"A/R Collection Reminder AI",   "icon":"💰", "desc":"Ingatkan piutang jatuh tempo H-7 & H-1 secara otomatis."},
    {"id":10, "name":"Oracle",      "role":"Predictive Analytics AI",      "icon":"🔮", "desc":"Proyeksi omzet, deteksi tren kebocoran, dan rekomendasi tindakan preventif."},
]

# =============================================================================
# 6. PRODUCT MATCHING ENGINE
# =============================================================================
KEYWORD_PACKAGE_MAP = [
    ("V-LITE",    ["warung","lapak","satu kasir","1 kasir","kios","usaha kecil",
                   "baru mulai","baru buka","coba dulu","trial","murah","terjangkau"], 1),
    ("V-PRO",     ["pantau toko","pantau kasir","kamera","cctv standar","keamanan standar",
                   "toko kecil","restoran kecil","cafe","kafe","monitor transaksi",
                   "laporan harian","ocr invoice","audit bank","2 kasir","3 kasir","plug","play"], 2),
    ("V-ADVANCE", ["kasir","stok barang","stok","banyak cabang","multi cabang","beberapa cabang",
                   "minimarket","supermarket","swalayan","toko besar","restoran besar",
                   "franchise","waralaba","cctv ai","alarm fraud","void mencurigakan"], 3),
    ("V-ELITE",   ["korporasi","perusahaan besar","server privat","server sendiri","forensik",
                   "ai forensik","sla","enterprise","ratusan kasir","puluhan cabang","holding",
                   "kasir curang","fraud kasir","kecurangan kasir","deteksi fraud",
                   "fraud detection","cek fraud"], 4),
    ("V-ULTRA",   ["white label","rebranding","custom platform","lisensi platform","c-level",
                   "10 agen","full custom","konsultasi strategis","reseller platform"], 5),
]

def detect_package_from_message(text):
    t = text.lower()
    scores = {}
    for pkg, keywords, weight in KEYWORD_PACKAGE_MAP:
        hit = sum(1 for kw in keywords if kw in t)
        if hit:
            scores[pkg] = scores.get(pkg, 0) + hit * weight
    return max(scores, key=scores.get) if scores else None

def build_package_cta(pkg):
    hb, hs   = HARGA_MAP.get(pkg, ("Custom","Konsultasi"))
    plink    = PRODUCT_LINKS.get(pkg, BASE_APP_URL)
    olink    = ORDER_LINKS.get(pkg, WA_LINK_KONSUL)
    label_map = {
        "V-LITE":"Fondasi Keamanan Digital (1 Kasir)","V-PRO":"Otomasi Penuh & Audit Bank",
        "V-ADVANCE":"Pengawas Aktif Multi-Cabang","V-ELITE":"Kedaulatan Data Korporasi",
        "V-ULTRA":"White-Label & 10 Elite AI Squad",
    }
    emoji_map = {"V-LITE":"🔵","V-PRO":"⚡","V-ADVANCE":"🟣","V-ELITE":"🟢","V-ULTRA":"👑"}
    install_note = (
        "✅ **Plug & Play** — aktif mandiri dalam hitungan menit, tanpa teknisi."
        if pkg in ("V-LITE","V-PRO")
        else "🔧 **Instalasi Profesional** — teknisi V-Guard datang ke lokasi bisnis Anda."
    )
    return (
        f"\n\n---\n{emoji_map.get(pkg,'🛡️')} **Rekomendasi Terbaik: {pkg}**\n"
        f"_{label_map.get(pkg,'')}_\n\n"
        f"💰 **Biaya Bulanan:** {hb}\n🛠️ **Biaya Setup:** {hs}\n{install_note}\n\n"
        f"👉 **[Lihat Detail {pkg}]({plink})**   📲 **[Order via WhatsApp]({olink})**\n\n"
        f"_Setiap hari tanpa V-Guard adalah hari yang berisiko. Saya siap memandu Anda! 🚀_"
    )

# =============================================================================
# 7. CS SYSTEM PROMPT
# =============================================================================
CS_SYSTEM_PROMPT = """
Anda adalah Sentinel CS — Konsultan AI pribadi resmi V-Guard AI Intelligence.
Gunakan sapaan Bapak, Ibu, atau Kakak. Gaya: hangat, persuasif, semi-formal, singkat dan langsung.

PRODUK & HARGA:
V-LITE    Rp 150.000/bln | Setup Rp 250.000     | PLUG & PLAY
V-PRO     Rp 450.000/bln | Setup Rp 750.000     | PLUG & PLAY
V-ADVANCE Rp 1.200.000/bln | Setup Rp 3.500.000 | Teknisi
V-ELITE   Mulai Rp 3.500.000/bln | Setup Rp 10jt | Teknisi
V-ULTRA   Custom | Konsultasi | Teknisi

PRODUCT MATCHING:
CCTV/Pantau/Monitor -> V-PRO
Kasir Curang/Fraud -> V-ELITE
Usaha Kecil/1 Kasir/Warung -> V-LITE
Multi-Cabang/Stok -> V-ADVANCE
White-Label/Enterprise -> V-ULTRA

ATURAN UTAMA:
- Tanya dulu jenis usaha dan jumlah kasir/cabang sebelum rekomendasikan harga
- Setelah tahu kebutuhan: rekomendasikan 1 paket + link detail + link order
- Akhiri selalu dengan pertanyaan follow-up
- JANGAN sebut error, maintenance, API, atau nomor WA manual
- Jika ada gangguan teknis: "Maaf, sistem sedang padat, mohon tunggu sebentar"
- Respons maksimal 150 kata agar ringkas di widget chat

ROI: Kebocoran rata-rata 5% omzet. V-Guard cegah 88%. ROI = (penghematan - biaya paket) / biaya paket x 100%
INSTALASI: V-LITE & V-PRO = PLUG & PLAY. V-ADVANCE ke atas = teknisi.
"""

# =============================================================================
# 8. HELPERS
# =============================================================================
def buat_client_id(nama, no_hp):
    raw = nama.strip().lower() + no_hp.strip()
    return "VG-" + hashlib.md5(raw.encode()).hexdigest()[:6].upper()

def buat_dashboard_link(cid):
    return BASE_APP_URL + "/?client_id=" + cid

def buat_referral_link(cid):
    return BASE_APP_URL + "/?ref=" + cid

def buat_payment_link(pkg, nama):
    txt = urllib.parse.quote(
        f"PEMBAYARAN V-GUARD AI\n\nYth. {nama}\nPaket: {pkg}\n"
        f"Biaya Bulanan: {HARGA_MAP.get(pkg,('—','—'))[0]}\n"
        f"Biaya Setup   : {HARGA_MAP.get(pkg,('—','—'))[1]}\n\n"
        f"Transfer ke:\nBank BCA · 3450074658 · a/n Erwin Sinaga\n\n"
        f"Konfirmasi setelah transfer ke nomor ini.\n— Tim V-Guard AI"
    )
    return f"https://wa.me/{WA_NUMBER}?text={txt}"

def hitung_proyeksi_omset(db):
    return sum(HARGA_NUMERIK.get(k.get("Produk","V-LITE"),0) for k in db if k.get("Status")=="Aktif")

def get_sample_transaksi():
    now = datetime.datetime.now()
    return pd.DataFrame({
        "ID_Transaksi":["TRX-001","TRX-002","TRX-003","TRX-004","TRX-005","TRX-006","TRX-007","TRX-008"],
        "Cabang":["Outlet Sudirman","Outlet Sudirman","Resto Central","Cabang Tangerang",
                  "Outlet Sudirman","Resto Central","Cabang Tangerang","Outlet Sudirman"],
        "Kasir":["Budi","Budi","Sari","Andi","Budi","Sari","Andi","Dewi"],
        "Jumlah":[150000,150000,500000,200000,150000,300000,50000,75000],
        "Waktu":[now-datetime.timedelta(minutes=2),now-datetime.timedelta(minutes=3),
                 now-datetime.timedelta(hours=1),now-datetime.timedelta(hours=2),
                 now-datetime.timedelta(minutes=4),now-datetime.timedelta(hours=3),
                 now-datetime.timedelta(hours=5),now-datetime.timedelta(minutes=10)],
        "Status":["VOID","NORMAL","NORMAL","NORMAL","VOID","NORMAL","NORMAL","NORMAL"],
        "Saldo_Fisik":[0,150000,480000,200000,0,300000,45000,75000],
        "Saldo_Sistem":[150000,150000,500000,200000,150000,300000,50000,75000],
    })

def scan_fraud_lokal(df):
    void_df = df[df["Status"]=="VOID"].copy()
    df_s = df.sort_values(["Kasir","Jumlah","Waktu"]).copy()
    df_s["selisih_menit"] = df_s.groupby(["Kasir","Jumlah"])["Waktu"].diff().dt.total_seconds().div(60)
    fraud_df = df_s[df_s["selisih_menit"] < 5].copy()
    df2 = df.copy()
    df2["selisih_saldo"] = df2["Saldo_Sistem"] - df2["Saldo_Fisik"]
    sus_df = df2[df2["selisih_saldo"] != 0].copy()
    return {"void": void_df, "fraud": fraud_df, "suspicious": sus_df}

# =============================================================================
# 9. AI RESPONSE ENGINE
# =============================================================================
def get_ai_response(user_message):
    detected = detect_package_from_message(user_message)
    if detected:
        st.session_state["detected_package"] = detected

    def fallback(msg, pkg):
        m = msg.lower()
        omzet_val = 0
        om = re.search(r"(\d[\d.,]*)\s*(juta|jt|miliar|m\b|rb|ribu)?", m)
        if om:
            try:
                raw = float(om.group(1).replace(",",".").replace(".",""))
                unit = (om.group(2) or "").strip().lower()
                if unit in ("juta","jt"):    omzet_val = int(raw * 1_000_000)
                elif unit in ("miliar","m"): omzet_val = int(raw * 1_000_000_000)
                elif unit in ("rb","ribu"):  omzet_val = int(raw * 1_000)
                elif raw >= 1_000_000:       omzet_val = int(raw)
            except Exception:
                omzet_val = 0

        roi_block = ""
        if omzet_val >= 1_000_000:
            bocor = omzet_val * 0.05
            saved = bocor * 0.88
            biaya = HARGA_NUMERIK.get(pkg or "V-PRO", 450_000)
            net   = saved - biaya
            roi   = (net / biaya * 100) if biaya > 0 else 0
            roi_block = (
                f"\n\n💡 **Estimasi ROI:**\n"
                f"- Omzet: Rp {omzet_val:,.0f}/bln\n"
                f"- Kebocoran 5%: Rp {bocor:,.0f}/bln\n"
                f"- Diselamatkan (88%): **Rp {saved:,.0f}/bln**\n"
                f"- ROI estimasi: **{roi:.0f}%** 🚀"
            )

        if any(k in m for k in ["harga","berapa","biaya","tarif","paket"]):
            base = (
                "Tentu! Sebelum saya rekomendasikan, boleh saya tahu dulu — **jenis usaha apa** "
                "dan berapa **kasir atau cabang** Bapak/Ibu? 😊"
            )
        elif any(k in m for k in ["cctv","kamera","pantau","monitor","visual"]):
            base = (
                "Untuk kebutuhan **monitoring & CCTV AI**, saya rekomendasikan **V-PRO** 📹\n\n"
                "✅ CCTV AI — teks transaksi tampil di rekaman\n"
                "✅ Audit bank otomatis · **Plug & Play** tanpa teknisi"
            )
            if not pkg: base += build_package_cta("V-PRO")
        elif any(k in m for k in ["fraud","curang","kecurangan","void mencurigakan","kasir curang"]):
            base = (
                "Untuk **deteksi fraud kasir**, solusi terbaik adalah **V-ELITE** 🛡️\n\n"
                "✅ Deep Learning Forensik · Private Server · SLA 99.9%"
            )
            if not pkg: base += build_package_cta("V-ELITE")
        elif any(k in m for k in ["apa itu","v-guard","vguard","tentang"]):
            base = (
                "**V-Guard AI Intelligence** adalah sistem keamanan bisnis berbasis AI "
                "yang mengawasi kasir, stok, dan rekening bank Anda 24/7 🏆\n\n"
                "- Cegah kebocoran hingga **88%**\n"
                "- Deteksi anomali **< 5 detik**\n- ROI rata-rata **400–900%/bulan**\n\n"
                "Boleh ceritakan bisnis Bapak/Ibu? 🙏"
            )
        elif any(k in m for k in ["roi","hemat","bocor","rugi","omzet"]):
            base = (
                "Rata-rata bisnis kehilangan **3–15% omzet** per bulan tanpa disadari. "
                "V-Guard AI mencegah hingga **88% kebocoran** otomatis.\n\n"
                "Boleh share **omzet bulanan** bisnis Bapak/Ibu? 😊"
            )
        elif any(k in m for k in ["book demo","demo","coba"]):
            base = (
                "Demo V-Guard **gratis 30 menit** — Pak Erwin langsung tunjukkan cara "
                "sistem mendeteksi kecurangan secara real-time.\n\n"
                f"📲 [Book Demo Gratis]({WA_LINK_DEMO})"
            )
        elif any(k in m for k in ["daftar","order","beli","aktivasi","mulai"]):
            base = (
                "Siap! Untuk memulai, Bapak/Ibu bisa pilih paket yang sesuai:\n\n"
                "🔵 V-LITE (Rp 150rb) · ⚡ V-PRO (Rp 450rb) · 🟣 V-ADVANCE (Rp 1,2jt)\n"
                "🟢 V-ELITE (Rp 3,5jt) · 👑 V-ULTRA (Custom)\n\n"
                "Boleh saya tahu jenis usaha Bapak/Ibu agar saya pilihkan yang paling tepat? 😊"
            )
        else:
            base = (
                "Halo! Saya **Sentinel CS**, konsultan AI V-Guard AI 👋\n\n"
                "Ceritakan bisnis Bapak/Ibu:\n"
                "- Berapa **kasir atau cabang**?\n"
                "- Berapa **omzet bulanan** rata-rata?\n\n"
                "Saya langsung hitung potensi kebocoran dan rekomendasikan solusi terbaik 💡"
            )

        result = base + roi_block
        if pkg and "Order" not in result and "Rekomendasi" not in result:
            result += build_package_cta(pkg)
        return result

    if model_vguard:
        try:
            hist = []
            for m in st.session_state.cs_chat_history[:-1]:
                hist.append({"role": "model" if m["role"]=="assistant" else "user", "parts":[m["content"]]})
            chat_obj = model_vguard.start_chat(history=hist)
            prompt = CS_SYSTEM_PROMPT + f"\n\nPesan Klien: {user_message}"
            if detected:
                bul,_ = HARGA_MAP.get(detected,("Custom","—"))
                prompt += (f"\n\n[HINT: Paket cocok: {detected} ({bul}/bln). "
                           f"Sertakan link: {PRODUCT_LINKS[detected]} dan {ORDER_LINKS[detected]}. "
                           f"Akhiri dengan pertanyaan follow-up. Respons max 150 kata.]")
            resp = chat_obj.send_message(prompt)
            ans  = resp.text.strip() if resp.text else ""
            if ans:
                st.session_state.api_cost_total += 200
                return ans
        except Exception:
            pass
    return fallback(user_message, detected)

# =============================================================================
# 10. MASTER CSS
# =============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;700&display=swap');

:root {
    --bg-primary:#060b14; --bg-secondary:#0d1626; --bg-card:#101c2e;
    --bg-hover:#162035; --accent:#00d4ff; --accent2:#0091ff; --accent3:#7b2fff;
    --danger:#ff3b5c; --success:#00e676; --warning:#ffab00;
    --text-primary:#e8f4ff; --text-muted:#7a9bbf;
    --border:#1e3352; --border-glow:#00d4ff44; --gold:#ffd700;
}

html,body,[class*="css"]{
    font-family:'Inter',sans-serif!important;
    color:var(--text-primary)!important;
    background-color:var(--bg-primary)!important;
}
section[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#08111f 0%,#0d1a2e 100%)!important;
    border-right:1px solid var(--border)!important;
}
section[data-testid="stSidebar"] *{color:var(--text-primary)!important;}
.main .block-container{padding:0!important;max-width:100%!important;}

/* Buttons */
.stButton>button{
    background:linear-gradient(135deg,var(--accent2),var(--accent))!important;
    color:#000!important;font-family:'Rajdhani',sans-serif!important;
    font-weight:700!important;font-size:15px!important;border:none!important;
    border-radius:6px!important;height:46px!important;transition:all .2s ease!important;
}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 0 20px var(--border-glow)!important;}
.stButton>button[kind="secondary"]{background:transparent!important;color:var(--accent)!important;border:1px solid var(--accent)!important;}
a[data-testid="stLinkButton"] button{background:linear-gradient(135deg,#25D366,#128C7E)!important;color:white!important;font-weight:700!important;border-radius:6px!important;}

/* Inputs */
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stNumberInput>div>div>input,.stSelectbox>div>div{
    background-color:var(--bg-card)!important;border:1px solid var(--border)!important;
    color:var(--text-primary)!important;border-radius:6px!important;
}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{border-color:var(--accent)!important;box-shadow:0 0 10px var(--border-glow)!important;}

/* Metrics */
[data-testid="stMetric"]{background:var(--bg-card)!important;border:1px solid var(--border)!important;border-radius:10px!important;padding:16px!important;}
[data-testid="stMetricLabel"]{color:var(--text-muted)!important;font-size:12px!important;}
[data-testid="stMetricValue"]{color:var(--accent)!important;font-family:'Rajdhani',sans-serif!important;font-size:28px!important;}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{background:var(--bg-secondary)!important;border-bottom:1px solid var(--border)!important;}
.stTabs [data-baseweb="tab"]{color:var(--text-muted)!important;font-family:'Rajdhani',sans-serif!important;font-weight:600!important;font-size:15px!important;}
.stTabs [aria-selected="true"]{color:var(--accent)!important;border-bottom:2px solid var(--accent)!important;}

/* Misc */
[data-testid="stDataFrame"]{border:1px solid var(--border)!important;border-radius:8px!important;}
[data-testid="stExpander"]{border:1px solid var(--border)!important;border-radius:8px!important;background:var(--bg-card)!important;}
.stProgress>div>div>div{background:linear-gradient(90deg,var(--accent2),var(--accent))!important;}
::-webkit-scrollbar{width:6px;}::-webkit-scrollbar-track{background:var(--bg-primary);}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}::-webkit-scrollbar-thumb:hover{background:var(--accent);}

/* ── FLOATING CHAT WIDGET ── */
#vguard-chat-widget {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 350px;
    z-index: 9999;
    font-family: 'Inter', sans-serif;
}
#chat-toggle-btn {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: linear-gradient(135deg, #0091ff, #00d4ff);
    border: none;
    cursor: pointer;
    z-index: 10000;
    box-shadow: 0 4px 20px #00d4ff44;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    transition: all .2s ease;
    animation: float 3s ease-in-out infinite;
}
#chat-toggle-btn:hover { transform: scale(1.1); box-shadow: 0 6px 28px #00d4ff66; }
@keyframes float {
    0%,100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}
#chat-box {
    position: fixed;
    bottom: 90px;
    right: 20px;
    width: 350px;
    height: 500px;
    background: #0d1626;
    border: 1px solid #1e3352;
    border-radius: 16px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 8px 40px #00000066;
    overflow: hidden;
    z-index: 9999;
    transition: all .3s ease;
}
#chat-header {
    background: linear-gradient(135deg, #060b14, #0a1628);
    border-bottom: 1px solid #1e3352;
    padding: 14px 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
}
#chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    scroll-behavior: smooth;
}
#chat-messages::-webkit-scrollbar{width:4px;}
#chat-messages::-webkit-scrollbar-track{background:transparent;}
#chat-messages::-webkit-scrollbar-thumb{background:#1e3352;border-radius:2px;}
.chat-bubble-bot {
    background: #101c2e;
    border: 1px solid #1e3352;
    border-radius: 14px 14px 14px 4px;
    padding: 10px 14px;
    font-size: 13px;
    line-height: 1.6;
    color: #e8f4ff;
    max-width: 90%;
    align-self: flex-start;
}
.chat-bubble-user {
    background: linear-gradient(135deg, #0091ff, #00d4ff);
    border-radius: 14px 14px 4px 14px;
    padding: 10px 14px;
    font-size: 13px;
    line-height: 1.6;
    color: #000;
    font-weight: 500;
    max-width: 85%;
    align-self: flex-end;
}
#chat-quick-pills {
    padding: 8px 14px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    border-top: 1px solid #1e3352;
    flex-shrink: 0;
    background: #0d1626;
}
.quick-pill {
    background: #101c2e;
    border: 1px solid #1e3352;
    color: #7a9bbf;
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 20px;
    cursor: pointer;
    transition: all .2s;
    white-space: nowrap;
}
.quick-pill:hover { border-color: #00d4ff; color: #00d4ff; background: #00d4ff11; }
#chat-input-area {
    display: flex;
    gap: 8px;
    padding: 10px 14px;
    border-top: 1px solid #1e3352;
    background: #060b14;
    flex-shrink: 0;
}
#chat-input {
    flex: 1;
    background: #101c2e;
    border: 1px solid #1e3352;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: #e8f4ff;
    outline: none;
    font-family: 'Inter', sans-serif;
    resize: none;
    height: 38px;
}
#chat-input:focus { border-color: #00d4ff; }
#chat-send-btn {
    background: linear-gradient(135deg, #0091ff, #00d4ff);
    border: none;
    border-radius: 8px;
    width: 38px;
    height: 38px;
    cursor: pointer;
    color: #000;
    font-size: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all .2s;
    flex-shrink: 0;
}
#chat-send-btn:hover { transform: scale(1.05); }
.chat-typing { display: flex; gap: 4px; padding: 4px 0; }
.chat-typing span { width: 7px; height: 7px; background: #00d4ff; border-radius: 50%; animation: blink 1.2s infinite; }
.chat-typing span:nth-child(2) { animation-delay: .2s; }
.chat-typing span:nth-child(3) { animation-delay: .4s; }
@keyframes blink { 0%,80%,100%{opacity:.3;} 40%{opacity:1;} }
.chat-notification-dot {
    position: absolute;
    top: 0;
    right: 0;
    width: 12px;
    height: 12px;
    background: #ff3b5c;
    border-radius: 50%;
    border: 2px solid #060b14;
}

/* ── HERO & PAGE COMPONENTS ── */
.hero-section{background:linear-gradient(135deg,#060b14 0%,#0a1628 50%,#080f1e 100%);padding:60px 48px 48px;position:relative;overflow:hidden;border-bottom:1px solid var(--border);}
.hero-section::before{content:'';position:absolute;top:-50%;right:-10%;width:600px;height:600px;background:radial-gradient(circle,#00d4ff11 0%,transparent 70%);pointer-events:none;}
.hero-badge{display:inline-block;background:linear-gradient(135deg,#00d4ff22,#0091ff22);border:1px solid var(--accent);color:var(--accent)!important;font-family:'JetBrains Mono',monospace!important;font-size:11px!important;padding:4px 14px;border-radius:20px;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:20px;}
.hero-title{font-family:'Rajdhani',sans-serif!important;font-size:58px!important;font-weight:700!important;line-height:1.1!important;color:var(--text-primary)!important;margin-bottom:8px!important;}
.hero-title .accent{color:var(--accent)!important;}
.hero-subtitle{font-size:19px!important;color:var(--text-muted)!important;line-height:1.7!important;max-width:520px;margin-bottom:36px!important;}
.stat-card{background:linear-gradient(135deg,var(--bg-card),var(--bg-secondary));border:1px solid var(--border);border-radius:12px;padding:28px 20px;text-align:center;}
.stat-number{font-family:'Rajdhani',sans-serif!important;font-size:44px!important;font-weight:700!important;background:linear-gradient(135deg,var(--accent),var(--accent3));-webkit-background-clip:text!important;-webkit-text-fill-color:transparent!important;background-clip:text!important;}
.stat-label{font-size:13px!important;color:var(--text-muted)!important;margin-top:4px;}
.feature-card{background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:24px;height:100%;transition:all .3s ease;}
.feature-card:hover{border-color:var(--accent);transform:translateY(-3px);box-shadow:0 8px 30px #00d4ff11;}
.feature-title{font-family:'Rajdhani',sans-serif!important;font-size:17px!important;font-weight:700!important;color:var(--text-primary)!important;margin-bottom:8px;}
.feature-desc{font-size:13px!important;color:var(--text-muted)!important;line-height:1.6;}
.testimonial-card{background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:24px;border-left:3px solid var(--accent);}
.testimonial-text{font-size:14px!important;color:var(--text-primary)!important;line-height:1.7;font-style:italic;margin-bottom:16px;}
.testimonial-author{font-family:'Rajdhani',sans-serif!important;font-size:15px!important;font-weight:700!important;color:var(--accent)!important;}
.testimonial-role{font-size:12px!important;color:var(--text-muted)!important;}
.stars{color:var(--gold)!important;font-size:14px;margin-bottom:10px;}
.section-header{font-family:'Rajdhani',sans-serif!important;font-size:36px!important;font-weight:700!important;color:var(--text-primary)!important;text-align:center;margin-bottom:8px!important;}
.section-subheader{font-size:16px!important;color:var(--text-muted)!important;text-align:center;margin-bottom:36px!important;}
.section-accent{color:var(--accent)!important;}
.section-wrapper{padding:56px 48px;border-bottom:1px solid var(--border);}
.section-wrapper-alt{padding:56px 48px;background:var(--bg-secondary);border-bottom:1px solid var(--border);}
.page-title{font-family:'Rajdhani',sans-serif!important;font-size:34px!important;font-weight:700!important;color:var(--text-primary)!important;margin-bottom:4px!important;}
.page-subtitle{font-size:15px!important;color:var(--text-muted)!important;margin-bottom:32px!important;}
.demo-mockup{background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:16px;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--text-muted);line-height:1.8;}
.demo-dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:4px;}
.demo-red{background:#ff5f57;}.demo-yellow{background:#febc2e;}.demo-green{background:#28c840;}
.sidebar-logo{font-family:'Rajdhani',sans-serif!important;font-size:22px!important;font-weight:700!important;color:var(--accent)!important;letter-spacing:1px;text-align:center;}
.sidebar-tagline{font-size:10px!important;color:var(--text-muted)!important;text-align:center;letter-spacing:2px;text-transform:uppercase;}
.status-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--success);margin-right:6px;animation:pulse 2s infinite;}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:.4;}}

/* ── PACKAGE CARDS ── */
.pkg-card{background:#101c2e;border:1px solid #1e3352;border-radius:14px;padding:22px 16px 20px;display:flex;flex-direction:column;height:100%;transition:all .3s ease;position:relative;}
.pkg-card:hover{border-color:#00d4ff;box-shadow:0 0 28px #00d4ff11;transform:translateY(-4px);}
.pkg-card-ultra{background:linear-gradient(160deg,#12100a,#1a1500,#0e0e0e);border:1px solid #ffd70055;border-radius:14px;padding:22px 16px 20px;display:flex;flex-direction:column;height:100%;transition:all .3s ease;position:relative;}
.pkg-card-ultra:hover{border-color:#ffd700;box-shadow:0 0 32px #ffd70022;transform:translateY(-4px);}
.pkg-card-popular{background:#101c2e;border:1.5px solid #0091ff;border-radius:14px;padding:22px 16px 20px;display:flex;flex-direction:column;height:100%;transition:all .3s ease;position:relative;}
.pkg-card-popular:hover{border-color:#00d4ff;box-shadow:0 0 28px #00d4ff11;transform:translateY(-4px);}
.pkg-features-grow{flex-grow:1;}
.hot-label{position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,#0091ff,#00d4ff);color:#000!important;font-family:'Rajdhani',sans-serif!important;font-size:10px!important;font-weight:700!important;padding:3px 14px;border-radius:20px;letter-spacing:1px;white-space:nowrap;}
.ultra-label{position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,#b8860b,#ffd700);color:#000!important;font-family:'Rajdhani',sans-serif!important;font-size:10px!important;font-weight:700!important;padding:3px 14px;border-radius:20px;letter-spacing:1px;white-space:nowrap;}
.tier-badge{display:inline-block;font-family:'JetBrains Mono',monospace!important;font-size:10px!important;letter-spacing:1.5px;text-transform:uppercase;padding:3px 10px;border-radius:20px;margin-bottom:10px;}
.badge-entry{background:#00d4ff18;color:#00d4ff!important;border:1px solid #00d4ff55;}
.badge-pro{background:#0091ff18;color:#6ac8ff!important;border:1px solid #0091ff55;}
.badge-adv{background:#7b2fff18;color:#b49fff!important;border:1px solid #7b2fff55;}
.badge-ent{background:#00e67618;color:#00e676!important;border:1px solid #00e67655;}
.badge-ultra{background:#ffd70018;color:#ffd700!important;border:1px solid #ffd70055;}
.pkg-name{font-family:'Rajdhani',sans-serif!important;font-size:20px!important;font-weight:700!important;color:#e8f4ff!important;margin-bottom:2px;}
.pkg-name-ultra{font-family:'Rajdhani',sans-serif!important;font-size:20px!important;font-weight:700!important;color:#ffd700!important;margin-bottom:2px;}
.pkg-focus{font-size:11px!important;color:#7a9bbf!important;line-height:1.4;margin-bottom:14px;}
.pkg-price{font-family:'Rajdhani',sans-serif!important;font-size:24px!important;font-weight:700!important;color:#00d4ff!important;margin-bottom:2px;}
.pkg-price-ultra{font-family:'Rajdhani',sans-serif!important;font-size:24px!important;font-weight:700!important;color:#ffd700!important;margin-bottom:2px;}
.pkg-period{font-size:11px!important;color:#7a9bbf!important;margin-bottom:4px;}
.pkg-setup{font-size:11px!important;color:#4a6a8a!important;margin-bottom:14px;}
.pkg-divider{border:none;border-top:1px solid #1e3352;margin:12px 0;}
.pkg-feature{font-size:12px!important;color:#9ab8d4!important;padding:3px 0;display:flex;align-items:flex-start;gap:6px;line-height:1.4;}
.pkg-feature-ultra{font-size:12px!important;color:#d4b84a!important;padding:3px 0;display:flex;align-items:flex-start;gap:6px;line-height:1.4;}
.pkg-check{color:#00e676!important;flex-shrink:0;font-size:11px;}
.pkg-check-ultra{color:#ffd700!important;flex-shrink:0;font-size:11px;}
.install-pill{display:inline-block;font-family:'JetBrains Mono',monospace!important;font-size:9px!important;padding:2px 8px;border-radius:20px;margin-top:8px;}
.install-pnp{background:#00e67618;color:#00e676!important;border:1px solid #00e67644;}
.install-pro{background:#ffab0018;color:#ffab00!important;border:1px solid #ffab0044;}

/* ── CLIENT / PORTAL CARDS ── */
.client-card-aktif{background:#101c2e;border:1px solid #1e3352;border-left:3px solid #00e676;border-radius:12px;padding:20px;margin-bottom:14px;}
.client-card-pending{background:#101c2e;border:1px solid #1e3352;border-left:3px solid #ffab00;border-radius:12px;padding:20px;margin-bottom:14px;}
.client-badge-aktif{display:inline-block;background:#00e67618;color:#00e676!important;border:1px solid #00e67644;border-radius:20px;font-size:10px!important;padding:2px 10px;font-family:'JetBrains Mono',monospace!important;}
.client-badge-pending{display:inline-block;background:#ffab0018;color:#ffab00!important;border:1px solid #ffab0044;border-radius:20px;font-size:10px!important;padding:2px 10px;font-family:'JetBrains Mono',monospace!important;}
.login-card{background:var(--bg-card);border:1px solid var(--border);border-radius:14px;padding:36px;}
.ref-link-box{background:#060b14;border:1px solid #1e3352;border-radius:8px;padding:12px 16px;font-family:'JetBrains Mono',monospace;font-size:12px;color:#00d4ff;word-break:break-all;}

/* ── AGENT CARDS ── */
.agent-card{background:#101c2e;border:1px solid #1e3352;border-radius:12px;padding:16px;transition:all .3s ease;position:relative;}
.agent-card:hover{border-color:#00d4ff;box-shadow:0 4px 20px #00d4ff11;}
.agent-card-active{border-left:3px solid #00e676;}
.agent-card-standby{border-left:3px solid #ffab00;}
.agent-card-offline{border-left:3px solid #ff3b5c;}
.agent-pulse{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;}
.agent-pulse-active{background:#00e676;animation:pulse 2s infinite;}
.agent-pulse-standby{background:#ffab00;}
.agent-pulse-offline{background:#ff3b5c;}

/* ── CCTV MONITOR ── */
.cctv-frame{background:#000;border:2px solid #1e3352;border-radius:8px;aspect-ratio:16/9;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;}
.cctv-overlay{position:absolute;top:8px;left:8px;font-family:'JetBrains Mono',monospace;font-size:10px;color:#00e676;background:#00000088;padding:4px 8px;border-radius:4px;}
.cctv-alert{position:absolute;top:8px;right:8px;font-family:'JetBrains Mono',monospace;font-size:10px;color:#ff3b5c;background:#00000088;padding:4px 8px;border-radius:4px;animation:pulse 1s infinite;}

/* ── INVESTOR CARD ── */
.investor-stat{background:linear-gradient(135deg,#0d1626,#101c2e);border:1px solid #1e3352;border-radius:12px;padding:24px;text-align:center;}
.investor-stat-num{font-family:'Rajdhani',sans-serif!important;font-size:36px!important;font-weight:700!important;color:#ffd700!important;}
.investor-stat-lbl{font-size:12px!important;color:#7a9bbf!important;margin-top:4px;}

/* ── PAIN CARDS ── */
.pain-card{background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:20px;margin-bottom:12px;border-left:3px solid var(--danger);}
.pain-card:hover{border-color:var(--accent);background:var(--bg-hover);}
.pain-title{font-family:'Rajdhani',sans-serif!important;font-size:16px!important;font-weight:700!important;color:var(--text-primary)!important;}
.pain-desc{font-size:13px!important;color:var(--text-muted)!important;margin-top:4px;}

/* ── MATCH BANNER ── */
.match-banner{background:linear-gradient(135deg,#00d4ff18,#0091ff11);border:1px solid #00d4ff55;border-left:3px solid #00d4ff;border-radius:10px;padding:16px 20px;margin-bottom:16px;}
.match-banner-title{font-family:'Rajdhani',sans-serif!important;font-size:15px!important;font-weight:700!important;color:#00d4ff!important;margin-bottom:4px;}
.match-banner-body{font-size:13px!important;color:#9ab8d4!important;}

/* ── CHAT in MAIN (Beranda section) ── */
[data-testid="stChatMessage"]{background:transparent!important;border:none!important;padding:4px 0!important;}
[data-testid="stChatMessageContent"]{background:#101c2e!important;border:1px solid #1e3352!important;border-radius:18px 18px 18px 4px!important;padding:14px 18px!important;font-size:14px!important;line-height:1.75!important;color:var(--text-primary)!important;box-shadow:0 2px 12px rgba(0,0,0,0.3)!important;}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"]{background:linear-gradient(135deg,#0091ff,#00d4ff)!important;border:none!important;border-radius:18px 18px 4px 18px!important;color:#000!important;font-weight:500!important;}
[data-testid="stChatInput"]{background:var(--bg-card)!important;border:1px solid var(--border)!important;border-radius:14px!important;}
[data-testid="stChatInput"] textarea{background:transparent!important;color:var(--text-primary)!important;font-size:14px!important;}
[data-testid="stChatInput"] textarea::placeholder{color:var(--text-muted)!important;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 11. FLOATING CHAT WIDGET (HTML/JS — Fixed 350x500, pojok kanan bawah)
# =============================================================================
# We handle the chat widget via Streamlit's session state + a full-page JS inject
# The widget is rendered as HTML and communicates via st.query_params for message passing

CHAT_WIDGET_HTML = """
<div id="chat-toggle-btn" onclick="toggleChat()" title="Chat dengan Sentinel CS">
    🛡️
    <div class="chat-notification-dot" id="notif-dot"></div>
</div>

<div id="chat-box" style="display:none;">
    <div id="chat-header">
        <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#0091ff,#00d4ff);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">🛡️</div>
        <div style="flex:1;">
            <div style="font-family:'Rajdhani',sans-serif;font-size:15px;font-weight:700;color:#e8f4ff;">Sentinel CS</div>
            <div style="font-size:10px;color:#00e676;font-family:'JetBrains Mono',monospace;"><span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#00e676;margin-right:4px;animation:pulse 2s infinite;"></span>Online · Siap membantu</div>
        </div>
        <button onclick="toggleChat()" style="background:transparent;border:none;color:#7a9bbf;font-size:18px;cursor:pointer;padding:0;line-height:1;">✕</button>
    </div>

    <div id="chat-messages">
        <div class="chat-bubble-bot">
            Halo! 👋 Saya <strong>Sentinel CS</strong>, konsultan AI V-Guard.<br><br>
            Ceritakan bisnis Bapak/Ibu — berapa <strong>kasir atau cabang</strong> dan <strong>omzet bulanan</strong> Anda?<br><br>
            Saya langsung hitung potensi kebocoran dan rekomendasikan paket terbaik 💡
        </div>
    </div>

    <div id="chat-quick-pills">
        <span class="quick-pill" onclick="sendQuick('Apa itu V-Guard?')">🛡️ Tentang V-Guard</span>
        <span class="quick-pill" onclick="sendQuick('Lihat semua paket')">📦 Lihat Paket</span>
        <span class="quick-pill" onclick="sendQuick('Saya punya warung 1 kasir')">🏪 Usaha Kecil</span>
        <span class="quick-pill" onclick="sendQuick('Saya khawatir kasir curang')">🔍 Cek Fraud</span>
        <span class="quick-pill" onclick="sendQuick('Hitung ROI untuk omzet 50 juta')">💰 Hitung ROI</span>
        <span class="quick-pill" onclick="sendQuick('Book demo gratis')">🎯 Book Demo</span>
    </div>

    <div id="chat-input-area">
        <input id="chat-input" type="text" placeholder="Ceritakan bisnis Anda..." 
               onkeydown="if(event.key==='Enter')sendMessage()">
        <button id="chat-send-btn" onclick="sendMessage()">➤</button>
    </div>
</div>

<script>
let chatOpen = false;
let conversationHistory = [];
let isWaiting = false;

// Fallback responses (no API)
const fallbackRules = [
    { keys: ["warung","1 kasir","kios","lapak","usaha kecil"], pkg: "V-LITE", price: "Rp 150.000/bln",
      reply: "Untuk usaha skala ini, saya rekomendasikan <strong>V-LITE</strong> (Rp 150.000/bln). Plug & Play — aktif dalam menit tanpa teknisi! 🔵<br><br>Mau saya kirimkan link detail & order?" },
    { keys: ["cafe","kafe","resto","restoran","pantau","monitor","cctv","kamera"], pkg: "V-PRO", price: "Rp 450.000/bln",
      reply: "Untuk pantau toko & CCTV AI, saya rekomendasikan <strong>V-PRO</strong> (Rp 450.000/bln). Termasuk audit bank otomatis & laporan PDF! ⚡<br><br>Berapa cabang yang Bapak/Ibu kelola?" },
    { keys: ["cabang","multi","minimarket","supermarket","franchise","stok"], pkg: "V-ADVANCE", price: "Rp 1.200.000/bln",
      reply: "Untuk multi-cabang & manajemen stok, <strong>V-ADVANCE</strong> adalah solusinya (Rp 1.200.000/bln). CCTV AI + Alarm Fraud WhatsApp! 🟣<br><br>Berapa total kasir Bapak/Ibu?" },
    { keys: ["fraud","curang","kecurangan","void mencurigakan","kasir curang"], pkg: "V-ELITE", price: "Rp 3.500.000/bln",
      reply: "Untuk deteksi fraud kasir level enterprise, saya rekomendasikan <strong>V-ELITE</strong>. Deep Learning Forensik + Private Server + SLA 99.9% 🟢<br><br>Mau saya jadwalkan demo langsung dengan Pak Erwin?" },
    { keys: ["harga","biaya","berapa","tarif","paket"], pkg: null, price: null,
      reply: "Tentu! Sebelum saya rekomendasikan paket yang tepat, boleh saya tahu dulu:<br><br>• <strong>Jenis usaha</strong> apa yang Bapak/Ibu kelola?<br>• Berapa <strong>kasir atau cabang</strong>?<br><br>Dengan info itu, saya langsung rekomendasikan yang paling sesuai 😊" },
    { keys: ["demo","coba","gratis"], pkg: null, price: null,
      reply: "Demo V-Guard <strong>GRATIS 30 menit</strong> — Pak Erwin langsung tunjukkan cara sistem mendeteksi kecurangan secara real-time!<br><br>📲 <a href='https://wa.me/6282122190885?text=Halo+Pak+Erwin,+saya+ingin+Book+Demo+V-Guard+AI.' target='_blank' style='color:#00d4ff;'>Klik di sini untuk Book Demo</a>" },
    { keys: ["roi","hemat","bocor","omzet"], pkg: null, price: null,
      reply: "Rata-rata bisnis kehilangan <strong>3–15% omzet</strong> setiap bulan tanpa disadari. V-Guard AI mencegah hingga <strong>88% kebocoran</strong> secara otomatis.<br><br>Boleh share omzet bulanan bisnis Bapak/Ibu? Saya hitung ROI-nya langsung! 💡" },
    { keys: ["apa itu","v-guard","vguard","tentang"], pkg: null, price: null,
      reply: "<strong>V-Guard AI Intelligence</strong> adalah sistem keamanan bisnis berbasis AI yang bekerja 24/7 mengawasi setiap rupiah di kasir, stok & rekening bank Anda 🏆<br><br>• Cegah kebocoran hingga <strong>88%</strong><br>• Deteksi anomali < 5 detik<br>• ROI rata-rata <strong>400–900%/bulan</strong><br><br>Boleh ceritakan bisnis Bapak/Ibu? 🙏" },
    { keys: ["paket","semua paket","lihat paket"], pkg: null, price: null,
      reply: "V-Guard tersedia dalam 5 tier:<br><br>🔵 <strong>V-LITE</strong> — Rp 150rb/bln · 1 kasir<br>⚡ <strong>V-PRO</strong> — Rp 450rb/bln · CCTV AI<br>🟣 <strong>V-ADVANCE</strong> — Rp 1,2jt/bln · Multi-cabang<br>🟢 <strong>V-ELITE</strong> — Rp 3,5jt/bln · Enterprise<br>👑 <strong>V-ULTRA</strong> — Custom · White Label<br><br>Ceritakan bisnis Anda dan saya pilihkan yang paling cocok 😊" },
];

function getFallbackReply(msg) {
    const m = msg.toLowerCase();
    for (const rule of fallbackRules) {
        if (rule.keys.some(k => m.includes(k))) return rule.reply;
    }
    return "Halo! 👋 Saya Sentinel CS, konsultan AI V-Guard.<br><br>Ceritakan bisnis Bapak/Ibu — berapa <strong>kasir/cabang</strong> dan <strong>omzet bulanan</strong>? Saya langsung rekomendasikan solusi terbaik 💡";
}

function toggleChat() {
    chatOpen = !chatOpen;
    document.getElementById('chat-box').style.display = chatOpen ? 'flex' : 'none';
    document.getElementById('notif-dot').style.display = chatOpen ? 'none' : 'block';
    if (chatOpen) scrollToBottom();
}

function scrollToBottom() {
    const msgs = document.getElementById('chat-messages');
    msgs.scrollTop = msgs.scrollHeight;
}

function addBubble(text, isUser) {
    const msgs = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = isUser ? 'chat-bubble-user' : 'chat-bubble-bot';
    div.innerHTML = text;
    msgs.appendChild(div);
    scrollToBottom();
}

function showTyping() {
    const msgs = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = 'chat-bubble-bot';
    div.id = 'typing-indicator';
    div.innerHTML = '<div class="chat-typing"><span></span><span></span><span></span></div>';
    msgs.appendChild(div);
    scrollToBottom();
}

function removeTyping() {
    const t = document.getElementById('typing-indicator');
    if (t) t.remove();
}

function sendMessage() {
    if (isWaiting) return;
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';
    processMessage(msg);
}

function sendQuick(msg) {
    if (isWaiting) return;
    processMessage(msg);
}

function processMessage(msg) {
    isWaiting = true;
    addBubble(msg, true);
    showTyping();
    conversationHistory.push({ role: 'user', content: msg });
    setTimeout(() => {
        removeTyping();
        const reply = getFallbackReply(msg);
        addBubble(reply, false);
        conversationHistory.push({ role: 'assistant', content: reply });
        isWaiting = false;
    }, 900 + Math.random() * 600);
}

// Auto-open after 4s with notification dot
setTimeout(() => {
    if (!chatOpen) {
        document.getElementById('notif-dot').style.display = 'block';
    }
}, 4000);
</script>
"""

# =============================================================================
# 12. SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("""
    <div style='padding:20px 0 16px;border-bottom:1px solid #1e3352;margin-bottom:16px;'>
        <div class='sidebar-logo'>V-GUARD AI</div>
        <div class='sidebar-tagline'>Digital Business Auditor</div>
        <div style='text-align:center;margin-top:8px;font-size:11px;color:#7a9bbf;font-family:JetBrains Mono,monospace;'>
            <span class='status-dot'></span>System Online · v2.0
        </div>
    </div>""", unsafe_allow_html=True)

    if os.path.exists("erwin.jpg"):
        st.image("erwin.jpg", use_container_width=True)
        st.markdown("""
        <div style='text-align:center;margin:10px 0 16px;'>
            <p style='color:#e8f4ff;font-weight:bold;margin-bottom:2px;font-size:14px;'>Erwin Sinaga</p>
            <p style='color:#7a9bbf;font-size:12px;'>Founder & CEO</p>
        </div>""", unsafe_allow_html=True)

    _ref = st.session_state.get("tracking_ref","")
    _src = st.session_state.get("tracking_source","organic")
    if _ref:
        st.markdown(
            "<div style='background:#00d4ff11;border:1px solid #00d4ff33;border-radius:6px;"
            "padding:6px 10px;margin-bottom:10px;font-size:10px;color:#00d4ff;"
            "font-family:JetBrains Mono,monospace;'>Ref: " + _ref + " · " + SOURCE_MAP.get(_src,_src) + "</div>",
            unsafe_allow_html=True,
        )

    dp = st.session_state.get("detected_package")
    if dp:
        hb,_ = HARGA_MAP.get(dp,("Custom","—"))
        st.markdown(
            "<div style='background:#00e67611;border:1px solid #00e67633;border-radius:8px;"
            "padding:10px 12px;margin-bottom:12px;'>"
            "<div style='font-size:10px;color:#00e676;font-family:JetBrains Mono,monospace;"
            "text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;'>🎯 Paket Terdeteksi</div>"
            "<div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:#e8f4ff;'>" + dp + "</div>"
            "<div style='font-size:11px;color:#7a9bbf;'>" + hb + "/bulan</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<p style='color:#7a9bbf;font-size:11px;text-transform:uppercase;"
        "letter-spacing:1.5px;margin-bottom:8px;'>Menu Navigasi</p>",
        unsafe_allow_html=True,
    )
    MENU_OPTIONS = ["Beranda", "Produk & Harga", "Kalkulator ROI", "Portal Klien", "Investor Area", "Admin Access"]
    menu = st.radio("", MENU_OPTIONS, label_visibility="collapsed")

# =============================================================================
# 13. FLOATING CHAT WIDGET — rendered on every page
# =============================================================================
st.markdown(CHAT_WIDGET_HTML, unsafe_allow_html=True)

# =============================================================================
# 14. PAGE: BERANDA
# =============================================================================
if menu == "Beranda":

    st.markdown("""
    <div class="hero-section">
        <div class="hero-badge">AI-Powered Fraud Detection &nbsp;·&nbsp; 24/7 Autonomous</div>
        <div class="hero-title">Hentikan <span class="accent">Kebocoran</span><br>Bisnis Anda. Sekarang.</div>
        <div class="hero-subtitle">V-Guard AI mengawasi setiap Rupiah di kasir, stok, dan rekening bank Anda
        secara otomatis — mendeteksi kecurangan sebelum Anda menyadarinya.</div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns([1.2,1.2,3])
    with c1: st.link_button("Book Demo Gratis", WA_LINK_DEMO, use_container_width=True)
    with c2: st.link_button("Chat Konsultasi", WA_LINK_KONSUL, use_container_width=True)
    st.markdown("<div style='height:48px;'></div>", unsafe_allow_html=True)

    # STATS
    st.markdown("<div class='section-wrapper'>", unsafe_allow_html=True)
    s1,s2,s3,s4 = st.columns(4)
    for col,(n,l) in zip([s1,s2,s3,s4],[
        ("88%","Kebocoran Berhasil Dicegah"),("24/7","Monitoring Otomatis"),
        ("< 5 Dtk","Deteksi Real-Time"),("5 Tier","Solusi Semua Skala"),
    ]):
        with col:
            st.markdown("<div class='stat-card'><div class='stat-number'>" + n + "</div><div class='stat-label'>" + l + "</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # PAIN POINTS
    st.markdown("""
    <div class='section-wrapper-alt'>
        <div class='section-header'>Apakah Anda Mengalami <span class='section-accent'>Ini?</span></div>
        <div class='section-subheader'>Tanda-tanda "The Invisible Leak" yang diam-diam menguras bisnis Anda</div>
    </div>""", unsafe_allow_html=True)
    PAINS = [
        ("💸","Omzet Besar, Uang Tidak Sinkron","Laporan kasir dan mutasi bank selalu berbeda."),
        ("📦","Stok Hilang Misterius","Barang keluar tapi tidak ada di laporan penjualan."),
        ("👁️","Tidak Bisa Pantau Semua Cabang","Tanpa AI, staf tahu kapan bisa 'bermain'."),
        ("🔄","Void & Diskon Mencurigakan","Transaksi sering di-void setelah pelanggan pergi."),
        ("💤","Laporan Manual Melelahkan","Setiap malam cocokkan angka secara manual."),
        ("📅","Piutang Macet, Arus Kas Terganggu","Invoice H-30 baru diingat di H+15."),
    ]
    pc1,pc2,pc3 = st.columns(3)
    for col,group in zip([pc1,pc2,pc3],[PAINS[:2],PAINS[2:4],PAINS[4:]]):
        with col:
            for icon,title,desc in group:
                st.markdown("<div class='pain-card'><div style='font-size:22px;margin-bottom:6px;'>" + icon + "</div><div class='pain-title'>" + title + "</div><div class='pain-desc'>" + desc + "</div></div>", unsafe_allow_html=True)

    # FEATURES
    st.markdown("""
    <div class='section-wrapper'>
        <div class='section-header'>Ekosistem <span class='section-accent'>V-Guard</span></div>
        <div class='section-subheader'>Satu platform, semua celah kecurangan tertutup secara otomatis</div>
    </div>""", unsafe_allow_html=True)
    FEATS = [
        ("🔗","Auto Data Integration","Tarik data langsung dari mesin kasir via IP/API. Tanpa input manual CSV."),
        ("🚨","Anomaly Detection Engine","Tandai VOID, refund, dan diskon mencurigakan secara otomatis dalam detik."),
        ("🏦","Bank Statement Audit","Cocokkan laporan kasir dengan mutasi bank secara otomatis."),
        ("📹","Visual Cashier Audit (CCTV)","Tampilkan teks transaksi tepat di atas rekaman CCTV real-time."),
        ("📦","Smart Inventory (OCR)","Update stok otomatis via drag-and-drop invoice supplier."),
        ("📲","WhatsApp Fraud Alarm","Notifikasi instan ke ponsel Owner saat anomali terdeteksi."),
    ]
    fc = st.columns(3)
    for i,(icon,title,desc) in enumerate(FEATS):
        with fc[i%3]:
            st.markdown("<div class='feature-card'><div style='font-size:28px;margin-bottom:12px;'>" + icon + "</div><div class='feature-title'>" + title + "</div><div class='feature-desc'>" + desc + "</div></div>", unsafe_allow_html=True)
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # DEMO MOCKUP
    st.markdown("""
    <div class='section-wrapper-alt'>
        <div class='section-header'>Lihat <span class='section-accent'>Dashboard</span> V-Guard</div>
        <div class='section-subheader'>Real-time monitoring langsung dari browser Anda</div>
    </div>""", unsafe_allow_html=True)
    dm1,dm2 = st.columns([1.6,1])
    with dm1:
        st.markdown("""
        <div class='demo-mockup'>
            <div style='margin-bottom:12px;'>
                <span class='demo-dot demo-red'></span><span class='demo-dot demo-yellow'></span><span class='demo-dot demo-green'></span>
                <span style='margin-left:12px;color:#7a9bbf;font-size:11px;'>v-guard.ai / sentinel-dashboard</span>
            </div>
            <span style='color:#7b2fff;'>●</span> [SENTINEL AI] — Fraud Scanner aktif...<br>
            <span style='color:#00d4ff;'>▸</span> Scanning 8 transaksi terakhir...<br>
            <span style='color:#ff3b5c;'>⚠</span> [ALERT] VOID: TRX-001 — Kasir: Budi — Rp 150.000<br>
            <span style='color:#ff3b5c;'>⚠</span> [ALERT] VOID: TRX-005 — Kasir: Budi — Rp 150.000<br>
            <span style='color:#ffab00;'>▸</span> Pola duplikat dalam 2 menit — Outlet Sudirman<br>
            <span style='color:#ff3b5c;'>⚠</span> [ALERT] Selisih saldo: TRX-003 — Rp 20.000 hilang<br>
            <span style='color:#00e676;'>✓</span> WhatsApp Alert dikirim ke Owner<br>
            <span style='color:#00d4ff;'>▸</span> AI Deep Scan selesai — 3 anomali dilaporkan<br>
            <span style='color:#00e676;'>✓</span> Laporan PDF dibuat otomatis — 04:00 WIB<br>
            <span style='color:#7a9bbf;'>_</span>
        </div>""", unsafe_allow_html=True)
    with dm2:
        for icon,val,lbl in [("🔍","3 Anomali","Terdeteksi malam ini"),("📲","1 Alert","Dikirim ke Owner"),("📊","100%","Audit Coverage"),("⚡","0.2ms","Response Time")]:
            st.markdown("<div style='background:#101c2e;border:1px solid #1e3352;border-radius:8px;padding:14px 18px;margin-bottom:10px;display:flex;align-items:center;gap:16px;'><span style='font-size:22px;'>" + icon + "</span><div><div style='font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;color:#00d4ff;'>" + val + "</div><div style='font-size:12px;color:#7a9bbf;'>" + lbl + "</div></div></div>", unsafe_allow_html=True)
    _,cc,_ = st.columns([1,1,1])
    with cc: st.link_button("Book Demo Langsung", WA_LINK_DEMO, use_container_width=True)

    # TESTIMONIALS
    st.markdown("""
    <div class='section-wrapper'>
        <div class='section-header'>Kata Mereka yang <span class='section-accent'>Sudah Merasakan</span></div>
        <div class='section-subheader'>Bisnis nyata, penghematan nyata</div>
    </div>""", unsafe_allow_html=True)
    t1,t2,t3 = st.columns(3)
    TESTI = [
        ("Sebelum pakai V-Guard, kasir saya melakukan void hampir setiap malam. Sekarang semuanya ter-record dan saya bisa tidur tenang.","Bpk. Timotius M.","Owner Kafe & Resto, Jakarta Selatan","Hemat ±Rp 8 Juta/bulan"),
        ("Stok saya sering selisih tapi saya kira itu wajar. Ternyata ada kebocoran dari supplier. V-Guard langsung deteksi hari pertama.","Ibu Riana S.","Pemilik Minimarket, 3 Cabang Tangerang","Selisih stok turun 94%"),
        ("Fitur H-7 reminder invoice sangat membantu cash flow. Tidak ada lagi piutang yang lupa ditagih lebih dari seminggu.","Bpk. Doni A.","Distributor FMCG, Bekasi","Collection rate +31%"),
    ]
    for col,(text,author,role,result) in zip([t1,t2,t3],TESTI):
        with col:
            st.markdown("<div class='testimonial-card'><div class='stars'>★★★★★</div><div class='testimonial-text'>\"" + text + "\"</div><div class='testimonial-author'>" + author + "</div><div class='testimonial-role'>" + role + "</div><div style='margin-top:12px;padding:8px 12px;background:#00d4ff11;border-radius:6px;font-size:12px;color:#00d4ff;font-family:JetBrains Mono,monospace;'>✓ " + result + "</div></div>", unsafe_allow_html=True)

    # FINAL CTA
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0d1a2e,#0a1628);padding:48px;text-align:center;border-top:1px solid #1e3352;border-bottom:1px solid #1e3352;'>
        <div style='font-family:Rajdhani,sans-serif;font-size:36px;font-weight:700;color:#e8f4ff;margin-bottom:12px;'>Siap Menutup Kebocoran Bisnis Anda?</div>
        <div style='font-size:15px;color:#7a9bbf;margin-bottom:28px;'>Konsultasi gratis 30 menit dengan tim V-Guard AI. Tidak ada kewajiban apapun.</div>
    </div>""", unsafe_allow_html=True)
    _,cf1,cf2,_ = st.columns([1,1,1,1])
    with cf1: st.link_button("Book Demo Gratis", WA_LINK_DEMO, use_container_width=True)
    with cf2: st.link_button("Chat Sekarang", WA_LINK_KONSUL, use_container_width=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

# =============================================================================
# 15. PAGE: PRODUK & HARGA
# =============================================================================
elif menu == "Produk & Harga":
    st.markdown("<div style='padding:40px 48px 0;'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-title'>Pilih Tingkat <span style='color:#00d4ff;'>Perlindungan</span> Bisnis Anda</div>"
        "<div class='page-subtitle'>Dari UMKM 1 kasir hingga korporasi multi-cabang — setiap tier mengaktifkan agen AI yang tepat.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    PACKAGES = [
        {"key":"LITE","name":"V-LITE","badge_cls":"badge-entry","badge_txt":"Entry Level","focus":"Fondasi keamanan digital untuk usaha satu kasir","price":"Rp 150.000","period":"/ bulan","setup":"Setup: Rp 250.000","popular":False,"ultra":False,"plug_play":True,"features":["Deteksi VOID & Cancel","Daily AI Summary via WhatsApp","Dashboard Web Real-Time","Laporan Kebocoran Otomatis","Support via WhatsApp"]},
        {"key":"PRO","name":"V-PRO","badge_cls":"badge-pro","badge_txt":"Pro","focus":"Otomasi admin, stok, & audit bank tanpa input manual","price":"Rp 450.000","period":"/ bulan","setup":"Setup: Rp 750.000","popular":True,"ultra":False,"plug_play":True,"features":["Semua fitur V-LITE","VCS Secure Integration","Bank Statement Audit Otomatis","Input Invoice via OCR","Laporan PDF Terjadwal","Support Prioritas 24/7"]},
        {"key":"ADVANCE","name":"V-ADVANCE","badge_cls":"badge-adv","badge_txt":"Pengawas Aktif","focus":"Mata AI pengawas aktif — visual, stok & multi-cabang","price":"Rp 1.200.000","period":"/ bulan","setup":"Setup: Rp 3.500.000","popular":False,"ultra":False,"plug_play":False,"features":["Semua fitur V-PRO","CCTV AI — Visual Cashier Audit","WhatsApp Fraud Alarm Instan","H-7 Auto Collection Reminder","Multi-Cabang Dashboard"]},
        {"key":"ELITE","name":"V-ELITE","badge_cls":"badge-ent","badge_txt":"Korporasi","focus":"Kedaulatan data penuh — server privat & AI forensik","price":"Mulai Rp 3.500.000","period":"/ bulan","setup":"Setup: Rp 10.000.000","popular":False,"ultra":False,"plug_play":False,"features":["Semua fitur V-ADVANCE","Deep Learning Forensik AI","Dedicated Private Server","Custom AI SOP per Divisi","On-site Implementation","SLA 99.9% Uptime"]},
        {"key":"ULTRA","name":"V-ULTRA","badge_cls":"badge-ultra","badge_txt":"Executive","focus":"White-Label & 10 Elite AI Squad aktif penuh","price":"Custom Quote","period":"Harga khusus korporasi","setup":"Konsultasi strategis gratis","popular":False,"ultra":True,"plug_play":False,"features":["Seluruh ekosistem V-ELITE","White-Label Platform","Executive BI Dashboard C-Level","10 Elite AI Squad serentak","Dedicated AI Strategist","V-Guard ERP Liaison Protocol"]},
    ]

    st.markdown("<div style='padding:28px 40px 0;'>", unsafe_allow_html=True)
    cards_html = ""
    for pkg in PACKAGES:
        feat_html = "".join(
            "<div class='pkg-feature" + ("-ultra" if pkg["ultra"] else "") + "'>"
            "<span class='pkg-check" + ("-ultra" if pkg["ultra"] else "") + "'>✓</span>" + f + "</div>"
            for f in pkg["features"]
        )
        install_html = "<span class='install-pill install-pnp'>Plug &amp; Play</span>" if pkg["plug_play"] else "<span class='install-pill install-pro'>Teknisi Profesional</span>"
        if pkg["popular"]:   label_html,card_cls = "<div class='hot-label'>TERLARIS</div>","pkg-card-popular"
        elif pkg["ultra"]:   label_html,card_cls = "<div class='ultra-label'>EKSKLUSIF</div>","pkg-card-ultra"
        else:                label_html,card_cls = "","pkg-card"
        name_cls  = "pkg-name-ultra" if pkg["ultra"] else "pkg-name"
        price_cls = "pkg-price-ultra" if pkg["ultra"] else "pkg-price"
        pkg_key   = "V-" + pkg["key"]
        ord_link  = ORDER_LINKS.get(pkg_key, WA_LINK_KONSUL)
        order_btn = "<a href='" + ord_link + "' target='_blank' style='display:block;margin-top:14px;padding:10px;text-align:center;background:linear-gradient(135deg,#0091ff,#00d4ff);color:#000;font-family:Rajdhani,sans-serif;font-size:13px;font-weight:700;border-radius:6px;text-decoration:none;letter-spacing:.5px;'>Order Sekarang</a>"
        cards_html += (
            "<div style='flex:1;min-width:0;padding-top:16px;'><div class='" + card_cls + "' style='height:100%;'>"
            + label_html + "<span class='tier-badge " + pkg["badge_cls"] + "'>" + pkg["badge_txt"] + "</span>"
            + "<div class='" + name_cls + "'>" + pkg["name"] + "</div>"
            + "<div class='pkg-focus'>" + pkg["focus"] + "</div>"
            + "<hr class='pkg-divider'>"
            + "<div class='" + price_cls + "'>" + pkg["price"] + "</div>"
            + "<div class='pkg-period'>" + pkg["period"] + "</div>"
            + "<div class='pkg-setup'>" + pkg["setup"] + "</div>"
            + install_html + "<hr class='pkg-divider'>"
            + "<div class='pkg-features-grow'>" + feat_html + "</div>"
            + order_btn + "</div></div>"
        )
    st.markdown("<div style='display:flex;flex-direction:row;gap:12px;align-items:stretch;width:100%;margin-bottom:24px;'>" + cards_html + "</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='padding:0 48px 16px;'><div style='background:#060b14;border:1px solid #1e3352;border-radius:8px;padding:14px 20px;font-size:12px;color:#7a9bbf;line-height:1.8;'><b style='color:#00e676;'>Plug &amp; Play (V-LITE &amp; V-PRO):</b> Setup mandiri, tanpa teknisi, langsung aktif dalam hitungan menit.&nbsp;&nbsp;<b style='color:#ffab00;'>Teknisi Profesional (V-ADVANCE ke atas):</b> Integrasi khusus oleh teknisi V-Guard di lokasi bisnis Anda.</div></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    _,ctm,_ = st.columns([1.5,1,1.5])
    with ctm: st.link_button("Konsultasi Paket via WhatsApp", WA_LINK_KONSUL, use_container_width=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

# =============================================================================
# 16. PAGE: KALKULATOR ROI
# =============================================================================
elif menu == "Kalkulator ROI":
    st.markdown("<div style='padding:40px 48px;'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-title'>🧮 Kalkulator <span style='color:#00d4ff;'>ROI V-Guard</span></div>"
        "<div class='page-subtitle'>Hitung estimasi penghematan dan ROI bulanan bisnis Anda secara real-time.</div>",
        unsafe_allow_html=True,
    )

    col_form, col_result = st.columns([1, 1.2], gap="large")

    with col_form:
        st.markdown("<div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;padding:24px;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#00d4ff;margin-bottom:16px;'>Input Data Bisnis</div>", unsafe_allow_html=True)

        jenis_usaha = st.selectbox("Jenis Usaha", ["Warung / 1 Kasir", "Toko Ritel / Cafe", "Minimarket", "Multi-Cabang", "Korporasi"], key="roi_jenis")
        omzet_input = st.number_input("Omzet Bulanan (Rp)", min_value=0, value=50_000_000, step=5_000_000, key="roi_omzet")
        jml_kasir   = st.number_input("Jumlah Kasir", min_value=1, value=2, step=1, key="roi_kasir")
        jml_cabang  = st.number_input("Jumlah Cabang / Outlet", min_value=1, value=1, step=1, key="roi_cabang")
        kebocoran_pct = st.slider("Estimasi Kebocoran Saat Ini (%)", 1, 20, 5, key="roi_bocor")

        # Auto-detect paket
        if jenis_usaha == "Warung / 1 Kasir": auto_pkg = "V-LITE"
        elif jenis_usaha == "Toko Ritel / Cafe": auto_pkg = "V-PRO"
        elif jenis_usaha == "Minimarket": auto_pkg = "V-PRO"
        elif jenis_usaha == "Multi-Cabang": auto_pkg = "V-ADVANCE"
        else: auto_pkg = "V-ELITE"

        paket_dipilih = st.selectbox("Paket Yang Ingin Dievaluasi", ["V-LITE","V-PRO","V-ADVANCE","V-ELITE"], index=["V-LITE","V-PRO","V-ADVANCE","V-ELITE"].index(auto_pkg) if auto_pkg in ["V-LITE","V-PRO","V-ADVANCE","V-ELITE"] else 1, key="roi_paket")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_result:
        biaya_paket = HARGA_NUMERIK.get(paket_dipilih, 450_000)
        bocor_rp    = omzet_input * (kebocoran_pct / 100)
        diselamatkan = bocor_rp * 0.88
        biaya_total  = biaya_paket
        net_saved    = diselamatkan - biaya_total
        roi_pct      = (net_saved / biaya_total * 100) if biaya_total > 0 else 0
        payback_hari = (biaya_total / diselamatkan * 30) if diselamatkan > 0 else 0
        hb, hs       = HARGA_MAP.get(paket_dipilih, ("—","—"))

        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#0d1626,#101c2e);border:1px solid #1e3352;border-radius:12px;padding:24px;margin-bottom:16px;'>
            <div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#00d4ff;margin-bottom:20px;'>Hasil Kalkulasi — {paket_dipilih}</div>
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;'>
                <div style='background:#060b14;border:1px solid #1e3352;border-radius:8px;padding:16px;text-align:center;'>
                    <div style='font-size:11px;color:#7a9bbf;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px;'>Kebocoran/Bulan</div>
                    <div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#ff3b5c;'>Rp {bocor_rp:,.0f}</div>
                </div>
                <div style='background:#060b14;border:1px solid #1e3352;border-radius:8px;padding:16px;text-align:center;'>
                    <div style='font-size:11px;color:#7a9bbf;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px;'>Diselamatkan (88%)</div>
                    <div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#00e676;'>Rp {diselamatkan:,.0f}</div>
                </div>
                <div style='background:#060b14;border:1px solid #1e3352;border-radius:8px;padding:16px;text-align:center;'>
                    <div style='font-size:11px;color:#7a9bbf;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px;'>Biaya Paket/Bulan</div>
                    <div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#ffab00;'>{hb}</div>
                </div>
                <div style='background:#060b14;border:1px solid #1e3352;border-radius:8px;padding:16px;text-align:center;'>
                    <div style='font-size:11px;color:#7a9bbf;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px;'>Net Saving/Bulan</div>
                    <div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#00d4ff;'>Rp {net_saved:,.0f}</div>
                </div>
            </div>
            <div style='background:linear-gradient(135deg,#00e67611,#00d4ff11);border:1px solid #00e67633;border-radius:10px;padding:20px;text-align:center;'>
                <div style='font-size:12px;color:#7a9bbf;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px;'>ROI Bulanan Estimasi</div>
                <div style='font-family:Rajdhani,sans-serif;font-size:56px;font-weight:700;background:linear-gradient(135deg,#00e676,#00d4ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>{roi_pct:.0f}%</div>
                <div style='font-size:12px;color:#7a9bbf;'>Payback Period: ±{payback_hari:.0f} hari</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        ord_link = ORDER_LINKS.get(paket_dipilih, WA_LINK_KONSUL)
        st.link_button(f"Order {paket_dipilih} — {hb}/bln", ord_link, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

# =============================================================================
# 17. PAGE: PORTAL KLIEN
# =============================================================================
elif menu == "Portal Klien":
    st.markdown("<div style='padding:32px 48px;'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-title'>🏠 Portal <span style='color:#00d4ff;'>Klien</span></div>"
        "<div class='page-subtitle'>Masuk dengan Client ID Anda, atau ajukan pembelian baru.</div>",
        unsafe_allow_html=True,
    )

    # Check if client is logged in
    if st.session_state.client_logged_in and st.session_state.client_data:
        klien = st.session_state.client_data
        cid   = klien.get("Client_ID","—")
        pkg   = klien.get("Produk","V-LITE")
        status = klien.get("Status","Menunggu Pembayaran")
        hb, hs = HARGA_MAP.get(pkg, ("—","—"))

        # Header
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#060b14,#0a1628);border:1px solid #1e3352;border-radius:14px;padding:24px;margin-bottom:24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;'>
            <div>
                <div style='font-family:Rajdhani,sans-serif;font-size:24px;font-weight:700;color:#e8f4ff;'>Selamat datang, {klien.get("Nama Klien","Klien")} 👋</div>
                <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#00d4ff;margin-top:4px;'>{cid} · {pkg} · {"🟢 AKTIF" if status == "Aktif" else "🟡 Menunggu Aktivasi"}</div>
            </div>
            <div style='text-align:right;'>
                <div style='font-size:12px;color:#7a9bbf;'>Paket</div>
                <div style='font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;color:#00d4ff;'>{pkg}</div>
                <div style='font-size:11px;color:#7a9bbf;'>{hb}/bln</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        portal_tabs = st.tabs(["📋 Akun Saya", "🔗 Referral", "📊 Dashboard", "📁 Dokumen"])

        with portal_tabs[0]:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;padding:20px;'>
                    <div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:#00d4ff;margin-bottom:16px;'>Informasi Akun</div>
                    <div style='font-size:13px;color:#7a9bbf;margin-bottom:8px;'><b style='color:#e8f4ff;'>Nama:</b> {klien.get("Nama Klien","—")}</div>
                    <div style='font-size:13px;color:#7a9bbf;margin-bottom:8px;'><b style='color:#e8f4ff;'>Usaha:</b> {klien.get("Nama Usaha","—")}</div>
                    <div style='font-size:13px;color:#7a9bbf;margin-bottom:8px;'><b style='color:#e8f4ff;'>WhatsApp:</b> {klien.get("WhatsApp","—")}</div>
                    <div style='font-size:13px;color:#7a9bbf;margin-bottom:8px;'><b style='color:#e8f4ff;'>Paket:</b> {pkg}</div>
                    <div style='font-size:13px;color:#7a9bbf;margin-bottom:8px;'><b style='color:#e8f4ff;'>Status:</b> <span style='color:{"#00e676" if status=="Aktif" else "#ffab00"};'>{status}</span></div>
                    <div style='font-size:13px;color:#7a9bbf;'><b style='color:#e8f4ff;'>Client ID:</b> <span style='font-family:JetBrains Mono,monospace;color:#00d4ff;'>{cid}</span></div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                if status == "Aktif":
                    st.markdown(f"""
                    <div style='background:#00e67611;border:1px solid #00e67633;border-radius:12px;padding:20px;margin-bottom:12px;'>
                        <div style='font-size:12px;color:#00e676;font-family:JetBrains Mono,monospace;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>✅ Akun Aktif</div>
                        <div style='font-size:13px;color:#7a9bbf;'>Sistem V-Guard AI aktif mengawasi bisnis Anda 24/7.</div>
                        <div style='margin-top:12px;font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#00e676;'>Live</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    pay_link = buat_payment_link(pkg, klien.get("Nama Klien","Klien"))
                    st.markdown(f"""
                    <div style='background:#ffab0011;border:1px solid #ffab0033;border-radius:12px;padding:20px;margin-bottom:12px;'>
                        <div style='font-size:12px;color:#ffab00;font-family:JetBrains Mono,monospace;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>⏳ Menunggu Aktivasi</div>
                        <div style='font-size:13px;color:#7a9bbf;margin-bottom:12px;'>Selesaikan pembayaran untuk mengaktifkan akun Anda.</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.link_button("📲 Bayar via WhatsApp", pay_link, use_container_width=True)

        with portal_tabs[1]:
            ref_link = buat_referral_link(cid)
            st.markdown(f"""
            <div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;padding:24px;margin-bottom:16px;'>
                <div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#00d4ff;margin-bottom:8px;'>🔗 Link Referral Anda</div>
                <div style='font-size:13px;color:#7a9bbf;margin-bottom:16px;'>Bagikan link ini ke rekan bisnis Anda. Setiap referral yang berhasil, Anda mendapatkan komisi menarik!</div>
                <div class='ref-link-box'>{ref_link}</div>
                <div style='margin-top:12px;font-size:12px;color:#7a9bbf;'>💰 Komisi referral: 10% dari biaya setup klien yang mendaftar melalui link Anda</div>
            </div>
            """, unsafe_allow_html=True)
            wa_share = "https://wa.me/?text=" + urllib.parse.quote(f"Halo! Saya sudah pakai V-Guard AI untuk keamanan bisnis saya — hasilnya luar biasa! Coba daftar di sini: {ref_link}")
            st.link_button("📲 Bagikan via WhatsApp", wa_share, use_container_width=True)

        with portal_tabs[2]:
            if status == "Aktif":
                st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#e8f4ff;margin-bottom:16px;'>📊 Dashboard Ringkasan</div>", unsafe_allow_html=True)
                if pkg in ("V-LITE","V-PRO"):
                    d1,d2,d3,d4 = st.columns(4)
                    d1.metric("VOID Hari Ini", "2", delta="▲ dari kemarin", delta_color="inverse")
                    d2.metric("Normal", "18", delta="✓ Sehat")
                    d3.metric("Alert Terkirim", "1", delta="via WhatsApp")
                    d4.metric("Uptime", "99.9%", delta="30 hari terakhir")

                if pkg in ("V-ADVANCE","V-ELITE","V-ULTRA"):
                    st.markdown("#### 🔍 Fraud Intelligence (Contoh Data)")
                    df_sample = get_sample_transaksi()
                    hasil = scan_fraud_lokal(df_sample)
                    sa,sb,sc = st.columns(3)
                    sa.metric("VOID Mencurigakan", len(hasil["void"]))
                    sb.metric("Pola Duplikat", len(hasil["fraud"]))
                    sc.metric("Selisih Saldo", len(hasil["suspicious"]))
                    st.dataframe(df_sample[["ID_Transaksi","Kasir","Jumlah","Status","Waktu"]].head(6), use_container_width=True, hide_index=True)

                if pkg in ("V-PRO","V-ADVANCE","V-ELITE","V-ULTRA"):
                    st.markdown("#### 📹 Monitor CCTV")
                    st.markdown("""
                    <div class='cctv-frame' style='max-width:480px;'>
                        <div style='text-align:center;color:#1e3352;'>
                            <div style='font-size:48px;margin-bottom:8px;'>📹</div>
                            <div style='font-size:13px;font-family:JetBrains Mono,monospace;'>CCTV Feed — Tersedia setelah hardware terpasang</div>
                            <div style='font-size:11px;color:#7a9bbf;margin-top:4px;'>Hubungi teknisi V-Guard untuk integrasi</div>
                        </div>
                        <div class='cctv-overlay'>● REC 04:22:18</div>
                        <div class='cctv-alert'>⚠ WAITING FEED</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Dashboard akan tersedia setelah akun Anda diaktifkan.")

        with portal_tabs[3]:
            st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#e8f4ff;margin-bottom:16px;'>📁 Folder Dokumen</div>", unsafe_allow_html=True)
            docs = [
                ("📋", "Kontrak Langganan", "Dokumen perjanjian layanan V-Guard AI", "Tersedia"),
                ("🧾", "Invoice Terakhir", f"Invoice {datetime.date.today().strftime('%B %Y')}", "PDF"),
                ("📘", "Panduan Onboarding", "Langkah aktivasi & setup sistem", "Tersedia"),
                ("🔒", "Kebijakan Privasi Data", "SLA & data privacy agreement", "Tersedia"),
                ("📊", "Laporan Bulanan", f"Laporan AI {datetime.date.today().strftime('%B %Y')}", "Dalam Proses" if status != "Aktif" else "PDF"),
            ]
            for icon, name, desc, badge in docs:
                badge_color = "#00e676" if badge in ("Tersedia","PDF") else "#ffab00"
                st.markdown(f"<div style='background:#101c2e;border:1px solid #1e3352;border-radius:8px;padding:14px 18px;margin-bottom:8px;display:flex;align-items:center;gap:14px;'><span style='font-size:22px;'>{icon}</span><div style='flex:1;'><div style='font-size:14px;color:#e8f4ff;font-weight:500;'>{name}</div><div style='font-size:12px;color:#7a9bbf;'>{desc}</div></div><span style='font-family:JetBrains Mono,monospace;font-size:10px;color:{badge_color};border:1px solid {badge_color}44;background:{badge_color}11;padding:3px 10px;border-radius:20px;'>{badge}</span></div>", unsafe_allow_html=True)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        if st.button("Logout Portal", key="portal_logout"):
            st.session_state.client_logged_in = False
            st.session_state.client_data = None
            st.rerun()

    else:
        # Login / Register
        tab_login, tab_daftar = st.tabs(["🔑 Login Client ID", "📝 Ajukan Pembelian Baru"])

        with tab_login:
            _,lc,_ = st.columns([1,1.2,1])
            with lc:
                st.markdown("<div class='login-card'>", unsafe_allow_html=True)
                st.markdown("<div style='text-align:center;margin-bottom:20px;'><div style='font-size:36px;'>🔑</div><div style='font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;color:#e8f4ff;'>Login Portal Klien</div><div style='font-size:13px;color:#7a9bbf;margin-top:4px;'>Masukkan Client ID yang diberikan tim V-Guard</div></div>", unsafe_allow_html=True)
                cid_input = st.text_input("Client ID", placeholder="VG-XXXXXX", key="portal_cid")
                if st.button("Masuk ke Portal", type="primary", use_container_width=True, key="btn_portal_login"):
                    found = None
                    for k in st.session_state.db_umum:
                        if k.get("Client_ID","").upper() == cid_input.strip().upper():
                            found = k
                            break
                    if found:
                        st.session_state.client_logged_in = True
                        st.session_state.client_data = found
                        st.rerun()
                    else:
                        st.error("Client ID tidak ditemukan. Hubungi tim V-Guard untuk bantuan.")
                st.markdown("</div>", unsafe_allow_html=True)

        with tab_daftar:
            if st.session_state.get("portal_form_submitted"):
                st.success("✅ Pengajuan Anda telah diterima! Tim V-Guard akan menghubungi Anda dalam 1×24 jam untuk proses aktivasi.")
                if st.button("Ajukan Lagi", key="btn_reset_form"):
                    st.session_state.portal_form_submitted = False
                    st.rerun()
            else:
                _,fc,_ = st.columns([0.5,2,0.5])
                with fc:
                    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
                    st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;color:#00d4ff;margin-bottom:16px;'>📝 Formulir Pendaftaran</div>", unsafe_allow_html=True)
                    nama_klien = st.text_input("Nama Lengkap *", placeholder="Budi Santoso", key="form_nama")
                    nama_usaha = st.text_input("Nama Usaha *", placeholder="Toko Maju Jaya", key="form_usaha")
                    wa_klien   = st.text_input("Nomor WhatsApp *", placeholder="08123456789", key="form_wa")
                    paket_form = st.selectbox("Paket yang Diminati *", ["V-LITE","V-PRO","V-ADVANCE","V-ELITE","V-ULTRA"], key="form_paket")
                    catatan    = st.text_area("Ceritakan singkat bisnis Anda", placeholder="Toko kelontong 2 kasir, omzet ±20jt/bln...", height=80, key="form_catatan")

                    if st.button("Kirim Pengajuan", type="primary", use_container_width=True, key="btn_submit_form"):
                        if nama_klien and nama_usaha and wa_klien:
                            cid_baru = buat_client_id(nama_klien, wa_klien)
                            pengajuan = {
                                "Client_ID": cid_baru,
                                "Nama Klien": nama_klien,
                                "Nama Usaha": nama_usaha,
                                "WhatsApp": wa_klien,
                                "Produk": paket_form,
                                "Status": "Menunggu Pembayaran",
                                "Catatan": catatan,
                                "Tanggal": str(datetime.date.today()),
                                "Source": "Portal Klien",
                            }
                            st.session_state.db_umum.append(pengajuan)
                            st.session_state.db_pengajuan.append(pengajuan)
                            st.session_state.portal_form_submitted = True
                            st.rerun()
                        else:
                            st.error("Lengkapi semua field yang wajib diisi (*).")
                    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

# =============================================================================
# 18. PAGE: INVESTOR AREA
# =============================================================================
elif menu == "Investor Area":
    st.markdown("<div style='padding:32px 48px;'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-title'>📈 Investor <span style='color:#ffd700;'>Area</span></div>"
        "<div class='page-subtitle'>V-Guard AI — Ekosistem Keamanan Bisnis Digital Indonesia</div>",
        unsafe_allow_html=True,
    )

    if not st.session_state.investor_pw_ok:
        _,ic,_ = st.columns([1,1,1])
        with ic:
            st.markdown("<div class='login-card' style='border-color:#ffd70033;'>", unsafe_allow_html=True)
            st.markdown("<div style='text-align:center;margin-bottom:20px;'><div style='font-size:36px;'>🔒</div><div style='font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;color:#ffd700;'>Restricted Access</div><div style='font-size:13px;color:#7a9bbf;margin-top:4px;'>Area khusus investor & mitra strategis</div></div>", unsafe_allow_html=True)
            inv_pw = st.text_input("Access Code", type="password", key="inv_pw")
            if st.button("Masuk Investor Area", type="primary", use_container_width=True, key="btn_inv"):
                if inv_pw == "investor2026":
                    st.session_state.investor_pw_ok = True
                    st.rerun()
                else:
                    st.error("Access code salah. Hubungi Founder untuk akses.")
                    st.markdown(f"📲 [Chat dengan Founder]({WA_LINK_KONSUL})")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Investor Dashboard
        st.markdown("""
        <div style='background:linear-gradient(135deg,#0d1626,#1a1500);border:1px solid #ffd70033;border-radius:14px;padding:24px;margin-bottom:24px;'>
            <div style='font-family:JetBrains Mono,monospace;font-size:10px;color:#ffd700;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;'>CONFIDENTIAL — INVESTOR BRIEF</div>
            <div style='font-family:Rajdhani,sans-serif;font-size:28px;font-weight:700;color:#ffd700;margin-bottom:4px;'>V-Guard AI Intelligence</div>
            <div style='font-size:14px;color:#7a9bbf;'>AI-Powered Business Security Ecosystem · Indonesia Market</div>
        </div>
        """, unsafe_allow_html=True)

        # KPI Stats
        inv_stats = [
            ("TAM","Rp 4,2 Triliun","Total Addressable Market Indonesia"),
            ("ARPU","Rp 650.000","Average Revenue Per User/bulan"),
            ("Churn Target","< 3%","Monthly churn rate target"),
            ("Gross Margin","78%","Target margin produk SaaS"),
            ("CAC","Rp 850.000","Customer Acquisition Cost estimasi"),
            ("LTV","Rp 23,4 Jt","Customer Lifetime Value (36 bln)"),
        ]
        cols = st.columns(3)
        for i,(title,val,desc) in enumerate(inv_stats):
            with cols[i%3]:
                st.markdown(f"<div class='investor-stat'><div class='investor-stat-num'>{val}</div><div style='font-family:Rajdhani,sans-serif;font-size:14px;font-weight:700;color:#e8f4ff;margin-top:4px;'>{title}</div><div class='investor-stat-lbl'>{desc}</div></div>", unsafe_allow_html=True)
                st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        st.divider()
        inv_tabs = st.tabs(["📊 Proyeksi Keuangan", "🗺️ Roadmap", "💡 Model Bisnis"])

        with inv_tabs[0]:
            data_proj = {
                "Bulan": ["Q1 2026","Q2 2026","Q3 2026","Q4 2026","Q1 2027","Q2 2027"],
                "Klien": [15, 45, 120, 280, 500, 900],
                "MRR (Rp Jt)": [8, 28, 78, 182, 325, 585],
                "Net Profit (Rp Jt)": [-5, 2, 18, 52, 110, 220],
            }
            df_proj = pd.DataFrame(data_proj)
            st.dataframe(df_proj, use_container_width=True, hide_index=True)
            st.markdown("""
            <div style='background:#101c2e;border:1px solid #1e3352;border-radius:8px;padding:14px 18px;margin-top:12px;font-size:12px;color:#7a9bbf;'>
                ⚠️ Proyeksi berdasarkan asumsi pertumbuhan organik + digital marketing. Angka aktual dapat berbeda tergantung eksekusi dan kondisi pasar.
            </div>
            """, unsafe_allow_html=True)

        with inv_tabs[1]:
            roadmap = [
                ("Q1 2026","🚀 Launch","Peluncuran V-LITE & V-PRO. Target 50 klien awal dari network founder.","done"),
                ("Q2 2026","⚡ Growth","Aktivasi V-ADVANCE & V-ELITE. Ekspansi ke 5 kota besar.","active"),
                ("Q3 2026","🌐 Scale","Launch V-ULTRA & white-label. Rekrut 10 reseller aktif.","upcoming"),
                ("Q4 2026","🏆 Series A Prep","Konsolidasi data, audit keuangan, pitch Series A.","upcoming"),
                ("2027","🌏 Expansion","Ekspansi ke Malaysia & Philippines. 1.000+ klien aktif.","upcoming"),
            ]
            for quarter, title, desc, status in roadmap:
                color = "#00e676" if status=="done" else "#00d4ff" if status=="active" else "#7a9bbf"
                border = "border-left:3px solid " + color + ";"
                st.markdown(f"<div style='background:#101c2e;border:1px solid #1e3352;{border}border-radius:8px;padding:16px 20px;margin-bottom:10px;display:flex;align-items:flex-start;gap:16px;'><div style='font-family:JetBrains Mono,monospace;font-size:11px;color:{color};min-width:60px;margin-top:2px;'>{quarter}</div><div><div style='font-family:Rajdhani,sans-serif;font-size:15px;font-weight:700;color:#e8f4ff;'>{title}</div><div style='font-size:13px;color:#7a9bbf;margin-top:4px;'>{desc}</div></div></div>", unsafe_allow_html=True)

        with inv_tabs[2]:
            st.markdown("""
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:16px;'>
                <div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;padding:20px;'>
                    <div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:#00d4ff;margin-bottom:12px;'>💰 Revenue Streams</div>
                    <div style='font-size:13px;color:#7a9bbf;line-height:1.8;'>
                    ● Langganan bulanan (SaaS MRR)<br>
                    ● Biaya setup & implementasi<br>
                    ● White-label licensing (V-ULTRA)<br>
                    ● Komisi referral program<br>
                    ● API usage fees (enterprise)
                    </div>
                </div>
                <div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;padding:20px;'>
                    <div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:#ffd700;margin-bottom:12px;'>🛡️ Keunggulan Kompetitif</div>
                    <div style='font-size:13px;color:#7a9bbf;line-height:1.8;'>
                    ● AI local-first (bahasa & konteks Indonesia)<br>
                    ● 5-tier pricing menjangkau semua segmen<br>
                    ● CCTV + Kasir + Bank dalam 1 platform<br>
                    ● Plug & Play — tidak butuh IT team<br>
                    ● WhatsApp-native alert system
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.link_button("📲 Jadwalkan Meeting dengan Founder", WA_LINK_KONSUL, use_container_width=False)
        if st.button("Logout Investor Area", key="inv_logout"):
            st.session_state.investor_pw_ok = False
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

# =============================================================================
# 19. PAGE: ADMIN ACCESS — WAR ROOM
# =============================================================================
elif menu == "Admin Access":
    st.markdown("<div style='padding:32px 48px;'>", unsafe_allow_html=True)

    if not st.session_state.admin_logged_in:
        _,lc,_ = st.columns([1,1,1])
        with lc:
            st.markdown("<div class='login-card'><div style='text-align:center;margin-bottom:24px;'><div style='font-size:40px;'>🔒</div><div style='font-family:Rajdhani,sans-serif;font-size:24px;font-weight:700;color:#e8f4ff;'>Admin Access</div><div style='font-size:13px;color:#7a9bbf;margin-top:4px;'>Restricted — Authorized Personnel Only</div></div></div>", unsafe_allow_html=True)
            admin_pw = st.text_input("Access Code", type="password", key="admin_pw_main")
            if st.button("Masuk ke War Room", type="primary", use_container_width=True, key="btn_admin_main"):
                if admin_pw == "w1nbju8282":
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("Access Code salah!")
    else:
        st.markdown(
            "<div class='page-title'>⚔️ The War Room — <span style='color:#00d4ff;'>Admin Control Center</span></div>"
            "<div class='page-subtitle'>V-GUARD AI Ecosystem ©2026 — Founder Edition</div>",
            unsafe_allow_html=True,
        )

        col_logout = st.columns([4,1])[1]
        with col_logout:
            if st.button("Logout", key="logout_main"):
                st.session_state.admin_logged_in = False
                st.rerun()

        war_tabs = st.tabs([
            "📊 Dashboard",
            "🤖 AI Agents",
            "📹 Monitor CCTV",
            "🚨 Fraud Scanner",
            "📋 Pengajuan Masuk",
            "👥 Aktivasi Klien",
            "🗄️ Database",
        ])

        # ── TAB 0: DASHBOARD ──────────────────────────────────────────────
        with war_tabs[0]:
            total_k = len(st.session_state.db_umum)
            aktif_k = sum(1 for k in st.session_state.db_umum if k.get("Status")=="Aktif")
            pending_k = sum(1 for k in st.session_state.db_umum if k.get("Status")=="Menunggu Pembayaran")
            mrr     = hitung_proyeksi_omset(st.session_state.db_umum)

            m1,m2,m3,m4,m5 = st.columns(5)
            m1.metric("Total Klien", str(total_k))
            m2.metric("Klien Aktif", str(aktif_k))
            m3.metric("Pending", str(pending_k))
            m4.metric("MRR", f"Rp {mrr:,.0f}")
            m5.metric("API Cost Session", f"Rp {st.session_state.api_cost_total:,.0f}")

            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

            # System log
            st.markdown("""
            <div class='demo-mockup'>
                <div style='margin-bottom:12px;'>
                    <span class='demo-dot demo-red'></span><span class='demo-dot demo-yellow'></span><span class='demo-dot demo-green'></span>
                    <span style='margin-left:12px;color:#7a9bbf;font-size:11px;'>v-guard-warroom / system-log</span>
                </div>
                <span style='color:#00e676;'>✓</span> [SYSTEM] V-Guard AI v2.0 — Boot selesai<br>
                <span style='color:#00d4ff;'>▸</span> [SENTINEL] 10 AI Agents terdaftar · 8 Aktif · 2 Standby<br>
                <span style='color:#00e676;'>✓</span> [LIAISON] Fraud scanner lokal aktif — filter anomali only<br>
                <span style='color:#00d4ff;'>▸</span> [CONCIERGE] Chat widget aktif di semua halaman<br>
                <span style='color:#ffab00;'>▸</span> [AUDITOR] Sinkronisasi mutasi bank — jadwal 06:00 WIB<br>
                <span style='color:#00e676;'>✓</span> [WHISPERBOT] WhatsApp gateway — Connected<br>
                <span style='color:#00d4ff;'>▸</span> [ORACLE] Predictive model last update: hari ini 02:00 WIB<br>
                <span style='color:#7a9bbf;'>_</span>
            </div>
            """, unsafe_allow_html=True)

            dp_log = st.session_state.get("detected_package")
            if dp_log:
                bul,_ = HARGA_MAP.get(dp_log,("—","—"))
                st.markdown("<div class='match-banner' style='margin-top:16px;'><div class='match-banner-title'>🎯 Paket Terdeteksi dari Sesi Chat CS</div><div class='match-banner-body'>Cocok: <b>" + dp_log + "</b> — " + bul + "/bln</div></div>", unsafe_allow_html=True)

        # ── TAB 1: AI AGENTS ──────────────────────────────────────────────
        with war_tabs[1]:
            st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#e8f4ff;margin-bottom:4px;'>🤖 10 Elite AI Agent Squad</div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size:13px;color:#7a9bbf;margin-bottom:20px;'>Status real-time seluruh agen AI dalam ekosistem V-Guard.</div>", unsafe_allow_html=True)

            # Agent status simulation
            agent_statuses = ["active","active","active","active","active","standby","active","active","standby","active"]

            for row_start in range(0, 10, 2):
                cols = st.columns(2)
                for i, col in enumerate(cols):
                    idx = row_start + i
                    if idx >= len(AI_AGENTS): break
                    agent = AI_AGENTS[idx]
                    st_code = agent_statuses[idx]
                    color_map = {"active":"#00e676","standby":"#ffab00","offline":"#ff3b5c"}
                    label_map = {"active":"ACTIVE","standby":"STANDBY","offline":"OFFLINE"}
                    color = color_map[st_code]
                    label = label_map[st_code]

                    # Kill switch
                    ks = st.session_state.agent_kill_switch.get(agent["id"], False)
                    with col:
                        st.markdown(f"""
                        <div class='agent-card agent-card-{"active" if not ks else "offline"}'>
                            <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;'>
                                <div style='display:flex;align-items:center;gap:8px;'>
                                    <span style='font-size:22px;'>{agent['icon']}</span>
                                    <div>
                                        <div style='font-family:Rajdhani,sans-serif;font-size:15px;font-weight:700;color:#e8f4ff;'>Agent #{agent['id']} · {agent['name']}</div>
                                        <div style='font-size:11px;color:#7a9bbf;'>{agent['role']}</div>
                                    </div>
                                </div>
                                <span style='font-family:JetBrains Mono,monospace;font-size:9px;color:{"#ff3b5c" if ks else color};border:1px solid {"#ff3b5c44" if ks else color+"44"};background:{"#ff3b5c11" if ks else color+"11"};padding:2px 8px;border-radius:20px;'>{"KILLED" if ks else label}</span>
                            </div>
                            <div style='font-size:12px;color:#7a9bbf;line-height:1.5;'>{agent['desc']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        btn_label = "🔴 Kill Agent" if not ks else "🟢 Restart Agent"
                        if st.button(btn_label, key=f"ks_{agent['id']}", use_container_width=True):
                            st.session_state.agent_kill_switch[agent['id']] = not ks
                            st.rerun()
                        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

        # ── TAB 2: MONITOR CCTV ───────────────────────────────────────────
        with war_tabs[2]:
            st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#e8f4ff;margin-bottom:4px;'>📹 Monitor CCTV — Visual Cashier Audit</div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size:13px;color:#7a9bbf;margin-bottom:20px;'>Live feed dari kamera klien. Teks transaksi dirender otomatis oleh VisualEye AI.</div>", unsafe_allow_html=True)

            cam_locations = ["Outlet Sudirman — Kasir 1", "Outlet Sudirman — Kasir 2", "Resto Central — Kasir Utama", "Cabang Tangerang — Pintu Masuk"]
            cam_cols = st.columns(2)
            for i, (col, loc) in enumerate(zip(cam_cols * 2, cam_locations)):
                with col:
                    now_str = datetime.datetime.now().strftime("%H:%M:%S")
                    alert_show = i == 0  # First camera shows alert
                    st.markdown(f"""
                    <div class='cctv-frame' style='margin-bottom:12px;'>
                        <div style='text-align:center;'>
                            <div style='font-size:32px;margin-bottom:6px;'>📹</div>
                            <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#1e3352;'>{loc}</div>
                            <div style='font-size:10px;color:#7a9bbf;margin-top:4px;'>Feed tersedia setelah hardware terpasang</div>
                        </div>
                        <div class='cctv-overlay'>● REC {now_str} · Cam {i+1}</div>
                        {"<div class='cctv-alert'>⚠ VOID DETECTED</div>" if alert_show else '<div style="position:absolute;top:8px;right:8px;font-family:JetBrains Mono,monospace;font-size:10px;color:#00e676;background:#00000088;padding:4px 8px;border-radius:4px;">✓ NORMAL</div>'}
                    </div>
                    """, unsafe_allow_html=True)
                    if i % 2 == 1:
                        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

            st.divider()
            st.markdown("""
            <div style='background:#101c2e;border:1px solid #1e3352;border-radius:10px;padding:16px 20px;'>
                <div style='font-family:Rajdhani,sans-serif;font-size:15px;font-weight:700;color:#00d4ff;margin-bottom:10px;'>VisualEye AI — Overlay Transaksi</div>
                <div style='font-size:12px;color:#7a9bbf;line-height:1.8;'>
                    Saat hardware CCTV terpasang dan feed aktif, VisualEye AI akan:<br>
                    ● Render <b style='color:#e8f4ff;'>teks transaksi real-time</b> di atas rekaman video<br>
                    ● Sorot <b style='color:#ff3b5c;'>frame mencurigakan</b> dengan batas merah otomatis<br>
                    ● Log <b style='color:#ffab00;'>timestamp</b> setiap transaksi dengan akurasi milidetik<br>
                    ● Kirim <b style='color:#00e676;'>klip anomali</b> ke Owner via WhatsApp dalam < 5 detik
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── TAB 3: FRAUD SCANNER ──────────────────────────────────────────
        with war_tabs[3]:
            st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#e8f4ff;margin-bottom:4px;'>🚨 Fraud Intelligence Scanner — The Liaison</div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size:13px;color:#7a9bbf;margin-bottom:16px;'>Agent #4 Liaison: Filter lokal anomali sebelum dikirim ke API — hemat biaya hingga 80%.</div>", unsafe_allow_html=True)

            df_trx = get_sample_transaksi()
            hasil  = scan_fraud_lokal(df_trx)

            fs1,fs2,fs3 = st.columns(3)
            fs1.metric("VOID / Cancel",  len(hasil["void"]),      delta="Tidak Wajar" if hasil["void"].shape[0] else "Aman")
            fs2.metric("Duplikat Kasir", len(hasil["fraud"]),     delta="Terdeteksi"  if hasil["fraud"].shape[0] else "Aman")
            fs3.metric("Selisih Saldo",  len(hasil["suspicious"]),delta="Anomali"     if hasil["suspicious"].shape[0] else "Aman")

            tv,tf,ts = st.tabs(["VOID","Duplikat","Selisih"])
            with tv:
                if not hasil["void"].empty:
                    st.error("Transaksi VOID mencurigakan ditemukan!")
                    st.dataframe(hasil["void"][["ID_Transaksi","Cabang","Kasir","Jumlah","Waktu"]], use_container_width=True)
                    for cab in hasil["void"]["Cabang"].unique():
                        am = urllib.parse.quote(f"⚠️ ALERT V-GUARD: VOID mencurigakan di [{cab}]. Cek kasir segera!")
                        st.link_button(f"Alert Owner — {cab}", f"https://wa.me/{WA_NUMBER}?text={am}")
                else: st.success("Tidak ada VOID mencurigakan.")
            with tf:
                if not hasil["fraud"].empty:
                    st.error("Pola duplikat < 5 menit terdeteksi!")
                    st.dataframe(hasil["fraud"][["ID_Transaksi","Cabang","Kasir","Jumlah","selisih_menit"]], use_container_width=True)
                else: st.success("Tidak ada pola duplikat.")
            with ts:
                if not hasil["suspicious"].empty:
                    st.error("Selisih saldo ditemukan!")
                    st.dataframe(hasil["suspicious"][["ID_Transaksi","Cabang","Kasir","Saldo_Fisik","Saldo_Sistem","selisih_saldo"]], use_container_width=True)
                else: st.success("Saldo seimbang.")

            st.divider()
            st.markdown("<div style='font-size:12px;color:#7a9bbf;background:#101c2e;border:1px solid #1e3352;border-radius:8px;padding:10px 14px;margin-bottom:12px;'>💡 <b>Efisiensi API Liaison:</b> Hanya anomali yang dikirim ke Gemini — transaksi normal difilter lokal. Hemat 80% biaya API.</div>", unsafe_allow_html=True)

            if model_vguard:
                if st.button("🤖 Jalankan AI Deep Scan (Anomali Only)", type="primary", key="btn_deep_scan"):
                    fraud_rows = pd.concat([hasil["void"],hasil["fraud"],hasil["suspicious"]]).drop_duplicates(subset=["ID_Transaksi"])
                    if fraud_rows.empty:
                        st.success("Tidak ada anomali untuk dianalisis.")
                    else:
                        with st.spinner("Agent Liaison + Gemini menganalisis anomali..."):
                            try:
                                prompt = "Analisis HANYA data anomali ini (transaksi normal sudah difilter Agent Liaison):\n\n" + fraud_rows.to_string(index=False) + "\n\nBerikan: 1) Pola kecurangan yang terdeteksi, 2) Kasir paling berisiko, 3) Rekomendasi taktis untuk Owner. Format ringkas dan actionable."
                                resp = model_vguard.generate_content(prompt)
                                res_text = resp.text.strip() if resp.text else "Tidak ada pola kritis tambahan."
                                st.session_state.api_cost_total += 150
                                st.markdown("### Hasil AI Deep Scan:")
                                st.markdown(res_text)
                            except Exception:
                                st.warning("Sistem sedang memproses data. Coba lagi dalam beberapa saat.")
            else:
                st.info("Sambungkan GOOGLE_API_KEY di st.secrets untuk AI Deep Scan.")

        # ── TAB 4: PENGAJUAN MASUK ────────────────────────────────────────
        with war_tabs[4]:
            st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#e8f4ff;margin-bottom:4px;'>📋 Pengajuan Masuk — Antrian Aktivasi</div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size:13px;color:#7a9bbf;margin-bottom:20px;'>Pengajuan dari Portal Klien yang menunggu proses aktivasi.</div>", unsafe_allow_html=True)

            pending_list = [k for k in st.session_state.db_umum if k.get("Status") == "Menunggu Pembayaran"]

            if not pending_list:
                st.info("Tidak ada pengajuan pending saat ini.")
            else:
                for i, klien in enumerate(pending_list):
                    cid  = klien.get("Client_ID","—")
                    pkg  = klien.get("Produk","V-LITE")
                    hb, hs = HARGA_MAP.get(pkg, ("—","—"))
                    wa_tgt = klien.get("WhatsApp",WA_NUMBER)
                    if not wa_tgt.startswith("62"): wa_tgt = "62" + wa_tgt.lstrip("0")

                    st.markdown(f"""
                    <div class='client-card-pending'>
                        <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;'>
                            <div>
                                <div style='font-family:Rajdhani,sans-serif;font-size:17px;font-weight:700;color:#e8f4ff;'>{klien.get("Nama Klien","—")} — {klien.get("Nama Usaha","—")}</div>
                                <div style='font-family:JetBrains Mono,monospace;font-size:10px;color:#00d4ff;margin-bottom:4px;'>{cid} · {pkg} · {hb}/bln</div>
                                <div style='font-size:12px;color:#7a9bbf;'>WA: {klien.get("WhatsApp","—")} · Daftar: {klien.get("Tanggal","—")} · Source: {klien.get("Source","—")}</div>
                                {f'<div style="font-size:12px;color:#7a9bbf;margin-top:4px;">Catatan: {klien.get("Catatan","")}</div>' if klien.get("Catatan") else ""}
                            </div>
                            <span class='client-badge-pending'>Menunggu Pembayaran</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    pc1, pc2, pc3 = st.columns(3)
                    with pc1:
                        pay_link = buat_payment_link(pkg, klien.get("Nama Klien","Klien"))
                        st.link_button("💳 Kirim Link Pembayaran", pay_link, use_container_width=True, key=f"pay_{cid}_{i}")
                    with pc2:
                        # Find index in db_umum
                        db_idx = next((j for j,k in enumerate(st.session_state.db_umum) if k.get("Client_ID")==cid), None)
                        if db_idx is not None:
                            if st.button("✅ Aktivasi Akun", key=f"aktiv_{cid}_{i}", type="primary", use_container_width=True):
                                st.session_state.db_umum[db_idx]["Status"] = "Aktif"
                                st.rerun()
                    with pc3:
                        dash = buat_dashboard_link(cid)
                        akses_txt = urllib.parse.quote(
                            f"Halo {klien.get('Nama Klien','Klien')},\n\n"
                            f"✅ Akun V-Guard Anda telah AKTIF!\n\n"
                            f"🔑 Client ID: {cid}\n"
                            f"🔗 Dashboard: {BASE_APP_URL}\n"
                            f"📦 Paket: {pkg}\n\n"
                            f"Selamat menggunakan V-Guard AI! Jika ada pertanyaan, balas pesan ini.\n— Tim V-Guard AI"
                        )
                        st.link_button("📲 Kirim Akses Klien", f"https://wa.me/{wa_tgt}?text={akses_txt}", use_container_width=True, key=f"access_{cid}_{i}")
                    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        # ── TAB 5: AKTIVASI KLIEN ─────────────────────────────────────────
        with war_tabs[5]:
            st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#e8f4ff;margin-bottom:4px;'>👥 Manajemen Klien Aktif</div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size:13px;color:#7a9bbf;margin-bottom:16px;'>Kelola status, kirim invoice, dan akses dashboard klien.</div>", unsafe_allow_html=True)

            # Add new client form
            with st.expander("➕ Tambah Klien Manual"):
                ac1,ac2 = st.columns(2)
                with ac1:
                    new_nama   = st.text_input("Nama Klien", key="new_nama")
                    new_usaha  = st.text_input("Nama Usaha", key="new_usaha")
                    new_wa     = st.text_input("WhatsApp", key="new_wa")
                with ac2:
                    new_produk = st.selectbox("Produk", ["V-LITE","V-PRO","V-ADVANCE","V-ELITE","V-ULTRA"], key="new_produk")
                    new_status = st.selectbox("Status Awal", ["Menunggu Pembayaran","Aktif"], key="new_status")
                if st.button("Tambahkan Klien", type="primary", key="btn_add_client"):
                    if new_nama and new_wa:
                        cid_new = buat_client_id(new_nama, new_wa)
                        st.session_state.db_umum.append({
                            "Client_ID": cid_new, "Nama Klien": new_nama,
                            "Nama Usaha": new_usaha, "WhatsApp": new_wa,
                            "Produk": new_produk, "Status": new_status,
                            "Tanggal": str(datetime.date.today()), "Source": "Admin Manual",
                        })
                        st.success(f"Klien ditambahkan! Client ID: {cid_new}")
                        st.rerun()
                    else:
                        st.error("Nama dan WhatsApp wajib diisi.")

            if not st.session_state.db_umum:
                st.info("Belum ada klien terdaftar.")
            else:
                for i,klien in enumerate(st.session_state.db_umum):
                    if "Client_ID" not in klien:
                        st.session_state.db_umum[i]["Client_ID"] = buat_client_id(klien["Nama Klien"],klien.get("WhatsApp",""))
                    cid = st.session_state.db_umum[i]["Client_ID"]
                    is_aktif = klien.get("Status")=="Aktif"
                    hb,hs = HARGA_MAP.get(klien["Produk"],("—","—"))
                    card_cls  = "client-card-aktif" if is_aktif else "client-card-pending"
                    badge_cls = "client-badge-aktif" if is_aktif else "client-badge-pending"
                    status_txt = "Aktif" if is_aktif else "Menunggu Pembayaran"
                    st.markdown("<div class='" + card_cls + "'><div style='font-family:Rajdhani,sans-serif;font-size:17px;font-weight:700;color:#e8f4ff;'>" + klien["Nama Klien"] + " — " + klien.get("Nama Usaha","-") + "</div><div style='font-family:JetBrains Mono,monospace;font-size:10px;color:#00d4ff;margin-bottom:6px;'>" + cid + " · " + klien["Produk"] + "</div><div style='font-size:12px;color:#7a9bbf;margin-bottom:8px;'>WA: " + klien.get("WhatsApp","-") + " · " + hb + "/bln · Setup: " + hs + "</div><span class='" + badge_cls + "'>" + status_txt + "</span></div>", unsafe_allow_html=True)
                    wa_tgt = klien.get("WhatsApp",WA_NUMBER)
                    if not wa_tgt.startswith("62"): wa_tgt = "62" + wa_tgt.lstrip("0")
                    ac1,ac2,ac3,ac4 = st.columns(4)
                    with ac1:
                        if is_aktif:
                            if st.button("⏸ Deactivate", key=f"deact_{i}", use_container_width=True):
                                st.session_state.db_umum[i]["Status"] = "Menunggu Pembayaran"; st.rerun()
                        else:
                            if st.button("✅ Activate", key=f"act_{i}", use_container_width=True, type="primary"):
                                st.session_state.db_umum[i]["Status"] = "Aktif"; st.rerun()
                    with ac2:
                        inv_txt = urllib.parse.quote(f"INVOICE V-GUARD AI\n\nYth. {klien['Nama Klien']}\nPaket: {klien['Produk']}\nBulanan: {hb}\nSetup: {hs}\n\nTransfer: BCA 3450074658 a/n Erwin Sinaga\nKonfirmasi setelah transfer.\n— Tim V-Guard AI")
                        st.link_button("🧾 Invoice", f"https://wa.me/{wa_tgt}?text={inv_txt}", use_container_width=True, key=f"inv_{i}")
                    with ac3:
                        dash = buat_dashboard_link(cid)
                        akses_txt = urllib.parse.quote(f"Halo {klien['Nama Klien']},\n\n✅ Akun V-Guard Anda AKTIF!\n\n🔑 Client ID: {cid}\n🔗 Portal: {BASE_APP_URL}\n📦 Paket: {klien['Produk']}\n\n— Tim V-Guard AI")
                        st.link_button("🔑 Kirim Akses", f"https://wa.me/{wa_tgt}?text={akses_txt}", use_container_width=True, key=f"akses_{i}")
                    with ac4:
                        ref_link = buat_referral_link(cid)
                        ref_txt = urllib.parse.quote(f"Link referral Anda: {ref_link}\nKomisi 10% dari setiap klien yang berhasil!")
                        st.link_button("🔗 Referral", f"https://wa.me/{wa_tgt}?text={ref_txt}", use_container_width=True, key=f"ref_{i}")
                    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

        # ── TAB 6: DATABASE ───────────────────────────────────────────────
        with war_tabs[6]:
            if st.session_state.db_umum:
                df_db = pd.DataFrame(st.session_state.db_umum)
                if "Client_ID" in df_db.columns:
                    df_db["Dashboard"] = df_db["Client_ID"].apply(buat_dashboard_link)
                    df_db["Referral"]  = df_db["Client_ID"].apply(buat_referral_link)
                st.dataframe(df_db, use_container_width=True, hide_index=True)
                st.download_button(
                    "⬇️ Download CSV",
                    data=df_db.to_csv(index=False).encode("utf-8"),
                    file_name=f"vguard_clients_{datetime.date.today()}.csv",
                    mime="text/csv",
                )
                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Hapus Semua Data (Reset)", key="btn_reset_db"):
                    st.session_state.db_umum = []
                    st.session_state.db_pengajuan = []
                    st.rerun()
            else:
                st.info("Database masih kosong. Klien yang mendaftar akan muncul di sini.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

# =============================================================================
# 20. FOOTER
# =============================================================================
st.markdown(
    "<div style='background:#060b14;border-top:1px solid #1e3352;padding:28px 48px;"
    "display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;'>"
    "<div><span style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#00d4ff;'>V-Guard AI Intelligence</span>"
    "<span style='color:#7a9bbf;font-size:12px;margin-left:12px;'>V-GUARD AI Ecosystem ©2026</span></div>"
    "<div style='font-size:12px;color:#7a9bbf;'>Digitizing Trust · Eliminating Leakage · Protecting Every Rupiah</div></div>",
    unsafe_allow_html=True,
)
