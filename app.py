# =============================================================================
# V-GUARD AI INTELLIGENCE — app.py  (V-GUARD AI Ecosystem ©2026)
# =============================================================================

import streamlit as st
import os
import urllib.parse
import hashlib
import pandas as pd
import datetime
import time
import re

# =============================================================================
# 1. MULTI-CHANNEL TRACKING
# =============================================================================
_qp = st.query_params
if "tracking_ref" not in st.session_state:
    st.session_state["tracking_ref"]    = _qp.get("ref",    "")
if "tracking_source" not in st.session_state:
    st.session_state["tracking_source"] = _qp.get("source", "organic")

# =============================================================================
# 2. AI ENGINE
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
# 4. SESSION STATE
# =============================================================================
_DEFAULTS = {
    "admin_logged_in":   False,
    "db_umum":           [],
    "api_cost_total":    0.0,
    "cs_chat_history":   [],
    "agent_kill_switch": {},
    "detected_package":  None,
    "pending_quick":     None,
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

BASE_APP_URL = "https://v-guard-ai.streamlit.app"
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

# =============================================================================
# 6. PRODUCT MATCHING
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
        f"👉 **[Lihat Detail {pkg} & Aktivasi Sekarang]({plink})**\n\n"
        f"📲 **[Order {pkg} via WhatsApp]({olink})**\n\n"
        f"_Setiap hari tanpa V-Guard adalah hari yang berisiko. Saya siap memandu Anda! 🚀_"
    )

# =============================================================================
# 7. CS SYSTEM PROMPT
# =============================================================================
CS_SYSTEM_PROMPT = """
Anda adalah Sentinel CS — Konsultan AI pribadi resmi V-Guard AI Intelligence.
Gunakan sapaan Bapak, Ibu, atau Kakak. Gaya: hangat, persuasif, semi-formal.

PRODUK & HARGA:
V-LITE    Rp 150.000/bln | Setup Rp 250.000     | PLUG & PLAY
V-PRO     Rp 450.000/bln | Setup Rp 750.000     | PLUG & PLAY
V-ADVANCE Rp 1.200.000/bln | Setup Rp 3.500.000 | Teknisi
V-ELITE   Mulai Rp 3.500.000/bln | Setup Rp 10jt | Teknisi
V-ULTRA   Custom | Konsultasi | Teknisi

PRODUCT MATCHING:
CCTV/Pantau/Monitor -> V-PRO (Rp 450rb/bln) | Link order: https://wa.me/6282122190885?text=order+V-PRO
Kasir Curang/Fraud Detection -> V-ELITE (Rp 3,5jt/bln) | Link order: https://wa.me/6282122190885?text=order+V-ELITE
Usaha Kecil/1 Kasir/Warung -> V-LITE (Rp 150rb/bln)
Multi-Cabang/Banyak Stok -> V-ADVANCE (Rp 1,2jt/bln)
White-Label/Enterprise -> V-ULTRA

ATURAN PENJUALAN:
- Jika user tanya harga: TANYA DULU jenis usaha dan jumlah kasir/cabang
- Setelah tahu kebutuhan: rekomendasikan 1 paket + link detail + link order WA
- Akhiri setiap respons dengan pertanyaan follow-up
- JANGAN sebut error/maintenance/API. Jika masalah: "Maaf, sistem sedang padat, mohon tunggu sebentar"

ROI: Kebocoran 5% omzet, V-Guard cegah 88%. ROI = (penghematan - biaya paket) / biaya paket x 100%
INSTALASI: V-LITE & V-PRO = PLUG & PLAY saja. V-ADVANCE ke atas = wajib teknisi.
"""

# =============================================================================
# 8. HELPERS
# =============================================================================
def buat_client_id(nama, no_hp):
    raw = nama.strip().lower() + no_hp.strip()
    return "VG-" + hashlib.md5(raw.encode()).hexdigest()[:6].upper()

def buat_dashboard_link(cid):
    return BASE_APP_URL + "/Portal_Klien?id=" + cid

def buat_referral_link(cid):
    return BASE_APP_URL + "/?ref=" + cid

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
# 9. AI RESPONSE
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
                f"- Omzet: **Rp {omzet_val:,.0f}/bln**\n"
                f"- Kebocoran 5%: **Rp {bocor:,.0f}/bln**\n"
                f"- Diselamatkan V-Guard (88%): **Rp {saved:,.0f}/bln**\n"
                f"- ROI estimasi: **{roi:.0f}%** 🚀"
            )

        if any(k in m for k in ["harga","berapa","biaya","tarif","paket"]):
            base = (
                "Tentu, saya bantu jelaskan harga, Bapak/Ibu! 😊\n\n"
                "Sebelumnya, boleh saya tahu dulu — **jenis usaha apa** yang Bapak/Ibu kelola "
                "dan berapa **kasir atau cabang** yang dioperasikan?\n\n"
                "Dengan info itu, saya langsung rekomendasikan paket yang paling tepat 😄"
            )
        elif any(k in m for k in ["cctv","kamera","pantau","monitor","visual"]):
            base = (
                "Untuk kebutuhan **monitoring & CCTV AI**, saya rekomendasikan **V-PRO** 📹\n\n"
                "✅ CCTV AI — teks transaksi tampil langsung di rekaman\n"
                "✅ Audit rekening bank otomatis\n"
                "✅ **Plug & Play** — aktif dalam menit tanpa teknisi"
            )
            if not pkg: base += build_package_cta("V-PRO")
        elif any(k in m for k in ["fraud","curang","kecurangan","void mencurigakan","kasir curang","cek fraud"]):
            base = (
                "Saya sangat memahami kekhawatiran Bapak/Ibu soal kecurangan kasir 🛡️\n\n"
                "Untuk **deteksi fraud kasir level lanjut**, V-ELITE adalah solusinya:\n"
                "✅ Deep Learning Forensik — deteksi pola void & duplikat\n"
                "✅ Private Server — data 100% di server sendiri\n"
                "✅ SLA Uptime 99.9% — monitoring tidak pernah berhenti"
            )
            if not pkg: base += build_package_cta("V-ELITE")
        elif any(k in m for k in ["apa itu","v-guard","vguard","tentang","penjelasan"]):
            base = (
                "Halo Bapak/Ibu! Senang bisa berkenalan 😊\n\n"
                "**V-Guard AI Intelligence** adalah sistem keamanan bisnis berbasis AI "
                "yang bekerja 24/7 mengawasi setiap rupiah di kasir, stok, dan rekening bank Anda.\n\n"
                "🏆 Hasil nyata dari klien kami:\n"
                "- Pencegahan kebocoran hingga **88%**\n"
                "- Deteksi anomali dalam **< 5 detik**\n"
                "- ROI rata-rata: **400–900%/bulan**\n\n"
                "Boleh saya tahu bisnis apa yang Bapak/Ibu kelola? 🙏"
            )
        elif any(k in m for k in ["roi","hemat","bocor","rugi","omzet"]):
            base = (
                "Pertanyaan yang sangat cerdas, Bapak/Ibu! 💡\n\n"
                "Rata-rata bisnis kehilangan **3–15% omzet** setiap bulan tanpa disadari.\n"
                "V-Guard AI mencegah hingga **88% kebocoran** secara otomatis."
            )
            if not roi_block:
                base += "\n\nBoleh saya tahu **omzet bulanan** bisnis Bapak/Ibu? 😊"
        elif any(k in m for k in ["lihat paket","daftar paket","semua paket"]):
            base = (
                "V-Guard tersedia dalam 5 tier:\n\n"
                "| Paket | Bulanan | Instalasi |\n|-------|---------|----------|\n"
                "| V-LITE | Rp 150rb | Plug & Play ✅ |\n"
                "| V-PRO | Rp 450rb | Plug & Play ✅ |\n"
                "| V-ADVANCE | Rp 1,2jt | Teknisi Profesional |\n"
                "| V-ELITE | Mulai Rp 3,5jt | Teknisi Profesional |\n"
                "| V-ULTRA | Custom | Teknisi Profesional |\n\n"
                "Boleh ceritakan jenis usaha Bapak/Ibu? Saya pilihkan yang paling cocok 😊"
            )
        elif any(k in m for k in ["book demo","demo","coba"]):
            base = (
                "Demo V-Guard **gratis 30 menit** — Pak Erwin langsung tunjukkan cara sistem "
                "mendeteksi kecurangan secara real-time.\n\n"
                f"📲 **[Book Demo Gratis Sekarang]({WA_LINK_DEMO})**"
            )
        else:
            base = (
                "Halo! Saya **Sentinel CS**, konsultan AI pribadi V-Guard AI 👋\n\n"
                "Saya di sini untuk membantu Bapak/Ibu **menutup kebocoran bisnis secara permanen**.\n\n"
                "Ceritakan bisnis Bapak/Ibu:\n"
                "- Berapa **jumlah kasir atau cabang**?\n"
                "- Berapa **omzet bulanan** rata-rata?\n\n"
                "Saya langsung hitung potensi kebocoran dan rekomendasikan solusi terbaik 💡"
            )

        result = base + roi_block
        if pkg and "Order" not in result:
            result += build_package_cta(pkg)
        if "wa.me/" not in result:
            result += f"\n\n📞 Konsultasi: [Chat Tim V-Guard](https://wa.me/{WA_NUMBER})"
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
                           f"Akhiri dengan pertanyaan follow-up.]")
            resp = chat_obj.send_message(prompt)
            ans  = resp.text.strip() if resp.text else ""
            if ans:
                st.session_state.api_cost_total += 200
                return ans
        except Exception:
            pass
    return fallback(user_message, detected)

# =============================================================================
# 10. CSS — Original Dark Theme + Kodee Chat Overlay
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
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;color:var(--text-primary)!important;background-color:var(--bg-primary)!important;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#08111f 0%,#0d1a2e 100%)!important;border-right:1px solid var(--border)!important;}
section[data-testid="stSidebar"] *{color:var(--text-primary)!important;}
.main .block-container{padding:0!important;max-width:100%!important;}
.stButton>button{background:linear-gradient(135deg,var(--accent2),var(--accent))!important;color:#000!important;font-family:'Rajdhani',sans-serif!important;font-weight:700!important;font-size:15px!important;border:none!important;border-radius:6px!important;height:46px!important;transition:all .2s ease!important;}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 0 20px var(--border-glow)!important;}
.stButton>button[kind="secondary"]{background:transparent!important;color:var(--accent)!important;border:1px solid var(--accent)!important;}
a[data-testid="stLinkButton"] button{background:linear-gradient(135deg,#25D366,#128C7E)!important;color:white!important;font-weight:700!important;border-radius:6px!important;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stNumberInput>div>div>input{background-color:var(--bg-card)!important;border:1px solid var(--border)!important;color:var(--text-primary)!important;border-radius:6px!important;}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{border-color:var(--accent)!important;box-shadow:0 0 10px var(--border-glow)!important;}
[data-testid="stMetric"]{background:var(--bg-card)!important;border:1px solid var(--border)!important;border-radius:10px!important;padding:16px!important;}
[data-testid="stMetricLabel"]{color:var(--text-muted)!important;font-size:12px!important;}
[data-testid="stMetricValue"]{color:var(--accent)!important;font-family:'Rajdhani',sans-serif!important;font-size:28px!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--bg-secondary)!important;border-bottom:1px solid var(--border)!important;}
.stTabs [data-baseweb="tab"]{color:var(--text-muted)!important;font-family:'Rajdhani',sans-serif!important;font-weight:600!important;font-size:15px!important;}
.stTabs [aria-selected="true"]{color:var(--accent)!important;border-bottom:2px solid var(--accent)!important;}
[data-testid="stDataFrame"]{border:1px solid var(--border)!important;border-radius:8px!important;}
[data-testid="stExpander"]{border:1px solid var(--border)!important;border-radius:8px!important;background:var(--bg-card)!important;}
.stProgress>div>div>div{background:linear-gradient(90deg,var(--accent2),var(--accent))!important;}
::-webkit-scrollbar{width:6px;}::-webkit-scrollbar-track{background:var(--bg-primary);}::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}::-webkit-scrollbar-thumb:hover{background:var(--accent);}
.hero-section{background:linear-gradient(135deg,#060b14 0%,#0a1628 50%,#080f1e 100%);padding:60px 48px 48px;position:relative;overflow:hidden;border-bottom:1px solid var(--border);}
.hero-section::before{content:'';position:absolute;top:-50%;right:-10%;width:600px;height:600px;background:radial-gradient(circle,#00d4ff11 0%,transparent 70%);pointer-events:none;}
.hero-badge{display:inline-block;background:linear-gradient(135deg,#00d4ff22,#0091ff22);border:1px solid var(--accent);color:var(--accent)!important;font-family:'JetBrains Mono',monospace!important;font-size:11px!important;padding:4px 14px;border-radius:20px;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:20px;}
.hero-title{font-family:'Rajdhani',sans-serif!important;font-size:58px!important;font-weight:700!important;line-height:1.1!important;color:var(--text-primary)!important;margin-bottom:8px!important;}
.hero-title .accent{color:var(--accent)!important;}
.hero-subtitle{font-size:19px!important;color:var(--text-muted)!important;line-height:1.7!important;max-width:520px;margin-bottom:36px!important;}
.pain-card{background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:20px;margin-bottom:12px;border-left:3px solid var(--danger);}
.pain-card:hover{border-color:var(--accent);background:var(--bg-hover);}
.pain-title{font-family:'Rajdhani',sans-serif!important;font-size:16px!important;font-weight:700!important;color:var(--text-primary)!important;}
.pain-desc{font-size:13px!important;color:var(--text-muted)!important;margin-top:4px;}
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
/* KODEE-STYLE CHAT BUBBLES */
.cs-section{background:linear-gradient(135deg,#060b14,#0a1628);border-top:1px solid #1e3352;padding:56px 48px;}
[data-testid="stChatMessage"]{background:transparent!important;border:none!important;padding:4px 0!important;}
[data-testid="stChatMessageContent"]{background:#101c2e!important;border:1px solid #1e3352!important;border-radius:18px 18px 18px 4px!important;padding:14px 18px!important;font-size:14px!important;line-height:1.75!important;color:var(--text-primary)!important;box-shadow:0 2px 12px rgba(0,0,0,0.3)!important;}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"]{background:linear-gradient(135deg,#0091ff,#00d4ff)!important;border:none!important;border-radius:18px 18px 4px 18px!important;color:#000!important;font-weight:500!important;}
[data-testid="stChatInput"]{background:var(--bg-card)!important;border:1px solid var(--border)!important;border-radius:14px!important;}
[data-testid="stChatInput"] textarea{background:transparent!important;color:var(--text-primary)!important;font-size:14px!important;}
[data-testid="stChatInput"] textarea::placeholder{color:var(--text-muted)!important;}
.match-banner{background:linear-gradient(135deg,#00d4ff18,#0091ff11);border:1px solid #00d4ff55;border-left:3px solid #00d4ff;border-radius:10px;padding:16px 20px;margin-bottom:16px;}
.match-banner-title{font-family:'Rajdhani',sans-serif!important;font-size:15px!important;font-weight:700!important;color:#00d4ff!important;margin-bottom:4px;}
.match-banner-body{font-size:13px!important;color:#9ab8d4!important;}
.client-card-aktif{background:#101c2e;border:1px solid #1e3352;border-left:3px solid #00e676;border-radius:12px;padding:20px;margin-bottom:14px;}
.client-card-pending{background:#101c2e;border:1px solid #1e3352;border-left:3px solid #ffab00;border-radius:12px;padding:20px;margin-bottom:14px;}
.client-badge-aktif{display:inline-block;background:#00e67618;color:#00e676!important;border:1px solid #00e67644;border-radius:20px;font-size:10px!important;padding:2px 10px;font-family:'JetBrains Mono',monospace!important;}
.client-badge-pending{display:inline-block;background:#ffab0018;color:#ffab00!important;border:1px solid #ffab0044;border-radius:20px;font-size:10px!important;padding:2px 10px;font-family:'JetBrains Mono',monospace!important;}
.login-card{background:var(--bg-card);border:1px solid var(--border);border-radius:14px;padding:36px;}
.ref-link-box{background:#060b14;border:1px solid #1e3352;border-radius:8px;padding:12px 16px;font-family:'JetBrains Mono',monospace;font-size:12px;color:#00d4ff;word-break:break-all;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 11. SIDEBAR — 3 menu items, no WA text, no AI status text
# =============================================================================
with st.sidebar:
    st.markdown("""
    <div style='padding:20px 0 16px;border-bottom:1px solid #1e3352;margin-bottom:16px;'>
        <div class='sidebar-logo'>V-GUARD AI</div>
        <div class='sidebar-tagline'>Digital Business Auditor</div>
        <div style='text-align:center;margin-top:8px;font-size:11px;color:#7a9bbf;font-family:JetBrains Mono,monospace;'>
            <span class='status-dot'></span>System Online
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
    menu = st.radio("", ["Beranda","Produk & Harga","Admin Access"], label_visibility="collapsed")

# =============================================================================
# 12. BERANDA — ORIGINAL CONTENT + Kodee Chatbot di Bawah
# =============================================================================
if menu == "Beranda":

    # ── HERO ORIGINAL ──────────────────────────────────────────────────────
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

    # ── STATS ORIGINAL ─────────────────────────────────────────────────────
    st.markdown("<div class='section-wrapper'>", unsafe_allow_html=True)
    s1,s2,s3,s4 = st.columns(4)
    for col,(n,l) in zip([s1,s2,s3,s4],[
        ("88%","Kebocoran Berhasil Dicegah"),("24/7","Monitoring Otomatis"),
        ("< 5 Dtk","Deteksi Real-Time"),("5 Tier","Solusi Semua Skala"),
    ]):
        with col:
            st.markdown("<div class='stat-card'><div class='stat-number'>" + n + "</div><div class='stat-label'>" + l + "</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── PAIN POINTS ORIGINAL ───────────────────────────────────────────────
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

    # ── FEATURES ORIGINAL ──────────────────────────────────────────────────
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

    # ── DEMO MOCKUP ORIGINAL ───────────────────────────────────────────────
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

    # ── TESTIMONIALS ORIGINAL ──────────────────────────────────────────────
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

    # ── FINAL CTA ORIGINAL ─────────────────────────────────────────────────
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0d1a2e,#0a1628);padding:48px;text-align:center;border-top:1px solid #1e3352;border-bottom:1px solid #1e3352;'>
        <div style='font-family:Rajdhani,sans-serif;font-size:36px;font-weight:700;color:#e8f4ff;margin-bottom:12px;'>Siap Menutup Kebocoran Bisnis Anda?</div>
        <div style='font-size:15px;color:#7a9bbf;margin-bottom:28px;'>Konsultasi gratis 30 menit dengan tim V-Guard AI. Tidak ada kewajiban apapun.</div>
    </div>""", unsafe_allow_html=True)

    _,cf1,cf2,_ = st.columns([1,1,1,1])
    with cf1: st.link_button("Book Demo Gratis", WA_LINK_DEMO, use_container_width=True)
    with cf2: st.link_button("Chat Sekarang", WA_LINK_KONSUL, use_container_width=True)

    # =========================================================================
    # CHATBOT SENTINEL CS — KODEE-STYLE BUBBLES (bagian yang di-upgrade)
    # =========================================================================
    st.markdown("""
    <div class='cs-section'>
        <div class='section-header'>Sentinel CS — <span class='section-accent'>Konsultan AI 24/7</span></div>
        <div class='section-subheader'>Tanya apa saja · Ketik atau klik topik di bawah · Jawaban instan</div>
    </div>""", unsafe_allow_html=True)

    cs_main, cs_side = st.columns([1.8,1], gap="large")

    with cs_main:

        # Pending quick pill handler
        new_input = None
        if st.session_state.get("pending_quick"):
            new_input = st.session_state.pending_quick
            st.session_state.pending_quick = None

        # Product match banner
        dp = st.session_state.get("detected_package")
        if dp:
            hb,hs = HARGA_MAP.get(dp,("Custom","—"))
            st.markdown(
                "<div class='match-banner'>"
                "<div class='match-banner-title'>🎯 Paket Yang Cocok untuk Anda: " + dp + "</div>"
                "<div class='match-banner-body'>" + hb + "/bln · Setup " + hs
                + " &nbsp;·&nbsp; <a href='" + PRODUCT_LINKS.get(dp,BASE_APP_URL) + "' target='_blank' style='color:#00d4ff;'>Lihat Detail</a>"
                + " &nbsp;|&nbsp; <a href='" + ORDER_LINKS.get(dp,WA_LINK_KONSUL) + "' target='_blank' style='color:#00e676;'>Order Sekarang</a>"
                + "</div></div>",
                unsafe_allow_html=True,
            )

        # Chat history — Kodee-style st.chat_message bubbles
        if not st.session_state.cs_chat_history:
            with st.chat_message("assistant", avatar="🛡️"):
                st.markdown(
                    "Halo! Saya **Sentinel CS**, konsultan AI pribadi V-Guard AI Intelligence 👋\n\n"
                    "Saya di sini untuk membantu Bapak/Ibu **menutup kebocoran bisnis secara permanen** "
                    "dengan teknologi AI yang bekerja 24/7 — tanpa lelah, tanpa kompromi.\n\n"
                    "Ceritakan bisnis Bapak/Ibu — berapa **kasir/cabang** dan **omzet bulanan** Anda? "
                    "Saya langsung hitung potensi penghematan dan rekomendasikan paket terbaik 💡"
                )
        else:
            for msg in st.session_state.cs_chat_history:
                with st.chat_message(msg["role"], avatar="🛡️" if msg["role"]=="assistant" else None):
                    st.markdown(msg["content"])

        # Quick Pills — Kodee-style
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        qp_cols = st.columns(4)
        quick_prompts = ["🛡️ Apa itu V-Guard?","📦 Lihat Paket","🔍 Cek Fraud Kasir","💰 Hitung ROI"]
        for i,(col,qp_text) in enumerate(zip(qp_cols,quick_prompts)):
            with col:
                if st.button(qp_text, key="beranda_qp_"+str(i), use_container_width=True):
                    st.session_state.pending_quick = qp_text
                    st.rerun()

        # Process pending quick pill
        if new_input:
            with st.chat_message("user"):
                st.markdown(new_input)
            st.session_state.cs_chat_history.append({"role":"user","content":new_input})
            with st.chat_message("assistant", avatar="🛡️"):
                with st.spinner("Sentinel CS sedang mengetik..."):
                    time.sleep(1.1)
                    answer = get_ai_response(new_input)
                st.markdown(answer)
            st.session_state.cs_chat_history.append({"role":"assistant","content":answer})

        # Chat input — Kodee-style fixed bottom input
        if user_msg := st.chat_input("Ceritakan bisnis Anda — kasir, cabang, atau masalah yang dihadapi...", key="chat_beranda"):
            with st.chat_message("user"):
                st.markdown(user_msg)
            st.session_state.cs_chat_history.append({"role":"user","content":user_msg})
            with st.chat_message("assistant", avatar="🛡️"):
                with st.spinner("Sentinel CS sedang mengetik..."):
                    time.sleep(1.1)
                    answer = get_ai_response(user_msg)
                st.markdown(answer)
            st.session_state.cs_chat_history.append({"role":"assistant","content":answer})

        # Reset button
        if st.session_state.cs_chat_history:
            st.markdown("<div style='text-align:right;margin-top:4px;'>", unsafe_allow_html=True)
            if st.button("🔄 Reset Chat", key="reset_chat_beranda"):
                st.session_state.cs_chat_history = []
                st.session_state["detected_package"] = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    with cs_side:
        st.markdown(
            "<div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;padding:20px;margin-bottom:16px;'>"
            "<div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:#00d4ff;margin-bottom:12px;'>🤖 Sentinel CS Bisa Bantu:</div>"
            + "".join([
                "<div style='display:flex;gap:8px;align-items:flex-start;margin-bottom:8px;'>"
                "<span style='color:#00e676;font-size:11px;flex-shrink:0;margin-top:2px;'>✓</span>"
                "<span style='font-size:12px;color:#7a9bbf;line-height:1.5;'>" + item + "</span></div>"
                for item in [
                    "Deteksi otomatis paket terbaik dari kata kunci Anda",
                    "Kirim link aktivasi & order langsung di chat",
                    "Hitung ROI & estimasi penghematan real-time",
                    "Jelaskan perbedaan Plug & Play vs Teknisi",
                    "Bandingkan fitur antar 5 tingkat paket",
                    "Jadwalkan demo langsung dengan Founder",
                ]
            ])
            + "</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='background:#0d1626;border:1px solid #1e3352;border-radius:12px;padding:18px;margin-bottom:16px;'>"
            "<div style='font-family:Rajdhani,sans-serif;font-size:14px;font-weight:700;color:#e8f4ff;margin-bottom:12px;'>🎯 Cara Cepat Dapat Rekomendasi:</div>"
            + "".join([
                "<div style='background:#101c2e;border-radius:6px;padding:8px 10px;margin-bottom:6px;font-size:11px;color:#7a9bbf;line-height:1.5;'>"
                "<span style='color:" + color + ";font-weight:700;'>" + pkg + "</span> → " + hint + "</div>"
                for pkg,hint,color in [
                    ("V-LITE","Sebutkan: warung, 1 kasir, kios","#00d4ff"),
                    ("V-PRO","Sebutkan: pantau toko, kamera, cafe","#6ac8ff"),
                    ("V-ADVANCE","Sebutkan: kasir, stok, banyak cabang","#b49fff"),
                    ("V-ELITE","Sebutkan: fraud kasir, kecurangan, server","#00e676"),
                    ("V-ULTRA","Sebutkan: white label, custom platform","#ffd700"),
                ]
            ])
            + "</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='background:#0d1626;border:1px solid #1e3352;border-radius:12px;padding:18px;'>"
            "<div style='font-family:Rajdhani,sans-serif;font-size:14px;font-weight:700;color:#e8f4ff;margin-bottom:12px;'>Panduan Instalasi</div>"
            "<div style='background:#00e67611;border:1px solid #00e67633;border-radius:8px;padding:10px;margin-bottom:8px;'>"
            "<div style='font-size:11px;font-weight:700;color:#00e676;font-family:JetBrains Mono,monospace;'>PLUG & PLAY ✅</div>"
            "<div style='font-size:11px;color:#7a9bbf;margin-top:4px;'>V-LITE & V-PRO — Mandiri, tanpa teknisi</div></div>"
            "<div style='background:#ffab0011;border:1px solid #ffab0033;border-radius:8px;padding:10px;'>"
            "<div style='font-size:11px;font-weight:700;color:#ffab00;font-family:JetBrains Mono,monospace;'>INTEGRASI PROFESIONAL 🔧</div>"
            "<div style='font-size:11px;color:#7a9bbf;margin-top:4px;'>V-ADVANCE ke atas — Teknisi V-Guard ke lokasi Anda</div>"
            "</div></div>",
            unsafe_allow_html=True,
        )
        st.link_button("WhatsApp Langsung", WA_LINK_KONSUL, use_container_width=True)

# =============================================================================
# 13. PRODUK & HARGA (original)
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
    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)

# =============================================================================
# 14. ADMIN ACCESS
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
        st.markdown("<div class='page-title'>The War Room — <span style='color:#00d4ff;'>Admin Control Center</span></div><div class='page-subtitle'>V-GUARD AI Ecosystem ©2026 — Founder Edition</div>", unsafe_allow_html=True)
        if st.button("Logout", key="logout_main"):
            st.session_state.admin_logged_in = False
            st.rerun()

        war_tabs = st.tabs(["Dashboard","🚨 Fraud Scanner","Aktivasi Klien","Database"])

        with war_tabs[0]:
            total_k = len(st.session_state.db_umum)
            aktif_k = sum(1 for k in st.session_state.db_umum if k.get("Status")=="Aktif")
            mrr     = hitung_proyeksi_omset(st.session_state.db_umum)
            m1,m2,m3,m4,m5 = st.columns(5)
            for col,(val,lbl) in zip([m1,m2,m3,m4,m5],[(str(total_k),"Total Klien"),(str(aktif_k),"Klien Aktif"),(str(total_k-aktif_k),"Pending"),(f"Rp {mrr:,.0f}","MRR"),("99.8%","Uptime")]):
                col.metric(lbl,val)
            dp_log = st.session_state.get("detected_package")
            if dp_log:
                bul,_ = HARGA_MAP.get(dp_log,("—","—"))
                st.markdown("<div class='match-banner'><div class='match-banner-title'>🎯 Paket Terdeteksi dari Sesi Chat CS</div><div class='match-banner-body'>Cocok: <b>" + dp_log + "</b> — " + bul + "/bln</div></div>", unsafe_allow_html=True)

        with war_tabs[1]:
            st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#e8f4ff;margin-bottom:4px;'>🚨 Fraud Intelligence Scanner</div><div style='font-size:13px;color:#7a9bbf;margin-bottom:16px;'>Hanya data Anomali, Void & Fraud — transaksi normal difilter (efisiensi API).</div>", unsafe_allow_html=True)
            df_trx = get_sample_transaksi()
            hasil  = scan_fraud_lokal(df_trx)
            fs1,fs2,fs3 = st.columns(3)
            fs1.metric("VOID / Cancel",  len(hasil["void"]),     delta="Tidak Wajar" if hasil["void"].shape[0] else "Aman")
            fs2.metric("Duplikat Kasir", len(hasil["fraud"]),    delta="Terdeteksi"  if hasil["fraud"].shape[0] else "Aman")
            fs3.metric("Selisih Saldo",  len(hasil["suspicious"]),delta="Anomali"    if hasil["suspicious"].shape[0] else "Aman")
            tv,tf,ts = st.tabs(["VOID","Duplikat","Selisih"])
            with tv:
                if not hasil["void"].empty:
                    st.error("Transaksi VOID mencurigakan!")
                    st.dataframe(hasil["void"][["ID_Transaksi","Cabang","Kasir","Jumlah","Waktu"]], use_container_width=True)
                    for cab in hasil["void"]["Cabang"].unique():
                        am = urllib.parse.quote(f"⚠️ ALERT V-GUARD: VOID mencurigakan di [{cab}]. Cek kasir segera!")
                        st.link_button(f"Alert Owner — {cab}", f"https://wa.me/{WA_NUMBER}?text={am}")
                else: st.success("Tidak ada VOID mencurigakan.")
            with tf:
                if not hasil["fraud"].empty:
                    st.error("Pola duplikat < 5 menit!")
                    st.dataframe(hasil["fraud"][["ID_Transaksi","Cabang","Kasir","Jumlah","selisih_menit"]], use_container_width=True)
                else: st.success("Tidak ada pola duplikat.")
            with ts:
                if not hasil["suspicious"].empty:
                    st.error("Selisih saldo ditemukan!")
                    st.dataframe(hasil["suspicious"][["ID_Transaksi","Cabang","Kasir","Saldo_Fisik","Saldo_Sistem","selisih_saldo"]], use_container_width=True)
                else: st.success("Saldo seimbang.")
            st.divider()
            st.markdown("<div style='font-size:12px;color:#7a9bbf;background:#101c2e;border:1px solid #1e3352;border-radius:8px;padding:10px 14px;margin-bottom:12px;'>💡 <b>Efisiensi API:</b> AI Deep Scan hanya mengirim data anomali ke cloud — hemat biaya API hingga 80%.</div>", unsafe_allow_html=True)
            if model_vguard:
                if st.button("🤖 Jalankan AI Deep Scan (Anomali Only)", type="primary"):
                    fraud_rows = pd.concat([hasil["void"],hasil["fraud"],hasil["suspicious"]]).drop_duplicates(subset=["ID_Transaksi"])
                    if fraud_rows.empty:
                        st.success("Tidak ada anomali untuk dianalisis.")
                    else:
                        with st.spinner("Sentinel AI menganalisis data anomali..."):
                            try:
                                prompt = "Analisis HANYA data anomali ini (transaksi normal sudah difilter):\n\n" + fraud_rows.to_string(index=False) + "\n\nBerikan: 1) Pola kecurangan, 2) Kasir berisiko, 3) Rekomendasi Owner. Ringkas dan taktis."
                                resp = model_vguard.generate_content(prompt)
                                res_text = resp.text.strip() if resp.text else "Tidak ada pola kritis tambahan."
                                st.session_state.api_cost_total += 150
                                st.markdown("### Hasil AI Deep Scan:")
                                st.markdown(res_text)
                            except Exception:
                                st.warning("Maaf, sistem sedang memproses data yang padat. Silakan coba lagi dalam beberapa menit.")
            else:
                st.info("Sambungkan GOOGLE_API_KEY di st.secrets untuk AI Deep Scan.")

        with war_tabs[2]:
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
                    ac1,ac2,ac3 = st.columns(3)
                    with ac1:
                        if is_aktif:
                            if st.button("Deactivate", key=f"deact_{i}", use_container_width=True):
                                st.session_state.db_umum[i]["Status"] = "Menunggu Pembayaran"; st.rerun()
                        else:
                            if st.button("Activate", key=f"act_{i}", use_container_width=True, type="primary"):
                                st.session_state.db_umum[i]["Status"] = "Aktif"; st.rerun()
                    with ac2:
                        inv_txt = urllib.parse.quote(f"INVOICE V-GUARD AI\n\nYth. {klien['Nama Klien']}\nPaket: {klien['Produk']}\nBulanan: {hb}\nSetup: {hs}\n\nTransfer: BCA 3450074658 a/n Erwin Sinaga\nKonfirmasi setelah transfer.\n— Tim V-Guard AI")
                        st.link_button("Kirim Invoice", f"https://wa.me/{wa_tgt}?text={inv_txt}", use_container_width=True)
                    with ac3:
                        dash = buat_dashboard_link(cid)
                        akses_txt = urllib.parse.quote(f"Halo {klien['Nama Klien']},\n\nDashboard V-Guard:\n{dash}\nClient ID: {cid}\n— Tim V-Guard AI")
                        st.link_button("Kirim Dashboard", f"https://wa.me/{wa_tgt}?text={akses_txt}", use_container_width=True)
                    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

        with war_tabs[3]:
            if st.session_state.db_umum:
                df_db = pd.DataFrame(st.session_state.db_umum)
                if "Client_ID" in df_db.columns:
                    df_db["Dashboard"] = df_db["Client_ID"].apply(buat_dashboard_link)
                    df_db["Referral"]  = df_db["Client_ID"].apply(buat_referral_link)
                st.dataframe(df_db, use_container_width=True, hide_index=True)
                st.download_button("⬇️ Download CSV", data=df_db.to_csv(index=False).encode("utf-8"), file_name=f"vguard_{datetime.date.today()}.csv", mime="text/csv")
            else:
                st.info("Database masih kosong.")

    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# 15. FOOTER
# =============================================================================
st.markdown(
    "<div style='background:#060b14;border-top:1px solid #1e3352;padding:28px 48px;"
    "display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;'>"
    "<div><span style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#00d4ff;'>V-Guard AI Intelligence</span>"
    "<span style='color:#7a9bbf;font-size:12px;margin-left:12px;'>V-GUARD AI Ecosystem ©2026</span></div>"
    "<div style='font-size:12px;color:#7a9bbf;'>Digitizing Trust · Eliminating Leakage · Protecting Every Rupiah</div></div>",
    unsafe_allow_html=True,
)
