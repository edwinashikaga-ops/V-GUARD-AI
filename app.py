# =============================================================================
# V-GUARD AI INTELLIGENCE — app.py  (Kodee-Style CS Chatbot Edition ©2026)
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
# 2. AI ENGINE — Google Gemini via st.secrets
# =============================================================================
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

_google_key  = None
model_vguard = None

try:
    _google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    _google_key = None

if _google_key and GENAI_AVAILABLE:
    try:
        genai.configure(api_key=_google_key)
        model_vguard = genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        model_vguard = None

# =============================================================================
# 3. PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="V-Guard AI — Concierge",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# 4. SESSION STATE DEFAULTS
# =============================================================================
_DEFAULTS = {
    "admin_logged_in": False,
    "cs_messages":     [],           # [{role, content}]
    "pending_quick":   None,         # quick-pill click buffer
    "db_umum":         [],
    "api_cost_total":  0.0,
    "detected_pkg":    None,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# =============================================================================
# 5. CONSTANTS
# =============================================================================
WA_NUMBER    = "6282122190885"
BASE_APP_URL = "https://v-guard-ai.streamlit.app"

WA_DEMO   = "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote("Halo Pak Erwin, saya ingin Book Demo V-Guard AI.")
WA_KONSUL = "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote("Halo Pak Erwin, saya ingin konsultasi mengenai V-Guard AI.")

PRODUCT_LINKS = {
    "V-LITE":    BASE_APP_URL + "/?menu=Produk+%26+Harga#v-lite",
    "V-PRO":     BASE_APP_URL + "/?menu=Produk+%26+Harga#v-pro",
    "V-ADVANCE": BASE_APP_URL + "/?menu=Produk+%26+Harga#v-advance",
    "V-ELITE":   BASE_APP_URL + "/?menu=Produk+%26+Harga#v-elite",
    "V-ULTRA":   BASE_APP_URL + "/?menu=Produk+%26+Harga#v-ultra",
}
ORDER_LINKS = {
    "V-LITE":    "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote("Halo Pak Erwin, saya ingin order Paket V-LITE."),
    "V-PRO":     "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote("Halo Pak Erwin, saya ingin order Paket V-PRO."),
    "V-ADVANCE": "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote("Halo Pak Erwin, saya ingin order Paket V-ADVANCE."),
    "V-ELITE":   "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote("Halo Pak Erwin, saya ingin order Paket V-ELITE."),
    "V-ULTRA":   "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote("Halo Pak Erwin, saya ingin konsultasi Paket V-ULTRA."),
}
HARGA_MAP = {
    "V-LITE":    ("Rp 150.000", "Rp 250.000"),
    "V-PRO":     ("Rp 450.000", "Rp 750.000"),
    "V-ADVANCE": ("Rp 1.200.000", "Rp 3.500.000"),
    "V-ELITE":   ("Mulai Rp 3.500.000", "Rp 10.000.000"),
    "V-ULTRA":   ("Custom", "Konsultasi"),
}
HARGA_NUM = {
    "V-LITE": 150_000, "V-PRO": 450_000, "V-ADVANCE": 1_200_000,
    "V-ELITE": 3_500_000, "V-ULTRA": 0,
}

PACKAGES_DATA = [
    {
        "name": "V-LITE", "badge": "Entry Level", "focus": "Fondasi keamanan untuk usaha 1 kasir",
        "price": "Rp 150.000", "period": "/bulan", "setup": "Setup: Rp 250.000",
        "plug_play": True, "popular": False, "ultra": False,
        "features": ["Deteksi VOID & Cancel", "Daily AI Summary via WhatsApp",
                     "Dashboard Web Real-Time", "Laporan Kebocoran Otomatis", "Support via WhatsApp"],
    },
    {
        "name": "V-PRO", "badge": "Pantau & Audit", "focus": "Monitoring CCTV AI + audit bank otomatis",
        "price": "Rp 450.000", "period": "/bulan", "setup": "Setup: Rp 750.000",
        "plug_play": True, "popular": True, "ultra": False,
        "features": ["Semua fitur V-LITE", "CCTV AI Visual Monitoring",
                     "Bank Statement Audit Otomatis", "Input Invoice via OCR",
                     "Laporan PDF Terjadwal", "Support Prioritas 24/7"],
    },
    {
        "name": "V-ADVANCE", "badge": "Multi-Cabang", "focus": "Pengawas aktif stok & multi-outlet",
        "price": "Rp 1.200.000", "period": "/bulan", "setup": "Setup: Rp 3.500.000",
        "plug_play": False, "popular": False, "ultra": False,
        "features": ["Semua fitur V-PRO", "WhatsApp Fraud Alarm Instan",
                     "H-7 Auto Collection Reminder", "Multi-Cabang Dashboard", "Smart Inventory OCR"],
    },
    {
        "name": "V-ELITE", "badge": "Fraud Detection", "focus": "Deteksi kasir & forensik AI penuh",
        "price": "Mulai Rp 3.500.000", "period": "/bulan", "setup": "Setup: Rp 10.000.000",
        "plug_play": False, "popular": False, "ultra": False,
        "features": ["Semua fitur V-ADVANCE", "Deep Learning Forensik Kasir",
                     "Dedicated Private Server", "Custom AI SOP per Divisi",
                     "On-site Implementation", "SLA 99.9% Uptime"],
    },
    {
        "name": "V-ULTRA", "badge": "Enterprise", "focus": "White-Label + 10 Elite AI Squad aktif",
        "price": "Custom Quote", "period": "Harga eksklusif", "setup": "Konsultasi strategis gratis",
        "plug_play": False, "popular": False, "ultra": True,
        "features": ["Seluruh ekosistem V-ELITE", "White-Label Platform",
                     "Executive BI Dashboard C-Level", "10 Elite AI Squad serentak",
                     "Dedicated AI Strategist", "V-Guard ERP Liaison Protocol"],
    },
]

# =============================================================================
# 6. PRODUCT MATCHING ENGINE
# =============================================================================
def detect_package(text: str) -> str | None:
    t = text.lower()
    scores: dict[str, int] = {}

    # V-LITE: small, 1 cashier
    lite_kw = ["warung", "lapak", "kios", "1 kasir", "satu kasir", "usaha kecil",
                "baru mulai", "baru buka", "coba dulu", "murah", "terjangkau", "entry"]
    scores["V-LITE"] = sum(2 for k in lite_kw if k in t)

    # V-PRO: CCTV / monitoring / pantau (user spec: CCTV/pantau → V-PRO)
    pro_kw = ["cctv", "kamera", "pantau", "monitoring", "monitor toko", "visual",
              "rekaman", "intip", "lihat toko", "pantau kasir", "cafe", "kafe",
              "restoran kecil", "toko kecil", "audit bank", "ocr", "plug play"]
    scores["V-PRO"] = sum(2 for k in pro_kw if k in t)

    # V-ADVANCE: multi-outlet, stock
    adv_kw = ["banyak cabang", "multi cabang", "beberapa cabang", "minimarket",
               "supermarket", "swalayan", "franchise", "waralaba", "stok barang",
               "banyak kasir", "multi outlet", "jaringan toko"]
    scores["V-ADVANCE"] = sum(3 for k in adv_kw if k in t)

    # V-ELITE: fraud detection / kasir curang (user spec: kasir/fraud → V-ELITE)
    elite_kw = ["kasir curang", "fraud kasir", "kecurangan kasir", "void mencurigakan",
                "deteksi fraud", "forensik", "server privat", "enterprise",
                "perusahaan besar", "korporasi", "ratusan kasir", "holding",
                "fraud detection", "cek fraud", "curang", "kecurangan"]
    scores["V-ELITE"] = sum(3 for k in elite_kw if k in t)

    # V-ULTRA: white label / custom
    ultra_kw = ["white label", "lisensi", "reseller platform", "c-level", "custom platform"]
    scores["V-ULTRA"] = sum(4 for k in ultra_kw if k in t)

    scores = {k: v for k, v in scores.items() if v > 0}
    return max(scores, key=scores.get) if scores else None


def build_cta(pkg: str) -> str:
    bul, setup = HARGA_MAP.get(pkg, ("Custom", "Konsultasi"))
    plink = PRODUCT_LINKS.get(pkg, BASE_APP_URL)
    olink = ORDER_LINKS.get(pkg, WA_KONSUL)
    install = "✅ **Plug & Play** — aktif mandiri, tanpa teknisi" if pkg in ("V-LITE", "V-PRO") \
              else "🔧 **Instalasi Profesional** — teknisi V-Guard ke lokasi Anda"
    return (
        f"\n\n---\n"
        f"**🎯 Rekomendasi: {pkg}**\n\n"
        f"💰 Biaya Bulanan: **{bul}**  |  🛠️ Setup: **{setup}**\n\n"
        f"{install}\n\n"
        f"👉 **[Lihat Detail {pkg} & Aktivasi Sekarang]({plink})**\n\n"
        f"📲 **[Order {pkg} via WhatsApp]({olink})**"
    )

# =============================================================================
# 7. CS SYSTEM PROMPT — Manusiawi & Consultative
# =============================================================================
CS_SYSTEM_PROMPT = """
Anda adalah **V-Guard Concierge** — konsultan penjualan AI pribadi untuk V-Guard AI Intelligence.
Anda bertugas membantu calon klien menemukan solusi terbaik untuk bisnis mereka.

═══════════════════════════════════════════════
KEPRIBADIAN & GAYA BAHASA — WAJIB DIIKUTI
═══════════════════════════════════════════════
• Gunakan sapaan "Bapak", "Ibu", atau "Kakak" — pilih yang paling sesuai konteks
• Semi-formal, hangat, seperti konsultan terpercaya yang peduli — bukan robot
• Empati dulu, baru solusi: "Saya paham kekhawatiran Bapak..."
• Selalu tutup dengan pertanyaan proaktif: "Bagaimana menurut Bapak, apakah ini sesuai kebutuhan?" atau "Boleh saya tahu berapa kasir yang Bapak kelola saat ini?"
• DILARANG KERAS: menyebut "AI maintenance", "API limit", "error", atau istilah teknis apapun. Jika ada kendala, katakan: "Maaf Pak/Bu, sistem sedang memproses data yang padat, mohon tunggu sebentar ya 🙏"
• Gunakan emoji secukupnya untuk terasa manusiawi: ✅ 💡 🛡️ 💰 📊

═══════════════════════════════════════════════
STRATEGI PENJUALAN — CONSULTATIVE SELLING
═══════════════════════════════════════════════
ATURAN EMAS: Jika user bertanya harga atau paket, JANGAN langsung kasih daftar harga.
Tanyakan dulu:
1. "Jenis usaha apa yang Bapak/Ibu kelola?"
2. "Berapa kasir atau cabang yang dimiliki?"
3. "Apa masalah utama yang ingin diselesaikan?"

Setelah mendapat informasi → jalankan product matching → rekomendasikan 1 paket spesifik.

═══════════════════════════════════════════════
PRODUCT MATCHING — GUNAKAN LOGIKA INI
═══════════════════════════════════════════════
🔵 PANTAU / CCTV / MONITORING → Rekomendasikan **V-PRO** (Rp 450.000/bln)
   Tekankan: CCTV AI overlay, audit bank otomatis, Plug & Play
   Link detail: https://v-guard-ai.streamlit.app/?menu=Produk+%26+Harga#v-pro
   Link order: https://wa.me/6282122190885?text=Halo+Pak+Erwin%2C+saya+ingin+order+Paket+V-PRO.

🔴 KASIR CURANG / FRAUD DETECTION / KECURANGAN → Rekomendasikan **V-ELITE** (Mulai Rp 3.500.000/bln)
   Tekankan: Deep Learning Forensik Kasir, Private Server, SLA 99.9%
   Link detail: https://v-guard-ai.streamlit.app/?menu=Produk+%26+Harga#v-elite
   Link order: https://wa.me/6282122190885?text=Halo+Pak+Erwin%2C+saya+ingin+order+Paket+V-ELITE.

🟢 USAHA KECIL / 1 KASIR / WARUNG → Rekomendasikan **V-LITE** (Rp 150.000/bln)
   Tekankan: harga terjangkau, Plug & Play, tanpa teknisi
   Link detail: https://v-guard-ai.streamlit.app/?menu=Produk+%26+Harga#v-lite

🟣 MULTI-CABANG / BANYAK STOK → Rekomendasikan **V-ADVANCE** (Rp 1.200.000/bln)
   Tekankan: multi-outlet dashboard, WA alarm, smart inventory
   Link detail: https://v-guard-ai.streamlit.app/?menu=Produk+%26+Harga#v-advance

👑 WHITE-LABEL / ENTERPRISE CUSTOM → Rekomendasikan **V-ULTRA**
   Arahkan ke konsultasi langsung.

═══════════════════════════════════════════════
FORMAT REKOMENDASI — WAJIB SERTAKAN LINK
═══════════════════════════════════════════════
Setiap kali merekomendasikan paket, WAJIB sertakan:
1. Nama paket dan harga
2. 2-3 keunggulan yang relevan dengan kebutuhan user
3. Link detail paket (gunakan markdown: [teks](url))
4. Link order WhatsApp
5. Pertanyaan follow-up untuk engagement

═══════════════════════════════════════════════
KALKULASI ROI (JIKA USER SEBUTKAN OMZET)
═══════════════════════════════════════════════
• Kebocoran rata-rata: 3–15% omzet (gunakan 5% sebagai default)
• V-Guard mencegah 88% kebocoran
• Penghematan = Omzet × 5% × 88%
• ROI = (Penghematan − Biaya Paket) / Biaya Paket × 100%

Contoh respons ROI yang baik:
"Kalau omzet Bapak Rp 100 juta/bln, estimasi kebocoran sekitar Rp 5 juta/bln.
Dengan V-PRO, bisa diselamatkan ±Rp 4,4 juta — artinya ROI-nya sekitar **878%** 🚀"

═══════════════════════════════════════════════
INSTRUKSI LAIN
═══════════════════════════════════════════════
• Bahasa Indonesia semi-formal, ramah, persuasif
• Selalu akhiri dengan pertanyaan atau call-to-action
• Jawaban fokus dan ringkas — tidak lebih dari 200 kata kecuali diminta detail
• Konsultasi langsung: https://wa.me/6282122190885
"""

# =============================================================================
# 8. AI RESPONSE FUNCTION
# =============================================================================
def get_ai_response(user_message: str) -> str:
    """Generate response from Gemini or smart fallback."""

    # Run local product matching
    pkg = detect_package(user_message)
    if pkg:
        st.session_state["detected_pkg"] = pkg

    def smart_fallback(msg: str, pkg_detected: str | None) -> str:
        """Human-like fallback — never shows technical errors."""
        m = msg.lower()

        # ROI calculation
        omzet_val = 0
        m_omzet = re.search(r'(\d[\d.,]*)\s*(juta|jt|miliar|m\b|rb|ribu)?', m)
        if m_omzet:
            try:
                raw = float(m_omzet.group(1).replace(",", ".").replace(".", ""))
                unit = (m_omzet.group(2) or "").strip().lower()
                if unit in ("juta", "jt"):    omzet_val = int(raw * 1_000_000)
                elif unit in ("miliar", "m"): omzet_val = int(raw * 1_000_000_000)
                elif unit in ("rb", "ribu"):  omzet_val = int(raw * 1_000)
                elif raw >= 1_000_000:        omzet_val = int(raw)
            except Exception:
                omzet_val = 0

        roi_block = ""
        if omzet_val >= 1_000_000:
            bocor = omzet_val * 0.05
            saved = bocor * 0.88
            biaya = HARGA_NUM.get(pkg_detected or "V-PRO", 450_000)
            net   = saved - biaya
            roi   = (net / biaya * 100) if biaya > 0 else 0
            roi_block = (
                f"\n\n💡 **Estimasi ROI Bisnis Bapak/Ibu:**\n"
                f"- Omzet: **Rp {omzet_val:,.0f}/bln**\n"
                f"- Estimasi kebocoran (5%): **Rp {bocor:,.0f}/bln**\n"
                f"- Diselamatkan V-Guard (88%): **Rp {saved:,.0f}/bln**\n"
                f"- ROI estimasi: **{roi:.0f}%** 🚀"
            )

        # Select base response by topic
        if any(k in m for k in ["harga", "berapa", "biaya", "tarif", "paket"]):
            base = (
                "Tentu, saya senang bantu menjelaskan harga, Bapak/Ibu! 😊\n\n"
                "Tapi sebelumnya, boleh saya tahu dulu — **jenis usaha apa** yang Bapak/Ibu kelola, "
                "dan kira-kira berapa **kasir atau cabang** yang dioperasikan?\n\n"
                "Dengan informasi itu, saya bisa langsung rekomendasikan paket yang paling tepat "
                "dan paling menguntungkan — bukan paket yang paling mahal 😄"
            )
        elif any(k in m for k in ["cctv", "kamera", "pantau", "monitor"]):
            base = (
                "Wah, kebutuhan monitoring yang Bapak/Ibu ceritakan sangat tepat ditangani "
                "V-Guard! 📹\n\n"
                "Untuk kebutuhan **CCTV AI & monitoring toko**, saya rekomendasikan **V-PRO** — "
                "solusi kami yang sudah terbukti membantu ratusan toko dan kafe.\n\n"
                "Keunggulan utamanya:\n"
                "✅ CCTV AI yang menampilkan teks transaksi langsung di rekaman\n"
                "✅ Audit rekening bank otomatis — tidak perlu cocokkan manual\n"
                "✅ **Plug & Play** — aktif dalam hitungan menit tanpa teknisi"
            )
            if pkg_detected == "V-PRO" or not pkg_detected:
                base += build_cta("V-PRO")
        elif any(k in m for k in ["fraud", "curang", "kasir curang", "kecurangan", "void"]):
            base = (
                "Saya sangat memahami kekhawatiran Bapak/Ibu soal kecurangan kasir 🛡️\n\n"
                "Ini masalah yang sering dialami bisnis yang sudah berkembang — "
                "dan V-Guard dirancang khusus untuk ini.\n\n"
                "Untuk **deteksi fraud kasir level lanjut**, saya rekomendasikan **V-ELITE** — "
                "dengan Deep Learning Forensik yang mampu mendeteksi pola kecurangan "
                "sebelum Bapak/Ibu menyadarinya.\n\n"
                "✅ Forensik AI — analisis pola void & duplikat transaksi\n"
                "✅ Private Server — data bisnis 100% aman di server sendiri\n"
                "✅ SLA Uptime 99.9% — monitoring tidak pernah berhenti"
            )
            if pkg_detected == "V-ELITE" or not pkg_detected:
                base += build_cta("V-ELITE")
        elif any(k in m for k in ["apa itu", "vguard", "v-guard", "tentang", "penjelasan", "jelaskan"]):
            base = (
                "Halo Bapak/Ibu! Senang bisa berkenalan 😊\n\n"
                "**V-Guard AI Intelligence** adalah sistem keamanan bisnis berbasis AI "
                "yang bekerja 24/7 mengawasi setiap rupiah di kasir, stok, dan rekening bank Anda.\n\n"
                "Bayangkan punya **auditor pribadi yang tidak pernah tidur** — "
                "dia langsung WhatsApp Bapak/Ibu kalau ada transaksi mencurigakan, "
                "void tidak wajar, atau selisih stok.\n\n"
                "🏆 **Hasil nyata dari klien kami:**\n"
                "- Pencegahan kebocoran hingga **88%**\n"
                "- Deteksi anomali dalam **< 5 detik**\n"
                "- ROI rata-rata klien: **400–900%** per bulan\n\n"
                "Boleh saya tahu, bisnis apa yang Bapak/Ibu kelola saat ini? "
                "Saya ingin pastikan solusi yang saya rekomendasikan benar-benar sesuai kebutuhan 🙏"
            )
        elif any(k in m for k in ["roi", "hemat", "bocor", "rugi", "omzet"]):
            base = (
                "Pertanyaan yang sangat cerdas, Bapak/Ibu! 💡\n\n"
                "Rata-rata bisnis kehilangan **3–15% omzet** setiap bulan tanpa mereka sadari — "
                "dari void kasir, selisih stok, hingga invoice yang tidak tertagih.\n\n"
                "V-Guard AI mencegah hingga **88% kebocoran** secara otomatis."
            )
            base += roi_block if roi_block else (
                "\n\nUntuk kalkulasi yang lebih presisi, boleh saya tahu "
                "**omzet bulanan rata-rata** bisnis Bapak/Ibu? 😊"
            )
        else:
            base = (
                "Halo! Saya **V-Guard Concierge**, siap membantu bisnis Bapak/Ibu 24/7 🛡️\n\n"
                "Saya bisa bantu Bapak/Ibu:\n"
                "📊 Hitung potensi kebocoran dan ROI bisnis\n"
                "🔍 Rekomendasikan paket yang paling tepat\n"
                "📹 Jelaskan cara kerja CCTV AI dan fraud detection\n"
                "💬 Atur konsultasi langsung dengan tim V-Guard\n\n"
                "Boleh ceritakan sedikit tentang bisnis Bapak/Ibu? "
                "Misalnya jenis usaha, jumlah kasir, atau masalah yang ingin diselesaikan 😊"
            )

        if roi_block and "roi_block" not in base:
            base += roi_block

        if pkg_detected and "build_cta" not in base and "Order" not in base and "Lihat Detail" not in base:
            base += build_cta(pkg_detected)

        if "wa.me" not in base:
            base += f"\n\n📞 Konsultasi langsung: [Chat dengan Tim V-Guard](https://wa.me/{WA_NUMBER})"

        return base

    # Try Gemini AI
    if model_vguard:
        try:
            history_api = [
                {"role": m["role"], "parts": [m["content"]]}
                for m in st.session_state.cs_messages[:-1]
                if m["role"] in ("user", "model")
            ]
            # Fix: Gemini uses "model" not "assistant"
            history_gemini = []
            for m in st.session_state.cs_messages[:-1]:
                role = "model" if m["role"] == "assistant" else "user"
                history_gemini.append({"role": role, "parts": [m["content"]]})

            chat_obj    = model_vguard.start_chat(history=history_gemini)
            full_prompt = CS_SYSTEM_PROMPT + f"\n\nPesan Klien: {user_message}"

            if pkg:
                bul, _ = HARGA_MAP.get(pkg, ("Custom", "—"))
                full_prompt += (
                    f"\n\n[SYSTEM: Paket cocok terdeteksi: {pkg} ({bul}/bln). "
                    f"Sertakan link detail: {PRODUCT_LINKS[pkg]} dan "
                    f"link order: {ORDER_LINKS[pkg]} dalam respons Anda. "
                    f"Akhiri dengan pertanyaan follow-up.]"
                )

            resp = chat_obj.send_message(full_prompt)
            answer = resp.text.strip() if resp.text else ""
            if answer:
                st.session_state.api_cost_total += 200
                return answer
        except Exception as e:
            # Humanized error — never show technical message
            err_str = str(e).lower()
            if "429" in err_str or "quota" in err_str:
                pass  # Fall through to smart_fallback silently
            # All errors: silently fall to fallback

    return smart_fallback(user_message, pkg)

# =============================================================================
# 9. HELPERS
# =============================================================================
def buat_client_id(nama: str, no_hp: str) -> str:
    raw = nama.strip().lower() + no_hp.strip()
    return "VG-" + hashlib.md5(raw.encode()).hexdigest()[:6].upper()

def get_sample_transaksi():
    now = datetime.datetime.now()
    return pd.DataFrame({
        "ID":      ["TRX-001","TRX-002","TRX-003","TRX-004","TRX-005","TRX-006","TRX-007","TRX-008"],
        "Cabang":  ["Sudirman","Sudirman","Central","Tangerang","Sudirman","Central","Tangerang","Sudirman"],
        "Kasir":   ["Budi","Budi","Sari","Andi","Budi","Sari","Andi","Dewi"],
        "Jumlah":  [150000,150000,500000,200000,150000,300000,50000,75000],
        "Waktu":   [
            now-datetime.timedelta(minutes=2), now-datetime.timedelta(minutes=3),
            now-datetime.timedelta(hours=1),   now-datetime.timedelta(hours=2),
            now-datetime.timedelta(minutes=4), now-datetime.timedelta(hours=3),
            now-datetime.timedelta(hours=5),   now-datetime.timedelta(minutes=10),
        ],
        "Status":       ["VOID","NORMAL","NORMAL","NORMAL","VOID","NORMAL","NORMAL","NORMAL"],
        "Saldo_Fisik":  [0,150000,480000,200000,0,300000,45000,75000],
        "Saldo_Sistem": [150000,150000,500000,200000,150000,300000,50000,75000],
    })

def scan_fraud(df: pd.DataFrame) -> dict:
    """Return only anomaly/fraud/void — never send normal data to cloud."""
    void_df = df[df["Status"] == "VOID"].copy()
    df_s = df.sort_values(["Kasir","Jumlah","Waktu"]).copy()
    df_s["gap_min"] = df_s.groupby(["Kasir","Jumlah"])["Waktu"].diff().dt.total_seconds().div(60)
    dup_df  = df_s[df_s["gap_min"] < 5].copy()
    df2 = df.copy()
    df2["selisih"] = df2["Saldo_Sistem"] - df2["Saldo_Fisik"]
    sus_df = df2[df2["selisih"] != 0].copy()
    return {"void": void_df, "duplikat": dup_df, "selisih": sus_df}

# =============================================================================
# 10. CSS — Clean Kodee-Style Dark Interface
# =============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg:        #070d18;
    --bg2:       #0c1525;
    --bg3:       #111f35;
    --card:      #0f1e33;
    --border:    #1a2e4a;
    --border2:   #243d5c;
    --accent:    #00c8f0;
    --accent2:   #0080e0;
    --accent3:   #6c2fff;
    --success:   #00d97e;
    --danger:    #ff3a5a;
    --warn:      #ffaa00;
    --gold:      #f0c040;
    --text:      #e0eeff;
    --muted:     #6888aa;
    --user-bg:   linear-gradient(135deg, #0080e0, #00c8f0);
    --ai-bg:     #111f35;
    --ai-border: #1a2e4a;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text) !important;
    background-color: var(--bg) !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070d18 0%, #0a1422 100%) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Main content ── */
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 4px 0 !important;
}

/* AI avatar area */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) > div:first-child {
    background: linear-gradient(135deg, var(--accent2), var(--accent)) !important;
    border-radius: 50% !important;
}

/* Chat message content bubbles — assistant */
[data-testid="stChatMessageContent"] {
    background: var(--ai-bg) !important;
    border: 1px solid var(--ai-border) !important;
    border-radius: 18px 18px 18px 4px !important;
    padding: 14px 18px !important;
    font-size: 14px !important;
    line-height: 1.75 !important;
    color: var(--text) !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3) !important;
}

/* User message bubble override */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #0080e0, #00c8f0) !important;
    border: none !important;
    border-radius: 18px 18px 4px 18px !important;
    color: #000 !important;
    font-weight: 500 !important;
}

/* Chat input */
[data-testid="stChatInput"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 16px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: var(--muted) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--card) !important;
    border: 1px solid var(--border2) !important;
    color: var(--accent) !important;
    border-radius: 24px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    height: 40px !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.2px !important;
}
.stButton > button:hover {
    background: rgba(0, 200, 240, 0.12) !important;
    border-color: var(--accent) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(0, 200, 240, 0.15) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent2), var(--accent)) !important;
    color: #000 !important;
    border: none !important;
    font-weight: 700 !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: var(--accent) !important;
    border: 1px solid var(--accent) !important;
}

/* Link buttons */
a[data-testid="stLinkButton"] button {
    background: linear-gradient(135deg, #128C7E, #25D366) !important;
    color: white !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
}

/* ── Inputs & Selects ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(0, 200, 240, 0.15) !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 12px !important; }
[data-testid="stMetricValue"] {
    color: var(--accent) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 26px !important;
    font-weight: 700 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg2) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--muted) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    border-radius: 8px 8px 0 0 !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: rgba(0, 200, 240, 0.06) !important;
}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

/* ── Progress ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--accent2), var(--accent)) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ── Custom Components ── */
.hero-chat {
    text-align: center;
    padding: 56px 24px 32px;
    background: radial-gradient(ellipse at 50% 0%, rgba(0,128,224,0.1) 0%, transparent 60%);
}
.hero-avatar {
    width: 72px; height: 72px;
    background: linear-gradient(135deg, #0080e0, #00c8f0);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 36px;
    margin: 0 auto 20px;
    box-shadow: 0 0 40px rgba(0,200,240,0.3);
}
.hero-greeting {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 30px !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    margin-bottom: 8px !important;
}
.hero-sub {
    font-size: 15px !important;
    color: var(--muted) !important;
    margin-bottom: 32px !important;
}

/* ── Package Cards ── */
.pkg-wrap {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px 18px;
    height: 100%;
    transition: all 0.3s ease;
    position: relative;
    display: flex;
    flex-direction: column;
}
.pkg-wrap:hover {
    border-color: var(--accent);
    box-shadow: 0 8px 32px rgba(0,200,240,0.1);
    transform: translateY(-4px);
}
.pkg-popular {
    border-color: var(--accent2) !important;
    background: linear-gradient(160deg, #0f1e33, #0a1628) !important;
}
.pkg-ultra {
    border-color: rgba(240,192,64,0.4) !important;
    background: linear-gradient(160deg, #141008, #1a1500, #0e0e0e) !important;
}
.badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px !important;
    font-weight: 600 !important;
    letter-spacing: 1.2px !important;
    text-transform: uppercase !important;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 10px;
}
.badge-lite  { background: rgba(0,200,240,0.12); color: #00c8f0 !important; border: 1px solid rgba(0,200,240,0.3); }
.badge-pro   { background: rgba(0,128,224,0.12); color: #6abcff !important; border: 1px solid rgba(0,128,224,0.3); }
.badge-adv   { background: rgba(108,47,255,0.12); color: #a88fff !important; border: 1px solid rgba(108,47,255,0.3); }
.badge-elite { background: rgba(0,217,126,0.12); color: #00d97e !important; border: 1px solid rgba(0,217,126,0.3); }
.badge-ultra { background: rgba(240,192,64,0.12); color: #f0c040 !important; border: 1px solid rgba(240,192,64,0.3); }
.hot-label {
    position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
    background: linear-gradient(135deg, #0080e0, #00c8f0);
    color: #000 !important; font-family: 'Rajdhani', sans-serif !important;
    font-size: 10px !important; font-weight: 700 !important;
    padding: 3px 14px; border-radius: 20px; letter-spacing: 1px; white-space: nowrap;
}
.ultra-label {
    position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
    background: linear-gradient(135deg, #b8860b, #f0c040);
    color: #000 !important; font-family: 'Rajdhani', sans-serif !important;
    font-size: 10px !important; font-weight: 700 !important;
    padding: 3px 14px; border-radius: 20px; letter-spacing: 1px; white-space: nowrap;
}

/* ── Sidebar Logo ── */
.sb-logo {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 20px !important;
    font-weight: 700 !important;
    color: var(--accent) !important;
    letter-spacing: 1px;
    text-align: center;
}
.sb-tag {
    font-size: 9px !important;
    color: var(--muted) !important;
    text-align: center;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.pulse {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--success);
    margin-right: 5px;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ── Admin War Card ── */
.war-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 11. SIDEBAR — Simplified (3 menus)
# =============================================================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 20px 0 16px; border-bottom: 1px solid #1a2e4a; margin-bottom: 16px; text-align: center;">
        <div style="font-size: 40px; margin-bottom: 8px;">🛡️</div>
        <div class="sb-logo">V-GUARD AI</div>
        <div class="sb-tag">Digital Business Guardian</div>
        <div style="margin-top: 10px; font-size: 11px; color: #6888aa; font-family: JetBrains Mono, monospace;">
            <span class="pulse"></span>System Online
        </div>
    </div>""", unsafe_allow_html=True)

    if os.path.exists("erwin.jpg"):
        st.image("erwin.jpg", use_container_width=True)
        st.markdown("""
        <div style="text-align: center; margin: 8px 0 14px;">
            <p style="color: #e0eeff; font-weight: 600; font-size: 13px; margin-bottom: 2px;">Erwin Sinaga</p>
            <p style="color: #6888aa; font-size: 11px;">Founder & CEO</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<p style='color:#6888aa;font-size:10px;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;'>Navigasi</p>",
                unsafe_allow_html=True)

    menu = st.radio("", ["🏠  Beranda", "📦  Produk & Harga", "🔒  Admin Access"], label_visibility="collapsed")
    menu = menu.split("  ")[1]  # strip emoji prefix

    # Detected package indicator
    dp = st.session_state.get("detected_pkg")
    if dp:
        bul, _ = HARGA_MAP.get(dp, ("Custom", "—"))
        st.markdown(f"""
        <div style="background: rgba(0,217,126,0.08); border: 1px solid rgba(0,217,126,0.25);
        border-radius: 10px; padding: 12px; margin-top: 16px;">
            <div style="font-size: 9px; color: #00d97e; font-family: JetBrains Mono, monospace;
            text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">🎯 Paket Terdeteksi</div>
            <div style="font-family: Rajdhani, sans-serif; font-size: 18px; font-weight: 700; color: #e0eeff;">{dp}</div>
            <div style="font-size: 11px; color: #6888aa;">{bul}/bulan</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.link_button("💬  Chat WhatsApp", WA_KONSUL, use_container_width=True)

# =============================================================================
# 12. BERANDA — Kodee-Style Chat-First Interface
# =============================================================================
if menu == "Beranda":

    # ── Pending quick pill handler ─────────────────────────────────────────
    new_input = None
    if st.session_state.get("pending_quick"):
        new_input = st.session_state.pending_quick
        st.session_state.pending_quick = None

    chat_col, _ = st.columns([1, 0.001])
    with chat_col:
        # ── Hero section (only when no messages) ──────────────────────────
        if not st.session_state.cs_messages and not new_input:
            st.markdown("""
            <div class="hero-chat">
                <div class="hero-avatar">🛡️</div>
                <div class="hero-greeting">Halo! 👋 Ada yang bisa saya bantu?</div>
                <div class="hero-sub">V-Guard Concierge siap konsultasi 24/7 — gratis &amp; tanpa kewajiban</div>
            </div>""", unsafe_allow_html=True)

            # Quick pills
            st.markdown("<div style='display:flex;justify-content:center;padding:0 48px;'>",
                        unsafe_allow_html=True)
            pc = st.columns(4)
            pills = [
                ("🛡️", "Apa itu V-Guard?"),
                ("📦", "Lihat Paket"),
                ("🔍", "Cek Fraud Kasir"),
                ("💰", "Hitung ROI"),
            ]
            for col, (icon, label) in zip(pc, pills):
                with col:
                    if st.button(f"{icon}  {label}", key=f"pill_{label}", use_container_width=True):
                        st.session_state.pending_quick = label
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # ── Compact pills during active chat ──────────────────────────────
        elif st.session_state.cs_messages:
            with st.expander("💡 Tanya Cepat", expanded=False):
                pc2 = st.columns(4)
                pills2 = ["Lihat Paket", "Hitung ROI", "Cara Instalasi", "Book Demo"]
                for col, label in zip(pc2, pills2):
                    with col:
                        if st.button(label, key=f"cpill_{label}", use_container_width=True):
                            st.session_state.pending_quick = label
                            st.rerun()

        # ── Render chat history from session state ─────────────────────────
        st.markdown("<div style='padding: 0 24px;'>", unsafe_allow_html=True)
        for msg in st.session_state.cs_messages:
            avatar = "🛡️" if msg["role"] == "assistant" else None
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Process new input (from pill or chat_input) ────────────────────
        if new_input:
            # Add user message to history
            st.session_state.cs_messages.append({"role": "user", "content": new_input})
            with st.chat_message("user"):
                st.markdown(new_input)

            # Generate and display AI response
            with st.chat_message("assistant", avatar="🛡️"):
                with st.spinner("V-Guard Concierge sedang mengetik..."):
                    time.sleep(1.1)
                    response = get_ai_response(new_input)
                st.markdown(response)

            st.session_state.cs_messages.append({"role": "assistant", "content": response})

        # ── Chat input (always visible) ────────────────────────────────────
        if prompt := st.chat_input(
            "Ceritakan kebutuhan bisnis Anda — kasir, cabang, atau masalah yang dihadapi...",
            key="main_chat",
        ):
            st.session_state.cs_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant", avatar="🛡️"):
                with st.spinner("V-Guard Concierge sedang mengetik..."):
                    time.sleep(1.1)
                    response = get_ai_response(prompt)
                st.markdown(response)

            st.session_state.cs_messages.append({"role": "assistant", "content": response})

        # ── Reset button ───────────────────────────────────────────────────
        if st.session_state.cs_messages:
            st.markdown("<div style='padding: 8px 24px 0; text-align: right;'>", unsafe_allow_html=True)
            if st.button("🔄  Mulai Percakapan Baru", key="reset_chat"):
                st.session_state.cs_messages = []
                st.session_state.detected_pkg = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# 13. PRODUK & HARGA
# =============================================================================
elif menu == "Produk & Harga":
    st.markdown("<div style='padding: 40px 48px 0;'>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-family:Rajdhani,sans-serif;font-size:34px;font-weight:700;color:#e0eeff;margin-bottom:4px;'>"
        "Pilih <span style='color:#00c8f0;'>Tingkat Perlindungan</span></div>"
        "<div style='font-size:14px;color:#6888aa;margin-bottom:32px;'>"
        "Dari usaha 1 kasir hingga korporasi multi-cabang — setiap tier dirancang tepat sasaran.</div>",
        unsafe_allow_html=True,
    )

    badge_map = {
        "V-LITE":    ("badge-lite",  ""),
        "V-PRO":     ("badge-pro",   ""),
        "V-ADVANCE": ("badge-adv",   ""),
        "V-ELITE":   ("badge-elite", ""),
        "V-ULTRA":   ("badge-ultra", ""),
    }

    cols = st.columns(5, gap="small")
    for col, pkg in zip(cols, PACKAGES_DATA):
        with col:
            badge_cls, _ = badge_map.get(pkg["name"], ("badge-lite", ""))
            card_cls = "pkg-ultra" if pkg["ultra"] else ("pkg-popular" if pkg["popular"] else "")

            feat_html = "".join(
                f"<div style='font-size:12px;color:#8aaccc;padding:3px 0;display:flex;gap:6px;'>"
                f"<span style='color:#00d97e;flex-shrink:0;'>✓</span>{f}</div>"
                for f in pkg["features"]
            )
            install_html = (
                "<span style='display:inline-block;background:rgba(0,217,126,0.1);color:#00d97e;"
                "border:1px solid rgba(0,217,126,0.3);border-radius:20px;font-size:9px;"
                "font-family:JetBrains Mono,monospace;padding:2px 8px;margin-top:6px;'>Plug &amp; Play ✅</span>"
                if pkg["plug_play"]
                else
                "<span style='display:inline-block;background:rgba(255,170,0,0.1);color:#ffaa00;"
                "border:1px solid rgba(255,170,0,0.3);border-radius:20px;font-size:9px;"
                "font-family:JetBrains Mono,monospace;padding:2px 8px;margin-top:6px;'>Teknisi Profesional 🔧</span>"
            )
            hot = "<div class='hot-label'>TERLARIS</div>" if pkg["popular"] else ""
            ultra = "<div class='ultra-label'>EKSKLUSIF</div>" if pkg["ultra"] else ""
            name_color = "#f0c040" if pkg["ultra"] else "#e0eeff"
            price_color = "#f0c040" if pkg["ultra"] else "#00c8f0"

            ord_link = ORDER_LINKS.get(pkg["name"], WA_KONSUL)

            st.markdown(
                f"<div style='padding-top:16px;height:100%;'>"
                f"<div class='pkg-wrap {card_cls}' style='height:100%;'>"
                f"{hot}{ultra}"
                f"<span class='badge {badge_cls}'>{pkg['badge']}</span>"
                f"<div style='font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;color:{name_color};'>{pkg['name']}</div>"
                f"<div style='font-size:11px;color:#6888aa;line-height:1.4;margin-bottom:14px;'>{pkg['focus']}</div>"
                f"<hr style='border:none;border-top:1px solid #1a2e4a;margin:12px 0;'>"
                f"<div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:{price_color};'>{pkg['price']}</div>"
                f"<div style='font-size:11px;color:#6888aa;margin-bottom:2px;'>{pkg['period']}</div>"
                f"<div style='font-size:11px;color:#3a5a7a;margin-bottom:12px;'>{pkg['setup']}</div>"
                f"{install_html}"
                f"<hr style='border:none;border-top:1px solid #1a2e4a;margin:12px 0;'>"
                f"<div style='flex-grow:1;'>{feat_html}</div>"
                f"<a href='{ord_link}' target='_blank' style='display:block;margin-top:16px;padding:10px;"
                f"text-align:center;background:linear-gradient(135deg,#0080e0,#00c8f0);color:#000;"
                f"font-family:Rajdhani,sans-serif;font-size:13px;font-weight:700;border-radius:8px;"
                f"text-decoration:none;letter-spacing:0.5px;'>Order Sekarang</a>"
                f"</div></div>",
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    st.markdown(
        "<div style='padding:0 48px;'>"
        "<div style='background:#0c1525;border:1px solid #1a2e4a;border-radius:10px;"
        "padding:14px 20px;font-size:12px;color:#6888aa;line-height:1.8;'>"
        "<b style='color:#00d97e;'>Plug &amp; Play (V-LITE &amp; V-PRO):</b> "
        "Setup mandiri, tanpa teknisi, aktif dalam hitungan menit. &nbsp;"
        "<b style='color:#ffaa00;'>Teknisi Profesional (V-ADVANCE ke atas):</b> "
        "Integrasi khusus oleh tim teknisi bersertifikat V-Guard di lokasi bisnis Anda."
        "</div></div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
    _, ctm, _ = st.columns([1.5, 1, 1.5])
    with ctm:
        st.link_button("Konsultasi Paket via WhatsApp", WA_KONSUL, use_container_width=True)
    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)

# =============================================================================
# 14. ADMIN ACCESS — Fraud-Only Intelligence Center
# =============================================================================
elif menu == "Admin Access":
    st.markdown("<div style='padding: 32px 48px;'>", unsafe_allow_html=True)

    if not st.session_state.admin_logged_in:
        _, lc, _ = st.columns([1, 1, 1])
        with lc:
            st.markdown("""
            <div style="background:#0f1e33;border:1px solid #1a2e4a;border-radius:16px;padding:36px;text-align:center;">
                <div style="font-size:48px;margin-bottom:16px;">🔒</div>
                <div style="font-family:Rajdhani,sans-serif;font-size:24px;font-weight:700;color:#e0eeff;margin-bottom:4px;">
                    Admin Access</div>
                <div style="font-size:13px;color:#6888aa;margin-bottom:24px;">
                    Restricted — Authorized Personnel Only</div>
            </div>""", unsafe_allow_html=True)
            pw = st.text_input("Access Code", type="password", key="admin_pw")
            if st.button("Masuk ke Intelligence Center", type="primary", use_container_width=True):
                if pw == "w1nbju8282":
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("Access Code salah. Hubungi Founder untuk reset.")
    else:
        st.markdown(
            "<div style='font-family:Rajdhani,sans-serif;font-size:30px;font-weight:700;color:#e0eeff;margin-bottom:4px;'>"
            "Intelligence Center — <span style='color:#00c8f0;'>War Room</span></div>"
            "<div style='font-size:13px;color:#6888aa;margin-bottom:24px;'>V-Guard AI ©2026 — Founder Edition</div>",
            unsafe_allow_html=True,
        )

        if st.button("Logout", key="logout"):
            st.session_state.admin_logged_in = False
            st.rerun()

        tabs = st.tabs(["📊 Overview", "🚨 Fraud Intelligence", "👥 Klien & Aktivasi", "📱 Database"])

        # ── Tab 1: Overview ───────────────────────────────────────────────
        with tabs[0]:
            total_k = len(st.session_state.db_umum)
            aktif_k = sum(1 for k in st.session_state.db_umum if k.get("Status") == "Aktif")
            mrr     = sum(HARGA_NUM.get(k.get("Produk","V-LITE"),0) for k in st.session_state.db_umum if k.get("Status")=="Aktif")

            m1, m2, m3, m4, m5 = st.columns(5)
            for col, (val, lbl) in zip([m1,m2,m3,m4,m5], [
                (str(total_k), "Total Klien"),
                (str(aktif_k), "Klien Aktif"),
                (str(total_k - aktif_k), "Pending"),
                (f"Rp {mrr:,.0f}", "MRR"),
                ("99.8%", "Uptime"),
            ]):
                col.metric(lbl, val)

            dp_log = st.session_state.get("detected_pkg")
            if dp_log:
                bul, _ = HARGA_MAP.get(dp_log, ("—","—"))
                st.markdown(
                    f"<div style='background:rgba(0,200,240,0.08);border:1px solid rgba(0,200,240,0.3);"
                    f"border-left:3px solid #00c8f0;border-radius:10px;padding:14px 18px;margin-top:16px;'>"
                    f"<div style='font-family:Rajdhani,sans-serif;font-size:14px;font-weight:700;color:#00c8f0;margin-bottom:4px;'>"
                    f"🎯 Sesi Aktif — Paket Terdeteksi dari Chat Concierge</div>"
                    f"<div style='font-size:13px;color:#8aaccc;'>Klien sesi ini cocok dengan: <b>{dp_log}</b> — {bul}/bln</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            st.divider()
            st.markdown(
                "<div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:#e0eeff;margin-bottom:12px;'>"
                "Distribusi Paket Klien Aktif</div>",
                unsafe_allow_html=True,
            )
            pkg_counts = {p: 0 for p in HARGA_NUM}
            for k in st.session_state.db_umum:
                if k.get("Status") == "Aktif":
                    pkg_counts[k.get("Produk","V-LITE")] = pkg_counts.get(k.get("Produk","V-LITE"),0) + 1

            pc_cols = st.columns(5)
            for col, (pkg_n, cnt) in zip(pc_cols, pkg_counts.items()):
                contrib = HARGA_NUM.get(pkg_n, 0) * cnt
                col.markdown(
                    f"<div style='background:#0f1e33;border:1px solid #1a2e4a;border-radius:10px;padding:14px;text-align:center;'>"
                    f"<div style='font-family:Rajdhani,sans-serif;font-size:15px;font-weight:700;color:#e0eeff;'>{pkg_n}</div>"
                    f"<div style='font-family:Rajdhani,sans-serif;font-size:26px;font-weight:700;color:#00c8f0;'>{cnt}</div>"
                    f"<div style='font-size:11px;color:#6888aa;'>Rp {contrib:,.0f}/bln</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # ── Tab 2: Fraud Intelligence — ANOMALY-ONLY ──────────────────────
        with tabs[1]:
            st.markdown(
                "<div style='font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;color:#e0eeff;margin-bottom:4px;'>"
                "🚨 Fraud Intelligence Scanner</div>"
                "<div style='font-size:13px;color:#6888aa;margin-bottom:20px;'>"
                "Hanya menampilkan data Anomali, Void &amp; Fraud — transaksi normal difilter untuk efisiensi API.</div>",
                unsafe_allow_html=True,
            )

            df_all   = get_sample_transaksi()
            hasil    = scan_fraud(df_all)  # Only fraud data extracted
            n_void   = len(hasil["void"])
            n_dup    = len(hasil["duplikat"])
            n_sus    = len(hasil["selisih"])
            n_total  = n_void + n_dup + n_sus

            f1, f2, f3, f4 = st.columns(4)
            f1.metric("Total Anomali",   str(n_total),  delta="Butuh Perhatian" if n_total else "Aman")
            f2.metric("VOID Mencurigakan", str(n_void),  delta="Kritis" if n_void else "Aman")
            f3.metric("Duplikat Kasir",  str(n_dup),    delta="Terdeteksi" if n_dup else "Aman")
            f4.metric("Selisih Saldo",   str(n_sus),    delta="Anomali" if n_sus else "Aman")

            if n_total:
                st.error(f"⚠️ {n_total} ANOMALI AKTIF — Tindakan segera diperlukan!")
            else:
                st.success("✅ Tidak ada anomali aktif saat ini.")

            tv, td, ts = st.tabs(["VOID / Cancel", "Duplikat Kasir", "Selisih Saldo"])

            with tv:
                if not hasil["void"].empty:
                    st.error("Transaksi VOID mencurigakan ditemukan!")
                    st.dataframe(
                        hasil["void"][["ID","Cabang","Kasir","Jumlah","Waktu","Status"]],
                        use_container_width=True, hide_index=True,
                    )
                    # WA Alert per cabang
                    for cab in hasil["void"]["Cabang"].unique():
                        alert_msg = urllib.parse.quote(
                            f"⚠️ ALERT V-GUARD: Transaksi VOID mencurigakan terdeteksi di [{cab}]. Segera cek kasir!"
                        )
                        st.link_button(
                            f"📲 Kirim Alert Owner — {cab}",
                            f"https://wa.me/{WA_NUMBER}?text={alert_msg}",
                        )
                else:
                    st.success("Tidak ada VOID mencurigakan.")

            with td:
                if not hasil["duplikat"].empty:
                    st.error("Pola transaksi duplikat dalam < 5 menit terdeteksi!")
                    st.dataframe(
                        hasil["duplikat"][["ID","Cabang","Kasir","Jumlah","gap_min"]].rename(
                            columns={"gap_min": "Jeda (Menit)"}
                        ),
                        use_container_width=True, hide_index=True,
                    )
                else:
                    st.success("Tidak ada pola duplikat.")

            with ts:
                if not hasil["selisih"].empty:
                    st.error("Selisih saldo fisik vs sistem ditemukan!")
                    st.dataframe(
                        hasil["selisih"][["ID","Cabang","Kasir","Saldo_Fisik","Saldo_Sistem","selisih"]].rename(
                            columns={"selisih": "Selisih (Rp)"}
                        ),
                        use_container_width=True, hide_index=True,
                    )
                else:
                    st.success("Saldo seimbang — tidak ada selisih.")

            # AI Deep Scan (only sends fraud data — not normal transactions)
            st.divider()
            st.markdown(
                "<div style='font-size:12px;color:#6888aa;background:#0c1525;border:1px solid #1a2e4a;"
                "border-radius:8px;padding:10px 14px;margin-bottom:12px;'>"
                "💡 <b>Efisiensi API:</b> AI Deep Scan hanya mengirim data anomali (bukan transaksi normal) "
                "ke cloud — menghemat biaya API hingga 80%.</div>",
                unsafe_allow_html=True,
            )

            if model_vguard:
                if st.button("🤖 Jalankan AI Deep Scan (Anomali Only)", type="primary"):
                    # Only send fraud data to AI — not normal transactions
                    fraud_only_df = pd.concat([
                        hasil["void"], hasil["duplikat"], hasil["selisih"]
                    ]).drop_duplicates(subset=["ID"])

                    if fraud_only_df.empty:
                        st.success("AI Scan: Tidak ada data anomali untuk dianalisis. Sistem bersih.")
                    else:
                        with st.spinner("Sentinel AI menganalisis data anomali..."):
                            try:
                                # Send ONLY fraud data to AI
                                prompt = (
                                    "Anda adalah Sentinel Fraud AI V-Guard. Analisis HANYA data anomali ini "
                                    "(bukan transaksi normal — sudah difilter):\n\n"
                                    + fraud_only_df.to_string(index=False)
                                    + "\n\nBerikan analisis: 1) Pola kecurangan yang terdeteksi, "
                                    "2) Kasir berisiko tinggi, 3) Rekomendasi tindakan Owner. "
                                    "Format: ringkas, taktis, langsung ke inti."
                                )
                                resp = model_vguard.generate_content(prompt)
                                result = resp.text.strip() if resp.text else "Analisis selesai — tidak ada pola kritis tambahan."
                                st.session_state.api_cost_total += 150  # Cheaper since less data
                                st.markdown("### 🤖 Hasil AI Deep Scan:")
                                st.markdown(result)
                            except Exception:
                                st.warning("Maaf, sistem AI sedang memproses data yang padat. Silakan coba lagi dalam beberapa menit.")
            else:
                st.info("Sambungkan GOOGLE_API_KEY di Streamlit Secrets untuk mengaktifkan AI Deep Scan.")

        # ── Tab 3: Klien & Aktivasi ───────────────────────────────────────
        with tabs[2]:
            st.markdown(
                "<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;"
                "color:#e0eeff;margin-bottom:16px;'>Panel Aktivasi Klien</div>",
                unsafe_allow_html=True,
            )

            if not st.session_state.db_umum:
                st.info("Belum ada klien terdaftar di sesi ini. Klien baru muncul setelah daftar di Portal Klien.")
            else:
                for i, klien in enumerate(st.session_state.db_umum):
                    if "Client_ID" not in klien:
                        st.session_state.db_umum[i]["Client_ID"] = buat_client_id(
                            klien["Nama Klien"], klien.get("WhatsApp", "")
                        )
                    cid         = st.session_state.db_umum[i]["Client_ID"]
                    is_aktif    = klien.get("Status") == "Aktif"
                    hb, hs      = HARGA_MAP.get(klien["Produk"], ("—","—"))
                    border_color = "#00d97e" if is_aktif else "#ffaa00"
                    status_color = "#00d97e" if is_aktif else "#ffaa00"
                    status_txt   = "Aktif" if is_aktif else "Menunggu Pembayaran"

                    st.markdown(
                        f"<div style='background:#0f1e33;border:1px solid #1a2e4a;border-left:3px solid {border_color};"
                        f"border-radius:12px;padding:18px;margin-bottom:10px;'>"
                        f"<div style='font-family:Rajdhani,sans-serif;font-size:17px;font-weight:700;color:#e0eeff;'>"
                        f"{klien['Nama Klien']} — {klien.get('Nama Usaha','-')}</div>"
                        f"<div style='font-family:JetBrains Mono,monospace;font-size:10px;color:#00c8f0;margin-bottom:6px;'>"
                        f"{cid} · {klien['Produk']}</div>"
                        f"<div style='font-size:12px;color:#6888aa;margin-bottom:8px;'>"
                        f"WA: {klien.get('WhatsApp','-')} · {hb}/bln · Setup: {hs}</div>"
                        f"<span style='background:rgba({('0,217,126' if is_aktif else '255,170,0')},0.12);"
                        f"color:{status_color};border:1px solid rgba({('0,217,126' if is_aktif else '255,170,0')},0.3);"
                        f"border-radius:20px;font-size:10px;padding:2px 10px;"
                        f"font-family:JetBrains Mono,monospace;'>{status_txt}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                    wa_tgt = klien.get("WhatsApp", WA_NUMBER)
                    if not wa_tgt.startswith("62"):
                        wa_tgt = "62" + wa_tgt.lstrip("0")

                    ac1, ac2, ac3 = st.columns(3)
                    with ac1:
                        btn_lbl = "Deactivate" if is_aktif else "Activate"
                        btn_type = "secondary" if is_aktif else "primary"
                        if st.button(btn_lbl, key=f"act_{i}", use_container_width=True, type=btn_type):
                            st.session_state.db_umum[i]["Status"] = "Menunggu Pembayaran" if is_aktif else "Aktif"
                            st.rerun()
                    with ac2:
                        inv_txt = urllib.parse.quote(
                            f"INVOICE V-GUARD AI\n\nYth. {klien['Nama Klien']}\n"
                            f"Paket: {klien['Produk']}\nBiaya Bulanan: {hb}\nSetup: {hs}\n\n"
                            f"Transfer: BCA 3450074658 a/n Erwin Sinaga\n\n"
                            f"Konfirmasi setelah transfer.\n— Tim V-Guard AI"
                        )
                        st.link_button("Kirim Invoice", f"https://wa.me/{wa_tgt}?text={inv_txt}", use_container_width=True)
                    with ac3:
                        dash_link = f"{BASE_APP_URL}/Portal_Klien?id={cid}"
                        akses_txt = urllib.parse.quote(
                            f"Halo {klien['Nama Klien']},\n\nAkses Dashboard V-Guard:\n{dash_link}\nClient ID: {cid}\n— Tim V-Guard AI"
                        )
                        st.link_button("Kirim Dashboard", f"https://wa.me/{wa_tgt}?text={akses_txt}", use_container_width=True)

                    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

        # ── Tab 4: Database ───────────────────────────────────────────────
        with tabs[3]:
            st.markdown(
                "<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;"
                "color:#e0eeff;margin-bottom:16px;'>Database Klien V-Guard</div>",
                unsafe_allow_html=True,
            )
            if st.session_state.db_umum:
                df_db = pd.DataFrame(st.session_state.db_umum)
                st.dataframe(df_db, use_container_width=True, hide_index=True)
                csv = df_db.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️  Download CSV",
                    data=csv,
                    file_name=f"vguard_clients_{datetime.date.today()}.csv",
                    mime="text/csv",
                )
            else:
                st.info("Database masih kosong di sesi ini.")

    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# 15. FOOTER
# =============================================================================
st.markdown(
    "<div style='background:#070d18;border-top:1px solid #1a2e4a;padding:24px 48px;"
    "display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;'>"
    "<div>"
    "<span style='font-family:Rajdhani,sans-serif;font-size:17px;font-weight:700;color:#00c8f0;'>"
    "V-Guard AI Intelligence</span>"
    "<span style='color:#6888aa;font-size:11px;margin-left:12px;'>©2026 All Rights Reserved</span>"
    "</div>"
    "<div style='font-size:11px;color:#6888aa;font-family:JetBrains Mono,monospace;'>"
    "Digitizing Trust · Eliminating Leakage · Protecting Every Rupiah"
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)
