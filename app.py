# =============================================================================
# V-GUARD AI INTELLIGENCE — APP.PY  (V-GUARD AI Ecosystem ©2026)
# =============================================================================

import streamlit as st
import os
import urllib.parse
import hashlib
import pandas as pd
import datetime
import re

# =============================================================================
# 1. MULTI-CHANNEL TRACKING  ← WAJIB DI PALING ATAS
# =============================================================================
_qp = st.query_params
if "tracking_ref" not in st.session_state:
    st.session_state["tracking_ref"]    = _qp.get("ref",    "")
if "tracking_source" not in st.session_state:
    st.session_state["tracking_source"] = _qp.get("source", "organic")

# =============================================================================
# 2. AI ENGINE — Menggunakan st.secrets["GOOGLE_API_KEY"]
# =============================================================================
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

_google_key   = None
ai_status     = "offline"
ai_status_msg = "🔴 AI Engine: Mode Offline"
model_vguard  = None

try:
    _google_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    _google_key = None

if _google_key and GENAI_AVAILABLE:
    try:
        genai.configure(api_key=_google_key)
        model_vguard  = genai.GenerativeModel("gemini-1.5-flash")
        ai_status     = "online"
        ai_status_msg = "🟢 AI Engine: Online"
    except Exception as _e:
        if "429" in str(_e) or "quota" in str(_e).lower():
            ai_status_msg = "🔴 AI Engine: Mode Offline (Kuota Habis)"
        else:
            ai_status_msg = "🔴 AI Engine: Mode Offline"

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
    "admin_logged_in":      False,
    "system_status":        "Healthy",
    "db_umum":              [],
    "api_cost_total":       0.0,
    "cs_chat_history":      [],
    "agent_kill_switch":    {},
    "detected_package":     None,      # ← hasil product matching
    "social_status": {
        "linkedin":  {"active": True,  "posts_today": 3, "last_post": "09:00", "leads": 12},
        "facebook":  {"active": True,  "posts_today": 2, "last_post": "10:30", "leads":  8},
        "tiktok":    {"active": True,  "posts_today": 1, "last_post": "12:00", "leads":  5},
        "instagram": {"active": True,  "posts_today": 2, "last_post": "11:15", "leads":  7},
        "youtube":   {"active": False, "posts_today": 0, "last_post": "—",     "leads":  2},
    },
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# =============================================================================
# 5. CONSTANTS & PRODUCT DATABASE
# =============================================================================
WA_NUMBER      = "6282122190885"
WA_LINK_DEMO   = "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote("Halo Pak Erwin, saya ingin Book Demo V-Guard AI.")
WA_LINK_KONSUL = "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote("Halo Pak Erwin, saya ingin konsultasi mengenai V-Guard AI.")

# ── Link Paket (gunakan anchor ke menu Produk & Harga sebagai placeholder) ──
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
    "V-LITE":    150_000,
    "V-PRO":     450_000,
    "V-ADVANCE": 1_200_000,
    "V-ELITE":   3_500_000,
    "V-ULTRA":   0,
}

SOURCE_MAP = {
    "whatsapp":  "WhatsApp",
    "facebook":  "Facebook",
    "linkedin":  "LinkedIn",
    "tiktok":    "TikTok",
    "instagram": "Instagram",
    "youtube":   "YouTube",
    "organic":   "Organik / Langsung",
}

# =============================================================================
# 6. PRODUCT MATCHING ENGINE
#    Mendeteksi kebutuhan klien dari pesan & mengembalikan paket yang cocok
# =============================================================================

# Keyword map: setiap paket punya bobot kata kunci
KEYWORD_PACKAGE_MAP = [
    # (paket, keywords, bobot)
    ("V-LITE", [
        "warung", "lapak", "satu kasir", "1 kasir", "kios", "sewa harian",
        "usaha kecil", "baru mulai", "mulai usaha", "baru buka",
        "coba dulu", "trial", "murah", "terjangkau", "entry",
    ], 1),

    ("V-PRO", [
        "pantau toko", "pantau kasir", "kamera", "cctv standar",
        "keamanan standar", "toko kecil", "restoran kecil", "cafe",
        "kafe kecil", "monitor transaksi", "laporan harian", "ocr invoice",
        "audit bank", "2 kasir", "3 kasir", "plug", "play", "mandiri",
    ], 2),

    ("V-ADVANCE", [
        "kasir", "stok barang", "stok", "penjualan", "banyak cabang",
        "multi cabang", "beberapa cabang", "minimarket", "supermarket",
        "swalayan", "toko besar", "restoran besar", "resto besar",
        "jaringan toko", "franchise kecil", "waralaba kecil",
        "cctv ai", "visual audit", "alarm fraud", "whatsapp alarm",
        "notifikasi fraud", "void mencurigakan", "deteksi fraud",
    ], 3),

    ("V-ELITE", [
        "korporasi", "perusahaan besar", "server privat", "server sendiri",
        "forensik", "ai forensik", "sla", "uptime", "dedicated server",
        "enterprise", "skala besar", "ratusan kasir", "puluhan cabang",
        "holding", "grup usaha", "conglomerate",
    ], 4),

    ("V-ULTRA", [
        "white label", "white-label", "rebranding", "custom platform",
        "beli platform", "lisensi platform", "c-level", "ceo dashboard",
        "10 agen", "ai agent", "full custom", "konsultasi strategis",
        "bisnis teknologi", "reseller platform",
    ], 5),
]

def detect_package_from_message(text: str) -> str | None:
    """
    Analisis teks klien → kembalikan nama paket terbaik atau None.
    Memenangkan paket dengan total skor tertinggi.
    """
    text_lower = text.lower()
    scores = {}
    for pkg, keywords, weight in KEYWORD_PACKAGE_MAP:
        hit = sum(1 for kw in keywords if kw in text_lower)
        if hit > 0:
            scores[pkg] = scores.get(pkg, 0) + hit * weight

    if not scores:
        return None
    return max(scores, key=scores.get)

def build_package_cta(pkg: str, context_msg: str = "") -> str:
    """
    Bangun pesan CTA persuasif lengkap dengan link paket.
    """
    harga_bul, harga_setup = HARGA_MAP.get(pkg, ("Custom", "Konsultasi"))
    prod_link  = PRODUCT_LINKS.get(pkg, BASE_APP_URL)
    order_link = ORDER_LINKS.get(pkg, WA_LINK_KONSUL)

    label_map = {
        "V-LITE":    "Fondasi Keamanan Digital (1 Kasir)",
        "V-PRO":     "Otomasi Penuh & Audit Bank",
        "V-ADVANCE": "Pengawas Aktif Multi-Cabang",
        "V-ELITE":   "Kedaulatan Data Korporasi",
        "V-ULTRA":   "White-Label & 10 Elite AI Squad",
    }
    label = label_map.get(pkg, "")

    emoji_map = {
        "V-LITE":    "🔵", "V-PRO": "⚡", "V-ADVANCE": "🟣",
        "V-ELITE":   "🟢", "V-ULTRA": "👑",
    }
    emoji = emoji_map.get(pkg, "🛡️")

    install_note = (
        "✅ **Plug & Play** — aktif mandiri dalam hitungan menit, tanpa teknisi."
        if pkg in ("V-LITE", "V-PRO")
        else "🔧 **Instalasi Profesional** — teknisi V-Guard datang ke lokasi bisnis Anda."
    )

    msg = (
        f"\n\n---\n"
        f"{emoji} **Rekomendasi Terbaik: {pkg}**\n"
        f"_{label}_\n\n"
        f"💰 **Biaya Bulanan:** {harga_bul}\n"
        f"🛠️ **Biaya Setup:** {harga_setup}\n"
        f"{install_note}\n\n"
        f"Berdasarkan kebutuhan Anda, saya sangat menyarankan **{pkg}**. "
        f"Anda bisa melihat detail fitur lengkap dan melakukan aktivasi langsung melalui:\n\n"
        f"👉 **[Lihat Detail {pkg} & Aktivasi Sekarang]({prod_link})**\n\n"
        f"Atau langsung chat untuk proses order:\n"
        f"📲 **[Order {pkg} via WhatsApp]({order_link})**\n\n"
        f"_Jangan biarkan kebocoran bisnis Anda berlanjut. Setiap hari tanpa V-Guard "
        f"adalah hari yang berisiko. Saya siap memandu Anda dari proses setup hingga sistem aktif!_ 🚀"
    )
    return msg

# =============================================================================
# 7. CS SYSTEM PROMPT — Dengan Product Matching Instructions
# =============================================================================
CS_SYSTEM_PROMPT = """
Anda adalah Sentinel CS — Konsultan AI pribadi resmi V-Guard AI Intelligence.
Gaya Anda: ahli keamanan digital yang persuasif, hangat, dan berorientasi solusi — seperti seorang asisten pribadi
yang sangat memahami bisnis klien dan peduli dengan kesuksesan mereka.

=== PRODUK, HARGA & LINK ===
| Paket     | Bulanan           | Setup          | Instalasi          | Link Detail                                      |
|-----------|-------------------|----------------|--------------------|--------------------------------------------------|
| V-LITE    | Rp 150.000/bln    | Rp 250.000     | PLUG & PLAY ✅     | https://v-guard-ai.streamlit.app/?menu=Produk+%26+Harga#v-lite    |
| V-PRO     | Rp 450.000/bln    | Rp 750.000     | PLUG & PLAY ✅     | https://v-guard-ai.streamlit.app/?menu=Produk+%26+Harga#v-pro     |
| V-ADVANCE | Rp 1.200.000/bln  | Rp 3.500.000   | Teknisi Profesional| https://v-guard-ai.streamlit.app/?menu=Produk+%26+Harga#v-advance |
| V-ELITE   | Mulai Rp 3,5jt/bln| Rp 10.000.000  | Teknisi Profesional| https://v-guard-ai.streamlit.app/?menu=Produk+%26+Harga#v-elite   |
| V-ULTRA   | Custom Quote      | Konsultasi     | Teknisi Profesional| https://v-guard-ai.streamlit.app/?menu=Produk+%26+Harga#v-ultra   |

=== LINK ORDER WHATSAPP ===
- V-LITE    : https://wa.me/6282122190885?text=Halo+Pak+Erwin%2C+saya+ingin+order+Paket+V-LITE.+Mohon+kirimkan+invoice.
- V-PRO     : https://wa.me/6282122190885?text=Halo+Pak+Erwin%2C+saya+ingin+order+Paket+V-PRO.+Mohon+kirimkan+invoice.
- V-ADVANCE : https://wa.me/6282122190885?text=Halo+Pak+Erwin%2C+saya+ingin+order+Paket+V-ADVANCE.+Mohon+kirimkan+invoice.
- V-ELITE   : https://wa.me/6282122190885?text=Halo+Pak+Erwin%2C+saya+ingin+order+Paket+V-ELITE.+Mohon+kirimkan+invoice.
- V-ULTRA   : https://wa.me/6282122190885?text=Halo+Pak+Erwin%2C+saya+ingin+konsultasi+Paket+V-ULTRA.

=== PRODUCT MATCHING — WAJIB IKUTI ATURAN INI ===

LEVEL 1 — KEBUTUHAN DASAR (→ V-LITE):
Kata kunci: warung, lapak, kios, satu kasir, 1 kasir, usaha kecil, baru mulai, baru buka, coba dulu, murah
→ Rekomendasikan V-LITE. Tekankan: harga terjangkau, Plug & Play, tidak butuh teknisi.

LEVEL 2 — KEBUTUHAN STANDAR (→ V-PRO):
Kata kunci: pantau toko, pantau kasir, kamera, keamanan standar, toko kecil, kafe, cafe, restoran kecil,
monitor transaksi, laporan harian, ocr invoice, audit bank, 2-3 kasir, plug and play, mandiri
→ Rekomendasikan V-PRO. Tekankan: Plug & Play, audit bank otomatis, OCR invoice.

LEVEL 3 — KEBUTUHAN KOMPLEKS (→ V-ADVANCE):
Kata kunci: kasir (lebih dari 3), stok barang, penjualan banyak item, banyak cabang, multi cabang,
minimarket, supermarket, franchise, cctv ai, alarm fraud, void mencurigakan, deteksi penipuan
→ Rekomendasikan V-ADVANCE. Tekankan: CCTV AI, WA Alarm, Multi-Cabang Dashboard.

LEVEL 4 — KORPORASI (→ V-ELITE):
Kata kunci: perusahaan besar, server privat, forensik, enterprise, ratusan kasir, puluhan cabang, holding, grup usaha
→ Rekomendasikan V-ELITE. Tekankan: server privat, SLA 99.9%, AI Forensik.

LEVEL 5 — WHITE-LABEL / CUSTOM (→ V-ULTRA):
Kata kunci: white label, lisensi platform, c-level, 10 ai agent, full custom, reseller platform
→ Rekomendasikan V-ULTRA. Arahkan ke konsultasi langsung.

=== INSTRUKSI PENGIRIMAN LINK OTOMATIS ===
Begitu Anda mengidentifikasi paket yang cocok, WAJIB tambahkan penutup seperti ini:

"Berdasarkan kebutuhan Anda, saya sangat menyarankan **[NAMA PAKET]**.
Anda bisa melihat detail fitur lengkap dan melakukan aktivasi langsung melalui link ini:
👉 **[Lihat Detail & Aktivasi [NAMA PAKET]]([LINK PAKET])**

Atau langsung proses order via WhatsApp:
📲 **[Order [NAMA PAKET] Sekarang]([LINK ORDER])**"

=== KALKULASI ROI / SHRINKAGE ===
- Rata-rata kebocoran bisnis: 3–15% omzet
- V-Guard mencegah hingga 88% kebocoran
- Penghematan/bulan = Omzet × % Kebocoran × 88%
- ROI = (Penghematan − Biaya Paket) / Biaya Paket × 100%
- Contoh: Omzet Rp 100 juta, bocor 5% → Rp 5 juta bocor → diselamatkan Rp 4,4 juta/bln
  Pakai V-PRO Rp 450rb → ROI = 878%

=== INSTALASI — BEDAKAN DENGAN SANGAT JELAS ===
- V-LITE & V-PRO     → PLUG & PLAY SAJA (mandiri, tanpa teknisi, tanpa ribet kabel)
- V-ADVANCE ke atas  → WAJIB integrasi khusus oleh teknisi profesional V-Guard ke lokasi

=== GAYA BAHASA ===
- Gunakan bahasa seperti konsultan pribadi yang ahli dan peduli bisnis klien
- Persuasif tapi tidak memaksa — bantu klien MELIHAT SENDIRI nilai solusinya
- Buat klien merasakan bahwa setiap hari tanpa V-Guard = hari berisiko
- Selalu empati dulu, baru solusi: "Saya mengerti kekhawatiran Anda..."
- Tutup setiap respons dengan call-to-action yang jelas dan link yang relevan

=== INSTRUKSI WAJIB ===
1. Tanya dulu (jika belum diketahui): jumlah kasir/cabang dan estimasi omzet bulanan.
2. Jalankan Product Matching berdasarkan kata kunci di atas.
3. Hitung ROI (shrinkage) jika user memberikan angka omzet.
4. Sertakan link paket & link order SETIAP KALI merekomendasikan paket.
5. Bahasa Indonesia, ramah, profesional, persuasif, ringkas tapi berisi.
6. Jangan berbohong tentang fitur — jujur dan transparan.
7. SELALU sertakan link konsultasi: https://wa.me/6282122190885
"""

# =============================================================================
# 8. HELPERS
# =============================================================================
def buat_client_id(nama: str, no_hp: str) -> str:
    raw = nama.strip().lower() + no_hp.strip()
    return "VG-" + hashlib.md5(raw.encode()).hexdigest()[:6].upper()

def buat_dashboard_link(client_id: str) -> str:
    return BASE_APP_URL + "/Portal_Klien?id=" + client_id

def buat_referral_link(client_id: str) -> str:
    return BASE_APP_URL + "/?ref=" + client_id

def buat_link_wa_alert(cabang: str, nomor: str = WA_NUMBER) -> str:
    msg = "⚠️ ALERT V-GUARD: Aktivitas mencurigakan terdeteksi di [" + cabang + "]. Segera cek sistem!"
    return "https://wa.me/" + nomor + "?text=" + urllib.parse.quote(msg)

def hitung_budget_guard(db_umum, api_cost_total):
    total = sum(
        int("".join(filter(str.isdigit, str(k.get("Nilai Kontrak", "0"))))) or 0
        for k in db_umum
    ) or 32_500_000
    batas  = total * 0.20
    persen = (api_cost_total / batas * 100) if batas > 0 else 0
    return total, batas, persen, persen >= 80

def get_source_counts():
    counts = {s: 0 for s in SOURCE_MAP}
    for k in st.session_state.db_umum:
        src = k.get("Source", "organic")
        if src in counts:
            counts[src] += 1
        else:
            counts["organic"] += 1
    return counts

def get_sample_transaksi():
    now = datetime.datetime.now()
    return pd.DataFrame({
        "ID_Transaksi": ["TRX-001","TRX-002","TRX-003","TRX-004","TRX-005","TRX-006","TRX-007","TRX-008"],
        "Cabang":       ["Outlet Sudirman","Outlet Sudirman","Resto Central","Cabang Tangerang",
                         "Outlet Sudirman","Resto Central","Cabang Tangerang","Outlet Sudirman"],
        "Kasir":        ["Budi","Budi","Sari","Andi","Budi","Sari","Andi","Dewi"],
        "Jumlah":       [150000,150000,500000,200000,150000,300000,50000,75000],
        "Waktu": [
            now - datetime.timedelta(minutes=2), now - datetime.timedelta(minutes=3),
            now - datetime.timedelta(hours=1),   now - datetime.timedelta(hours=2),
            now - datetime.timedelta(minutes=4), now - datetime.timedelta(hours=3),
            now - datetime.timedelta(hours=5),   now - datetime.timedelta(minutes=10),
        ],
        "Status":       ["VOID","NORMAL","NORMAL","NORMAL","VOID","NORMAL","NORMAL","NORMAL"],
        "Saldo_Fisik":  [0,150000,480000,200000,0,300000,45000,75000],
        "Saldo_Sistem": [150000,150000,500000,200000,150000,300000,50000,75000],
    })

def scan_fraud_lokal(df):
    void_df = df[df["Status"] == "VOID"].copy()
    df_s    = df.sort_values(["Kasir","Jumlah","Waktu"]).copy()
    df_s["selisih_menit"] = (
        df_s.groupby(["Kasir","Jumlah"])["Waktu"].diff().dt.total_seconds().div(60)
    )
    fraud_df = df_s[df_s["selisih_menit"] < 5].copy()
    df2      = df.copy()
    df2["selisih_saldo"] = df2["Saldo_Sistem"] - df2["Saldo_Fisik"]
    sus_df   = df2[df2["selisih_saldo"] != 0].copy()
    return {"void": void_df, "fraud": fraud_df, "suspicious": sus_df}

def hitung_proyeksi_omset(db_umum):
    total = 0
    for k in db_umum:
        if k.get("Status") == "Aktif":
            total += HARGA_NUMERIK.get(k.get("Produk", "V-LITE"), 0)
    return total

# =============================================================================
# 9. AI RESPONSE HELPER — Selalu Ada Jawaban + Product Matching
# =============================================================================
def get_ai_response(user_message: str) -> str:
    """
    Ambil respons dari Gemini AI + injeksi Product Matching.
    Jika AI offline → fallback cerdas dengan Product Matching tetap berjalan.
    """

    # ── Jalankan Product Matching di sisi Python ──────────────────────────
    detected = detect_package_from_message(user_message)
    if detected:
        st.session_state["detected_package"] = detected
    # ─────────────────────────────────────────────────────────────────────

    def build_full_fallback(msg: str, pkg_detected: str | None) -> str:
        """Bangun respons fallback lengkap dengan CTA paket jika terdeteksi."""
        msg_lower = msg.lower()

        # ── Hitung ROI jika ada angka omzet ──────────────────────────────
        omzet_match = re.search(r'(\d[\d.,]*)\s*(juta|jt|miliar|m|rb|ribu|ratus\s*juta)?', msg_lower)
        omzet_val   = 0
        if omzet_match:
            try:
                raw_num = float(omzet_match.group(1).replace(",", ".").replace(".", ""))
                unit    = (omzet_match.group(2) or "").strip().lower()
                if unit in ("juta", "jt"):
                    omzet_val = int(raw_num * 1_000_000)
                elif unit in ("miliar", "m"):
                    omzet_val = int(raw_num * 1_000_000_000)
                elif unit in ("rb", "ribu"):
                    omzet_val = int(raw_num * 1_000)
                elif unit in ("ratus juta",):
                    omzet_val = int(raw_num * 100_000_000)
                else:
                    if raw_num >= 1_000_000:
                        omzet_val = int(raw_num)
                    else:
                        omzet_val = 0
            except Exception:
                omzet_val = 0

        roi_block = ""
        if omzet_val >= 1_000_000:
            bocor_pct   = 5
            bocor_val   = omzet_val * bocor_pct / 100
            saved_val   = bocor_val * 0.88
            pkg_biaya   = HARGA_NUMERIK.get(pkg_detected or "V-PRO", 450_000)
            net_roi     = saved_val - pkg_biaya
            roi_pct     = (net_roi / pkg_biaya * 100) if pkg_biaya > 0 else 0
            roi_block   = (
                f"\n\n💡 **Estimasi Cepat ROI Bisnis Anda:**\n"
                f"- Omzet: **Rp {omzet_val:,.0f}/bln**\n"
                f"- Kebocoran rata-rata 5%: **Rp {bocor_val:,.0f}/bln**\n"
                f"- Diselamatkan V-Guard (88%): **Rp {saved_val:,.0f}/bln**\n"
                f"- ROI estimasi: **{roi_pct:.0f}%** 🚀\n"
                f"_Hitung lebih detail di menu **Kalkulator ROI**._"
            )

        # ── Pilih konten utama berdasarkan topik ─────────────────────────
        if any(k in msg_lower for k in ["roi", "bocor", "rugi", "hemat", "omzet", "juta", "untung"]):
            base = (
                "**Analisis Kebocoran Bisnis Anda** 🧮\n\n"
                "Rata-rata bisnis kehilangan **3–15% omzet** setiap bulan akibat kebocoran yang "
                "tidak terdeteksi — mulai dari void kasir, selisih stok, hingga piutang macet.\n\n"
                "V-Guard AI mencegah hingga **88% kebocoran** secara otomatis, 24 jam penuh.\n"
            )
        elif any(k in msg_lower for k in ["harga", "berapa", "biaya", "tarif", "paket", "lite", "pro", "advance", "elite", "ultra"]):
            base = (
                "**Daftar Paket V-Guard AI** 🛡️\n\n"
                "| Paket | Bulanan | Setup | Instalasi |\n"
                "|-------|---------|-------|-----------|\n"
                "| V-LITE    | Rp 150rb   | Rp 250rb   | Plug & Play ✅ |\n"
                "| V-PRO     | Rp 450rb   | Rp 750rb   | Plug & Play ✅ |\n"
                "| V-ADVANCE | Rp 1,2jt   | Rp 3,5jt   | Teknisi Profesional |\n"
                "| V-ELITE   | Mulai 3,5jt| Rp 10jt    | Teknisi Profesional |\n"
                "| V-ULTRA   | Custom     | Konsultasi | Teknisi Profesional |\n\n"
            )
        elif any(k in msg_lower for k in ["plug", "play", "pasang", "instal", "kabel", "teknis", "setup cara"]):
            base = (
                "**Panduan Instalasi V-Guard** ⚡\n\n"
                "**PLUG & PLAY** ✅ — Khusus V-LITE & V-PRO\n"
                "Aktif mandiri dalam hitungan menit. Sambungkan ke mesin kasir, scan QR setup, "
                "dan dashboard langsung berjalan — tanpa teknisi, tanpa ribet kabel.\n\n"
                "**INSTALASI PROFESIONAL** 🔧 — V-ADVANCE, V-ELITE, V-ULTRA\n"
                "Tim teknisi berpengalaman V-Guard datang ke lokasi bisnis Anda untuk integrasi "
                "CCTV AI, server privat, dan konfigurasi multi-cabang yang sempurna.\n\n"
            )
        elif any(k in msg_lower for k in ["fitur", "bisa apa", "fungsi", "kegunaan", "manfaat"]):
            base = (
                "**Ekosistem Fitur V-Guard AI** 🔗\n\n"
                "- 🚨 **Anomaly Detection** — Void, refund & diskon mencurigakan terdeteksi < 5 detik\n"
                "- 🏦 **Bank Audit Otomatis** — Cocokkan kasir vs mutasi rekening secara real-time\n"
                "- 📹 **CCTV AI Overlay** — Tampilkan teks transaksi di atas rekaman CCTV\n"
                "- 📦 **Smart Inventory (OCR)** — Update stok via drag-and-drop invoice\n"
                "- 📲 **WhatsApp Alarm** — Notifikasi instan ke Owner saat fraud terdeteksi\n"
                "- 📊 **Multi-Cabang Dashboard** — Pantau semua outlet dari 1 layar\n\n"
                "Setiap paket mengaktifkan kombinasi fitur yang disesuaikan skala bisnis Anda.\n"
            )
        else:
            base = (
                "Halo! Saya **Sentinel CS**, konsultan AI pribadi V-Guard AI Intelligence. 👋\n\n"
                "Saya di sini untuk membantu Anda **menutup kebocoran bisnis** secara permanen "
                "dengan teknologi AI yang bekerja 24/7 — tanpa lelah, tanpa kompromi.\n\n"
                "Ceritakan bisnis Anda:\n"
                "- Berapa **jumlah kasir atau cabang** yang Anda kelola?\n"
                "- Berapa **omzet bulanan** rata-rata Anda?\n\n"
                "Dengan informasi itu, saya akan langsung hitung potensi kebocoran Anda "
                "dan rekomendasikan solusi yang paling tepat dan paling menguntungkan. 💡\n"
            )

        result = base + roi_block

        # ── Injeksi CTA paket jika terdeteksi ────────────────────────────
        if pkg_detected:
            result += build_package_cta(pkg_detected)
        else:
            result += f"\n\n📞 **Konsultasi gratis langsung:** https://wa.me/{WA_NUMBER}"

        return result

    # ── Coba panggil Gemini AI ─────────────────────────────────────────────
    if model_vguard:
        try:
            hist_api = [
                {"role": m["role"], "parts": [m["content"]]}
                for m in st.session_state.cs_chat_history[:-1]
            ]
            chat_obj    = model_vguard.start_chat(history=hist_api)
            full_prompt = CS_SYSTEM_PROMPT + "\n\nPertanyaan Klien: " + user_message

            # Jika ada paket terdeteksi, beritahu AI untuk menyertakan link
            if detected:
                pkg_hint = (
                    f"\n\n[SYSTEM HINT: Berdasarkan analisis kata kunci, paket yang cocok adalah {detected}. "
                    f"Sertakan link detail: {PRODUCT_LINKS[detected]} "
                    f"dan link order: {ORDER_LINKS[detected]} dalam respons Anda.]"
                )
                full_prompt += pkg_hint

            resp_obj = chat_obj.send_message(full_prompt)
            answer   = resp_obj.text.strip() if resp_obj.text else ""
            if not answer:
                return build_full_fallback(user_message, detected)
            st.session_state.api_cost_total += 200
            return answer
        except Exception as _err:
            err_str = str(_err)
            note = (
                "\n\n_⚠️ AI Engine sedang sibuk — respons dari mode offline. "
                "Untuk konsultasi real-time: [Chat Sekarang](https://wa.me/" + WA_NUMBER + ")_"
                if "429" in err_str or "quota" in err_str.lower()
                else "\n\n_⚠️ AI sedang maintenance — menggunakan respons lokal._"
            )
            return build_full_fallback(user_message, detected) + note
    else:
        return build_full_fallback(user_message, detected)

# =============================================================================
# 10. CSS — Dark Cyber Security Theme
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
.stButton>button{background:linear-gradient(135deg,var(--accent2),var(--accent))!important;color:#000!important;font-family:'Rajdhani',sans-serif!important;font-weight:700!important;font-size:15px!important;border:none!important;border-radius:6px!important;height:46px!important;transition:all .2s ease!important;letter-spacing:.5px!important;}
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
::-webkit-scrollbar{width:6px;}::-webkit-scrollbar-track{background:var(--bg-primary);}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}::-webkit-scrollbar-thumb:hover{background:var(--accent);}
/* ── Hero ── */
.hero-section{background:linear-gradient(135deg,#060b14 0%,#0a1628 50%,#080f1e 100%);padding:60px 48px 48px;position:relative;overflow:hidden;border-bottom:1px solid var(--border);}
.hero-section::before{content:'';position:absolute;top:-50%;right:-10%;width:600px;height:600px;background:radial-gradient(circle,#00d4ff11 0%,transparent 70%);pointer-events:none;}
.hero-badge{display:inline-block;background:linear-gradient(135deg,#00d4ff22,#0091ff22);border:1px solid var(--accent);color:var(--accent)!important;font-family:'JetBrains Mono',monospace!important;font-size:11px!important;padding:4px 14px;border-radius:20px;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:20px;}
.hero-title{font-family:'Rajdhani',sans-serif!important;font-size:58px!important;font-weight:700!important;line-height:1.1!important;color:var(--text-primary)!important;margin-bottom:8px!important;}
.hero-title .accent{color:var(--accent)!important;}
.hero-subtitle{font-size:19px!important;color:var(--text-muted)!important;line-height:1.7!important;max-width:520px;margin-bottom:36px!important;}
/* ── Cards ── */
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
/* ── Section ── */
.section-header{font-family:'Rajdhani',sans-serif!important;font-size:36px!important;font-weight:700!important;color:var(--text-primary)!important;text-align:center;margin-bottom:8px!important;}
.section-subheader{font-size:16px!important;color:var(--text-muted)!important;text-align:center;margin-bottom:36px!important;}
.section-accent{color:var(--accent)!important;}
.section-wrapper{padding:56px 48px;border-bottom:1px solid var(--border);}
.section-wrapper-alt{padding:56px 48px;background:var(--bg-secondary);border-bottom:1px solid var(--border);}
.page-title{font-family:'Rajdhani',sans-serif!important;font-size:34px!important;font-weight:700!important;color:var(--text-primary)!important;margin-bottom:4px!important;}
.page-subtitle{font-size:15px!important;color:var(--text-muted)!important;margin-bottom:32px!important;}
/* ── Demo ── */
.demo-mockup{background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:16px;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--text-muted);line-height:1.8;}
.demo-dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:4px;}
.demo-red{background:#ff5f57;}.demo-yellow{background:#febc2e;}.demo-green{background:#28c840;}
/* ── Sidebar ── */
.sidebar-logo{font-family:'Rajdhani',sans-serif!important;font-size:22px!important;font-weight:700!important;color:var(--accent)!important;letter-spacing:1px;text-align:center;}
.sidebar-tagline{font-size:10px!important;color:var(--text-muted)!important;text-align:center;letter-spacing:2px;text-transform:uppercase;}
.status-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--success);margin-right:6px;animation:pulse 2s infinite;}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:.4;}}
/* ── Package cards ── */
.pkg-card{background:#101c2e;border:1px solid #1e3352;border-radius:14px;padding:22px 16px 20px;display:flex;flex-direction:column;height:100%;transition:all .3s ease;position:relative;}
.pkg-card:hover{border-color:#00d4ff;box-shadow:0 0 28px #00d4ff11;transform:translateY(-4px);}
.pkg-card-ultra{background:linear-gradient(160deg,#12100a 0%,#1a1500 60%,#0e0e0e 100%);border:1px solid #ffd70055;border-radius:14px;padding:22px 16px 20px;display:flex;flex-direction:column;height:100%;transition:all .3s ease;position:relative;}
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
/* ── Package Match Banner ── */
.match-banner{background:linear-gradient(135deg,#00d4ff18,#0091ff11);border:1px solid #00d4ff55;border-left:3px solid #00d4ff;border-radius:10px;padding:16px 20px;margin-bottom:16px;}
.match-banner-title{font-family:'Rajdhani',sans-serif!important;font-size:15px!important;font-weight:700!important;color:#00d4ff!important;margin-bottom:4px;}
.match-banner-body{font-size:13px!important;color:#9ab8d4!important;}
/* ── CS Chat ── */
.cs-section{background:linear-gradient(135deg,#060b14,#0a1628);border-top:1px solid #1e3352;padding:56px 48px;}
.chat-bubble-user{background:linear-gradient(135deg,#0091ff,#00d4ff);color:#000!important;padding:12px 16px;border-radius:14px 14px 4px 14px;font-size:14px;margin-bottom:8px;max-width:80%;margin-left:auto;}
.chat-bubble-ai{background:var(--bg-card);border:1px solid var(--border);color:var(--text-primary)!important;padding:12px 16px;border-radius:14px 14px 14px 4px;font-size:14px;margin-bottom:8px;max-width:85%;}
.chat-label{font-size:11px!important;color:var(--text-muted)!important;margin-bottom:3px;font-family:'JetBrains Mono',monospace!important;}
/* ── Affiliate ── */
.ref-link-box{background:#060b14;border:1px solid #1e3352;border-radius:8px;padding:12px 16px;font-family:'JetBrains Mono',monospace;font-size:12px;color:#00d4ff;word-break:break-all;}
/* ── Admin / War Room ── */
.war-card{background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:18px;margin-bottom:12px;}
.war-title{font-family:'Rajdhani',sans-serif!important;font-size:16px!important;font-weight:700!important;color:var(--accent)!important;margin-bottom:4px;}
.social-badge-on{display:inline-block;background:#00e67618;color:#00e676!important;border:1px solid #00e67644;border-radius:20px;font-size:10px!important;padding:2px 10px;font-family:'JetBrains Mono',monospace!important;}
.social-badge-off{display:inline-block;background:#ff3b5c18;color:#ff3b5c!important;border:1px solid #ff3b5c44;border-radius:20px;font-size:10px!important;padding:2px 10px;font-family:'JetBrains Mono',monospace!important;}
.client-card{background:#101c2e;border:1px solid #1e3352;border-radius:12px;padding:20px;margin-bottom:14px;}
.client-card-aktif{background:#101c2e;border:1px solid #1e3352;border-left:3px solid #00e676;border-radius:12px;padding:20px;margin-bottom:14px;}
.client-card-pending{background:#101c2e;border:1px solid #1e3352;border-left:3px solid #ffab00;border-radius:12px;padding:20px;margin-bottom:14px;}
.client-name{font-family:'Rajdhani',sans-serif!important;font-size:17px!important;font-weight:700!important;color:#e8f4ff!important;}
.client-id{font-family:'JetBrains Mono',monospace!important;font-size:11px!important;color:#00d4ff!important;margin-bottom:6px;}
.client-meta{font-size:12px!important;color:#7a9bbf!important;margin-bottom:4px;}
.client-badge-aktif{display:inline-block;background:#00e67618;color:#00e676!important;border:1px solid #00e67644;border-radius:20px;font-size:10px!important;padding:2px 10px;font-family:'JetBrains Mono',monospace!important;}
.client-badge-pending{display:inline-block;background:#ffab0018;color:#ffab00!important;border:1px solid #ffab0044;border-radius:20px;font-size:10px!important;padding:2px 10px;font-family:'JetBrains Mono',monospace!important;}
.client-link{font-family:'JetBrains Mono',monospace!important;font-size:10px!important;color:#4a6a8a!important;word-break:break-all;margin-top:6px;padding:6px 10px;background:#060b14;border-radius:4px;border:1px solid #1e3352;}
.login-card{background:var(--bg-card);border:1px solid var(--border);border-radius:14px;padding:36px;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 11. SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("""
    <div style='padding:20px 0 16px;border-bottom:1px solid #1e3352;margin-bottom:16px;'>
        <div class='sidebar-logo'>V-GUARD AI</div>
        <div class='sidebar-tagline'>Digital Business Auditor</div>
    </div>""", unsafe_allow_html=True)

    if os.path.exists("erwin.jpg"):
        st.image("erwin.jpg", use_container_width=True)
        st.markdown("""
        <div style='text-align:center;margin:10px 0 16px;'>
            <p style='color:#e8f4ff;font-weight:bold;margin-bottom:2px;font-size:14px;'>Erwin Sinaga</p>
            <p style='color:#7a9bbf;font-size:12px;'>Founder & CEO</p>
        </div>""", unsafe_allow_html=True)

    _src = st.session_state.get("tracking_source", "organic")
    _ref = st.session_state.get("tracking_ref", "")
    if _ref:
        st.markdown(
            "<div style='background:#00d4ff11;border:1px solid #00d4ff33;border-radius:6px;"
            "padding:6px 10px;margin-bottom:10px;font-size:10px;color:#00d4ff;"
            "font-family:JetBrains Mono,monospace;'>"
            "Ref: " + _ref + " · " + SOURCE_MAP.get(_src, _src) + "</div>",
            unsafe_allow_html=True,
        )

    # ── Product Match Indicator di Sidebar ──────────────────────────────
    dp = st.session_state.get("detected_package")
    if dp:
        hb, _ = HARGA_MAP.get(dp, ("Custom", "—"))
        st.markdown(
            "<div style='background:#00e67611;border:1px solid #00e67633;border-radius:8px;"
            "padding:10px 12px;margin-bottom:12px;'>"
            "<div style='font-size:10px;color:#00e676;font-family:JetBrains Mono,monospace;"
            "text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;'>🎯 Paket Terdeteksi</div>"
            "<div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:#e8f4ff;'>"
            + dp + "</div>"
            "<div style='font-size:11px;color:#7a9bbf;'>" + hb + "/bulan</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    # ────────────────────────────────────────────────────────────────────

    st.markdown(
        "<p style='color:#7a9bbf;font-size:11px;text-transform:uppercase;"
        "letter-spacing:1.5px;margin-bottom:8px;'>Menu Navigasi</p>",
        unsafe_allow_html=True,
    )

    MENU_ITEMS = [
        "Beranda",
        "Produk & Harga",
        "Kalkulator ROI",
        "Portal Klien",
        "Admin Access",
    ]
    menu = st.radio("", MENU_ITEMS, label_visibility="collapsed")

# =============================================================================
# 12. BERANDA
# =============================================================================
if menu == "Beranda":

    st.markdown("""
    <div class="hero-section">
        <div class="hero-badge">AI-Powered Fraud Detection &nbsp;·&nbsp; 24/7 Autonomous</div>
        <div class="hero-title">Hentikan <span class="accent">Kebocoran</span><br>Bisnis Anda. Sekarang.</div>
        <div class="hero-subtitle">V-Guard AI mengawasi setiap Rupiah di kasir, stok, dan rekening bank Anda
        secara otomatis — mendeteksi kecurangan sebelum Anda menyadarinya.</div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1.2, 1.2, 3])
    with c1:
        st.link_button("Book Demo Gratis", WA_LINK_DEMO, use_container_width=True)
    with c2:
        st.link_button("Chat Konsultasi", WA_LINK_KONSUL, use_container_width=True)

    st.markdown("<div style='height:48px;'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-wrapper'>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    for col, (n, l) in zip([s1, s2, s3, s4], [
        ("88%",    "Kebocoran Berhasil Dicegah"),
        ("24/7",   "Monitoring Otomatis"),
        ("< 5 Dtk","Deteksi Real-Time"),
        ("5 Tier", "Solusi Semua Skala"),
    ]):
        with col:
            st.markdown(
                "<div class='stat-card'><div class='stat-number'>" + n + "</div>"
                "<div class='stat-label'>" + l + "</div></div>",
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

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
    pc1, pc2, pc3 = st.columns(3)
    for col, group in zip([pc1, pc2, pc3], [PAINS[:2], PAINS[2:4], PAINS[4:]]):
        with col:
            for icon, title, desc in group:
                st.markdown(
                    "<div class='pain-card'><div style='font-size:22px;margin-bottom:6px;'>" + icon + "</div>"
                    "<div class='pain-title'>" + title + "</div>"
                    "<div class='pain-desc'>" + desc + "</div></div>",
                    unsafe_allow_html=True,
                )

    st.markdown("""
    <div class='section-wrapper'>
        <div class='section-header'>Ekosistem <span class='section-accent'>V-Guard</span></div>
        <div class='section-subheader'>Satu platform, semua celah kecurangan tertutup secara otomatis</div>
    </div>""", unsafe_allow_html=True)

    FEATS = [
        ("🔗","Auto Data Integration","Tarik data langsung dari mesin kasir via IP/API. Tanpa input manual CSV."),
        ("🚨","Anomaly Detection Engine","Tandai VOID, refund, dan diskon mencurigakan secara otomatis dalam hitungan detik."),
        ("🏦","Bank Statement Audit","Cocokkan laporan kasir dengan mutasi bank secara otomatis."),
        ("📹","Visual Cashier Audit (CCTV)","Tampilkan teks transaksi tepat di atas rekaman CCTV real-time."),
        ("📦","Smart Inventory (OCR)","Update stok otomatis via drag-and-drop invoice supplier."),
        ("📲","WhatsApp Fraud Alarm","Notifikasi instan ke ponsel Owner saat anomali terdeteksi."),
    ]
    fc = st.columns(3)
    for i, (icon, title, desc) in enumerate(FEATS):
        with fc[i % 3]:
            st.markdown(
                "<div class='feature-card'><div style='font-size:28px;margin-bottom:12px;'>" + icon + "</div>"
                "<div class='feature-title'>" + title + "</div>"
                "<div class='feature-desc'>" + desc + "</div></div>",
                unsafe_allow_html=True,
            )
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='section-wrapper-alt'>
        <div class='section-header'>Lihat <span class='section-accent'>Dashboard</span> V-Guard</div>
        <div class='section-subheader'>Real-time monitoring langsung dari browser Anda</div>
    </div>""", unsafe_allow_html=True)

    dm1, dm2 = st.columns([1.6, 1])
    with dm1:
        st.markdown("""
        <div class='demo-mockup'>
            <div style='margin-bottom:12px;'>
                <span class='demo-dot demo-red'></span>
                <span class='demo-dot demo-yellow'></span>
                <span class='demo-dot demo-green'></span>
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
        for icon, val, lbl in [
            ("🔍","3 Anomali","Terdeteksi malam ini"),
            ("📲","1 Alert","Dikirim ke Owner"),
            ("📊","100%","Audit Coverage"),
            ("⚡","0.2ms","Response Time"),
        ]:
            st.markdown(
                "<div style='background:#101c2e;border:1px solid #1e3352;border-radius:8px;"
                "padding:14px 18px;margin-bottom:10px;display:flex;align-items:center;gap:16px;'>"
                "<span style='font-size:22px;'>" + icon + "</span>"
                "<div><div style='font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;color:#00d4ff;'>" + val + "</div>"
                "<div style='font-size:12px;color:#7a9bbf;'>" + lbl + "</div></div></div>",
                unsafe_allow_html=True,
            )

    _, cc, _ = st.columns([1,1,1])
    with cc:
        st.link_button("Book Demo Langsung", WA_LINK_DEMO, use_container_width=True)

    st.markdown("""
    <div class='section-wrapper'>
        <div class='section-header'>Kata Mereka yang <span class='section-accent'>Sudah Merasakan</span></div>
        <div class='section-subheader'>Bisnis nyata, penghematan nyata</div>
    </div>""", unsafe_allow_html=True)

    t1, t2, t3 = st.columns(3)
    TESTI = [
        ("Sebelum pakai V-Guard, kasir saya melakukan void hampir setiap malam. Sekarang semuanya ter-record dan saya bisa tidur tenang.",
         "Bpk. Timotius M.","Owner Kafe & Resto, Jakarta Selatan","Hemat ±Rp 8 Juta/bulan"),
        ("Stok saya sering selisih tapi saya kira itu wajar. Ternyata ada kebocoran dari supplier. V-Guard langsung deteksi hari pertama.",
         "Ibu Riana S.","Pemilik Minimarket, 3 Cabang Tangerang","Selisih stok turun 94%"),
        ("Fitur H-7 reminder invoice sangat membantu cash flow. Tidak ada lagi piutang yang lupa ditagih lebih dari seminggu.",
         "Bpk. Doni A.","Distributor FMCG, Bekasi","Collection rate +31%"),
    ]
    for col, (text, author, role, result) in zip([t1, t2, t3], TESTI):
        with col:
            st.markdown(
                "<div class='testimonial-card'><div class='stars'>★★★★★</div>"
                "<div class='testimonial-text'>\"" + text + "\"</div>"
                "<div class='testimonial-author'>" + author + "</div>"
                "<div class='testimonial-role'>" + role + "</div>"
                "<div style='margin-top:12px;padding:8px 12px;background:#00d4ff11;border-radius:6px;"
                "font-size:12px;color:#00d4ff;font-family:JetBrains Mono,monospace;'>✓ " + result + "</div></div>",
                unsafe_allow_html=True,
            )

    st.markdown("""
    <div style='background:linear-gradient(135deg,#0d1a2e,#0a1628);padding:48px;text-align:center;border-top:1px solid #1e3352;border-bottom:1px solid #1e3352;'>
        <div style='font-family:Rajdhani,sans-serif;font-size:36px;font-weight:700;color:#e8f4ff;margin-bottom:12px;'>
            Siap Menutup Kebocoran Bisnis Anda?
        </div>
        <div style='font-size:15px;color:#7a9bbf;margin-bottom:28px;'>
            Konsultasi gratis 30 menit dengan tim V-Guard AI. Tidak ada kewajiban apapun.
        </div>
    </div>""", unsafe_allow_html=True)

    _, cf1, cf2, _ = st.columns([1,1,1,1])
    with cf1:
        st.link_button("Book Demo Gratis", WA_LINK_DEMO, use_container_width=True)
    with cf2:
        st.link_button("Chat Sekarang", WA_LINK_KONSUL, use_container_width=True)

    # =========================================================================
    # CHATBOT SENTINEL CS — Bagian Bawah Beranda
    # =========================================================================
    st.markdown("""
    <div class='cs-section'>
        <div class='section-header'>Sentinel CS — <span class='section-accent'>Konsultan AI 24/7</span></div>
        <div class='section-subheader'>Tanya apa saja · AI langsung cocokkan dengan paket terbaik untuk bisnis Anda</div>
    </div>""", unsafe_allow_html=True)

    cs_main, cs_side = st.columns([1.8, 1], gap="large")

    with cs_main:

        # ── Tampilkan Product Match Banner jika paket terdeteksi ──────────
        dp = st.session_state.get("detected_package")
        if dp:
            hb, hs = HARGA_MAP.get(dp, ("Custom", "—"))
            prod_lnk  = PRODUCT_LINKS.get(dp, BASE_APP_URL)
            order_lnk = ORDER_LINKS.get(dp, WA_LINK_KONSUL)
            st.markdown(
                "<div class='match-banner'>"
                "<div class='match-banner-title'>🎯 Paket Yang Cocok untuk Anda: " + dp + "</div>"
                "<div class='match-banner-body'>" + hb + "/bln · Setup " + hs
                + " &nbsp;·&nbsp; <a href='" + prod_lnk + "' target='_blank' "
                "style='color:#00d4ff;'>Lihat Detail</a>"
                + " &nbsp;|&nbsp; <a href='" + order_lnk + "' target='_blank' "
                "style='color:#00e676;'>Order Sekarang</a></div>"
                "</div>",
                unsafe_allow_html=True,
            )
        # ─────────────────────────────────────────────────────────────────

        # ── Tampilkan riwayat percakapan ──────────────────────────────────
        if not st.session_state.cs_chat_history:
            st.markdown(
                "<div style='background:#0d1626;border:1px solid #1e3352;border-radius:14px;"
                "padding:24px;min-height:120px;'>"
                "<div style='margin-bottom:4px;'>"
                "<div class='chat-label'>Sentinel CS — V-Guard AI</div>"
                "<div class='chat-bubble-ai'>"
                "Halo! Saya <b>Sentinel CS</b>, konsultan AI pribadi V-Guard AI Intelligence. 👋<br><br>"
                "Saya di sini untuk membantu Anda <b>menutup kebocoran bisnis secara permanen</b> "
                "dengan teknologi yang bekerja 24/7 — tanpa lelah, tanpa kompromi.<br><br>"
                "Ceritakan bisnis Anda — berapa <b>kasir/cabang</b> dan "
                "<b>omzet bulanan</b> Anda? Saya akan langsung hitung potensi penghematan "
                "dan rekomendasikan paket yang paling menguntungkan untuk Anda. 💡"
                "</div></div></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div style='background:#0d1626;border:1px solid #1e3352;border-radius:14px;"
                "padding:24px;min-height:120px;'>",
                unsafe_allow_html=True,
            )
            for msg in st.session_state.cs_chat_history:
                if msg["role"] == "user":
                    st.markdown(
                        "<div style='text-align:right;margin-bottom:4px;'>"
                        "<div class='chat-label'>Anda</div>"
                        "<div style='display:inline-block;'>"
                        "<div class='chat-bubble-user'>" + msg["content"] + "</div></div></div>",
                        unsafe_allow_html=True,
                    )
                else:
                    content = msg["content"].replace("\n", "<br>")
                    st.markdown(
                        "<div style='margin-bottom:4px;'>"
                        "<div class='chat-label'>Sentinel CS — V-Guard AI</div>"
                        "<div class='chat-bubble-ai'>" + content + "</div></div>",
                        unsafe_allow_html=True,
                    )
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Quick Prompts — dirancang memicu Product Matching ─────────────
        qp_cols = st.columns(4)
        quick_prompts = [
            "Saya punya warung 1 kasir",
            "Toko saya punya 3 cabang dan banyak kasir",
            "Hitung ROI untuk omzet 50 juta",
            "Pantau toko dengan kamera CCTV AI",
        ]
        for i, (c, qp_text) in enumerate(zip(qp_cols, quick_prompts)):
            with c:
                if st.button(qp_text, key="beranda_qp_" + str(i), use_container_width=True):
                    st.session_state.cs_chat_history.append({"role": "user", "content": qp_text})
                    with st.spinner("Sentinel CS menganalisis kebutuhan Anda..."):
                        answer = get_ai_response(qp_text)
                    st.session_state.cs_chat_history.append({"role": "assistant", "content": answer})
                    st.rerun()

        # ── Chat Input ────────────────────────────────────────────────────
        user_msg_beranda = st.chat_input(
            "Ceritakan bisnis Anda — kasir, cabang, atau masalah yang dihadapi...",
            key="chat_beranda",
        )
        if user_msg_beranda:
            st.session_state.cs_chat_history.append({"role": "user", "content": user_msg_beranda})
            with st.spinner("Sentinel CS menganalisis kebutuhan Anda..."):
                answer = get_ai_response(user_msg_beranda)
            st.session_state.cs_chat_history.append({"role": "assistant", "content": answer})
            st.rerun()

    with cs_side:
        # ── Info Kapabilitas CS ───────────────────────────────────────────
        st.markdown(
            "<div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;"
            "padding:20px;margin-bottom:16px;'>"
            "<div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;"
            "color:#00d4ff;margin-bottom:12px;'>🤖 Sentinel CS Bisa Bantu:</div>"
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

        # ── Panduan Product Matching ──────────────────────────────────────
        st.markdown(
            "<div style='background:#0d1626;border:1px solid #1e3352;border-radius:12px;"
            "padding:18px;margin-bottom:16px;'>"
            "<div style='font-family:Rajdhani,sans-serif;font-size:14px;font-weight:700;"
            "color:#e8f4ff;margin-bottom:12px;'>🎯 Cara Cepat Dapat Rekomendasi:</div>"
            + "".join([
                "<div style='background:#101c2e;border-radius:6px;padding:8px 10px;"
                "margin-bottom:6px;font-size:11px;color:#7a9bbf;line-height:1.5;'>"
                "<span style='color:" + color + ";font-weight:700;'>" + pkg + "</span> → " + hint + "</div>"
                for pkg, hint, color in [
                    ("V-LITE",    "Sebutkan: warung, 1 kasir, kios",           "#00d4ff"),
                    ("V-PRO",     "Sebutkan: pantau toko, kamera, cafe",       "#6ac8ff"),
                    ("V-ADVANCE", "Sebutkan: kasir, stok, banyak cabang",      "#b49fff"),
                    ("V-ELITE",   "Sebutkan: perusahaan besar, server privat", "#00e676"),
                    ("V-ULTRA",   "Sebutkan: white label, custom platform",    "#ffd700"),
                ]
            ])
            + "</div>",
            unsafe_allow_html=True,
        )

        # ── Install Info ──────────────────────────────────────────────────
        st.markdown(
            "<div style='background:#0d1626;border:1px solid #1e3352;border-radius:12px;"
            "padding:18px;margin-bottom:16px;'>"
            "<div style='font-family:Rajdhani,sans-serif;font-size:14px;font-weight:700;"
            "color:#e8f4ff;margin-bottom:12px;'>Panduan Instalasi</div>"
            "<div style='background:#00e67611;border:1px solid #00e67633;border-radius:8px;"
            "padding:10px;margin-bottom:8px;'>"
            "<div style='font-size:11px;font-weight:700;color:#00e676;"
            "font-family:JetBrains Mono,monospace;'>PLUG & PLAY ✅</div>"
            "<div style='font-size:11px;color:#7a9bbf;margin-top:4px;'>"
            "V-LITE & V-PRO — Mandiri, tanpa teknisi, tanpa kabel ribet</div></div>"
            "<div style='background:#ffab0011;border:1px solid #ffab0033;border-radius:8px;padding:10px;'>"
            "<div style='font-size:11px;font-weight:700;color:#ffab00;"
            "font-family:JetBrains Mono,monospace;'>INTEGRASI PROFESIONAL 🔧</div>"
            "<div style='font-size:11px;color:#7a9bbf;margin-top:4px;'>"
            "V-ADVANCE, V-ELITE, V-ULTRA — Teknisi V-Guard ke lokasi Anda</div>"
            "</div></div>",
            unsafe_allow_html=True,
        )

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("Reset Chat", key="reset_chat_beranda", use_container_width=True):
                st.session_state.cs_chat_history = []
                st.session_state["detected_package"] = None
                st.rerun()
        with col_r2:
            st.link_button("WhatsApp", WA_LINK_KONSUL, use_container_width=True)

# =============================================================================
# 13. PRODUK & HARGA
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
        {
            "key": "LITE", "name": "V-LITE", "badge_cls": "badge-entry", "badge_txt": "Entry Level",
            "focus": "Fondasi keamanan digital untuk usaha satu kasir",
            "price": "Rp 150.000", "period": "/ bulan", "setup": "Setup: Rp 250.000",
            "popular": False, "ultra": False, "plug_play": True,
            "features": [
                "Deteksi VOID & Cancel",
                "Daily AI Summary via WhatsApp",
                "Dashboard Web Real-Time",
                "Laporan Kebocoran Otomatis",
                "Support via WhatsApp",
            ],
        },
        {
            "key": "PRO", "name": "V-PRO", "badge_cls": "badge-pro", "badge_txt": "Pro",
            "focus": "Otomasi admin, stok, & audit bank tanpa input manual",
            "price": "Rp 450.000", "period": "/ bulan", "setup": "Setup: Rp 750.000",
            "popular": True, "ultra": False, "plug_play": True,
            "features": [
                "Semua fitur V-LITE",
                "VCS Secure Integration",
                "Bank Statement Audit Otomatis",
                "Input Invoice via OCR",
                "Laporan PDF Terjadwal",
                "Support Prioritas 24/7",
            ],
        },
        {
            "key": "ADVANCE", "name": "V-ADVANCE", "badge_cls": "badge-adv", "badge_txt": "Pengawas Aktif",
            "focus": "Mata AI pengawas aktif — visual, stok & multi-cabang",
            "price": "Rp 1.200.000", "period": "/ bulan", "setup": "Setup: Rp 3.500.000",
            "popular": False, "ultra": False, "plug_play": False,
            "features": [
                "Semua fitur V-PRO",
                "CCTV AI — Visual Cashier Audit",
                "WhatsApp Fraud Alarm Instan",
                "H-7 Auto Collection Reminder",
                "Multi-Cabang Dashboard",
            ],
        },
        {
            "key": "ELITE", "name": "V-ELITE", "badge_cls": "badge-ent", "badge_txt": "Korporasi",
            "focus": "Kedaulatan data penuh — server privat & AI forensik",
            "price": "Mulai Rp 3.500.000", "period": "/ bulan", "setup": "Setup: Rp 10.000.000",
            "popular": False, "ultra": False, "plug_play": False,
            "features": [
                "Semua fitur V-ADVANCE",
                "Deep Learning Forensik AI",
                "Dedicated Private Server",
                "Custom AI SOP per Divisi",
                "On-site Implementation",
                "SLA 99.9% Uptime",
            ],
        },
        {
            "key": "ULTRA", "name": "V-ULTRA", "badge_cls": "badge-ultra", "badge_txt": "Executive",
            "focus": "White-Label & 10 Elite AI Squad aktif penuh",
            "price": "Custom Quote", "period": "Harga khusus korporasi",
            "setup": "Konsultasi strategis gratis",
            "popular": False, "ultra": True, "plug_play": False,
            "features": [
                "Seluruh ekosistem V-ELITE",
                "White-Label Platform",
                "Executive BI Dashboard C-Level",
                "10 Elite AI Squad serentak",
                "Dedicated AI Strategist",
                "V-Guard Secure Liaison Protocol (ERP)",
            ],
        },
    ]

    st.markdown("<div style='padding:28px 40px 0;'>", unsafe_allow_html=True)

    cards_html = ""
    for pkg in PACKAGES:
        feat_html = ""
        for f in pkg["features"]:
            if pkg["ultra"]:
                feat_html += "<div class='pkg-feature-ultra'><span class='pkg-check-ultra'>✓</span>" + f + "</div>"
            else:
                feat_html += "<div class='pkg-feature'><span class='pkg-check'>✓</span>" + f + "</div>"

        install_html = (
            "<span class='install-pill install-pnp'>Plug &amp; Play</span>"
            if pkg["plug_play"]
            else "<span class='install-pill install-pro'>Teknisi Profesional</span>"
        )

        if pkg["popular"]:
            label_html = "<div class='hot-label'>TERLARIS</div>"
            card_cls   = "pkg-card-popular"
        elif pkg["ultra"]:
            label_html = "<div class='ultra-label'>EKSKLUSIF</div>"
            card_cls   = "pkg-card-ultra"
        else:
            label_html = ""
            card_cls   = "pkg-card"

        name_cls  = "pkg-name-ultra" if pkg["ultra"] else "pkg-name"
        price_cls = "pkg-price-ultra" if pkg["ultra"] else "pkg-price"

        # ── Order button per kartu ────────────────────────────────────────
        pkg_key  = "V-" + pkg["key"]
        ord_link = ORDER_LINKS.get(pkg_key, WA_LINK_KONSUL)
        order_btn_html = (
            "<a href='" + ord_link + "' target='_blank' "
            "style='display:block;margin-top:14px;padding:10px;text-align:center;"
            "background:linear-gradient(135deg,#0091ff,#00d4ff);color:#000;"
            "font-family:Rajdhani,sans-serif;font-size:13px;font-weight:700;"
            "border-radius:6px;text-decoration:none;letter-spacing:.5px;'>Order Sekarang</a>"
        )

        card_html = (
            "<div style='flex:1;min-width:0;padding-top:16px;'>"
            "<div class='" + card_cls + "' style='height:100%;'>"
            + label_html
            + "<span class='tier-badge " + pkg["badge_cls"] + "'>" + pkg["badge_txt"] + "</span>"
            + "<div class='" + name_cls + "'>" + pkg["name"] + "</div>"
            + "<div class='pkg-focus'>" + pkg["focus"] + "</div>"
            + "<hr class='pkg-divider'>"
            + "<div class='" + price_cls + "'>" + pkg["price"] + "</div>"
            + "<div class='pkg-period'>" + pkg["period"] + "</div>"
            + "<div class='pkg-setup'>" + pkg["setup"] + "</div>"
            + install_html
            + "<hr class='pkg-divider'>"
            + "<div class='pkg-features-grow'>" + feat_html + "</div>"
            + order_btn_html
            + "</div></div>"
        )
        cards_html += card_html

    st.markdown(
        "<div style='display:flex;flex-direction:row;gap:12px;align-items:stretch;"
        "width:100%;margin-bottom:24px;'>"
        + cards_html
        + "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div style='padding:0 48px 16px;'>"
        "<div style='background:#060b14;border:1px solid #1e3352;border-radius:8px;"
        "padding:14px 20px;font-size:12px;color:#7a9bbf;line-height:1.8;'>"
        "<b style='color:#00e676;'>Plug &amp; Play (V-LITE &amp; V-PRO):</b> "
        "Setup mandiri, tanpa teknisi, tanpa ribet kabel — langsung aktif dalam hitungan menit.&nbsp;&nbsp;"
        "<b style='color:#ffab00;'>Teknisi Profesional (V-ADVANCE, V-ELITE, V-ULTRA):</b> "
        "Memerlukan integrasi khusus oleh teknisi V-Guard di lokasi bisnis Anda."
        "</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    _, ctm, _ = st.columns([1.5, 1, 1.5])
    with ctm:
        st.link_button("Konsultasi Paket via WhatsApp", WA_LINK_KONSUL, use_container_width=True)
    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)

# =============================================================================
# 14. KALKULATOR ROI
# =============================================================================
elif menu == "Kalkulator ROI":
    st.markdown("<div style='padding:40px 48px;'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-title'>Kalkulator <span style='color:#00d4ff;'>Kerugian &amp; ROI</span></div>"
        "<div class='page-subtitle'>Hitung berapa banyak Rupiah yang bocor dari bisnis Anda setiap bulan</div>",
        unsafe_allow_html=True,
    )

    roi_l, roi_r = st.columns([1, 1.2], gap="large")

    with roi_l:
        st.markdown(
            "<div style='background:#101c2e;border:1px solid #1e3352;border-radius:14px;padding:28px;'>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;"
            "color:#e8f4ff;margin-bottom:20px;'>Data Bisnis Anda</p>",
            unsafe_allow_html=True,
        )
        omzet  = st.number_input("Omzet Bulanan (Rp)", value=100_000_000, step=5_000_000, format="%d")
        jenis  = st.selectbox("Jenis Bisnis", ["Kafe / Resto","Retail / Minimarket","Gudang / Distributor","Korporasi Multi-Cabang"])
        cabang = st.number_input("Jumlah Kasir / Cabang", value=1, min_value=1, max_value=100)
        leak   = st.slider("Estimasi % Kebocoran", 1, 25, 5)
        paket_rec = st.selectbox("Paket yang Diminati", [
            "V-LITE (Rp 150rb/bln)",
            "V-PRO (Rp 450rb/bln)",
            "V-ADVANCE (Rp 1,2Jt/bln)",
            "V-ELITE (Mulai Rp 3,5Jt/bln)",
            "V-ULTRA (Custom)",
        ])
        biaya_map = {
            "V-LITE (Rp 150rb/bln)":          150_000,
            "V-PRO (Rp 450rb/bln)":            450_000,
            "V-ADVANCE (Rp 1,2Jt/bln)":      1_200_000,
            "V-ELITE (Mulai Rp 3,5Jt/bln)":  3_500_000,
            "V-ULTRA (Custom)":                        0,
        }
        biaya_vguard = biaya_map[paket_rec]
        st.markdown("</div>", unsafe_allow_html=True)

    with roi_r:
        loss_m  = omzet * (leak / 100)
        loss_y  = loss_m * 12
        save_m  = loss_m * 0.88
        save_y  = save_m * 12
        net_roi = save_m - biaya_vguard if biaya_vguard > 0 else save_m
        roi_pct = (net_roi / biaya_vguard * 100) if biaya_vguard > 0 else 0
        payback = (biaya_vguard / save_m * 30) if save_m > 0 and biaya_vguard > 0 else 0

        st.markdown(
            "<div style='background:#0d1a2e;border:1px solid #ff3b5c55;border-left:3px solid #ff3b5c;"
            "border-radius:14px;padding:24px;margin-bottom:16px;'>"
            "<div style='font-size:13px;color:#7a9bbf;'>Estimasi Kebocoran per Bulan</div>"
            "<div style='font-family:Rajdhani,sans-serif;font-size:42px;font-weight:700;color:#ff3b5c;'>"
            "Rp " + f"{loss_m:,.0f}" + "</div>"
            "<div style='font-size:13px;color:#7a9bbf;margin-top:4px;'>Per tahun: "
            "<b style='color:#ff3b5c;'>Rp " + f"{loss_y:,.0f}" + "</b></div></div>"
            "<div style='background:#0d1a2e;border:1px solid #00e67655;border-left:3px solid #00e676;"
            "border-radius:14px;padding:24px;margin-bottom:16px;'>"
            "<div style='font-size:13px;color:#7a9bbf;'>Estimasi Penyelamatan dengan V-Guard (88%)</div>"
            "<div style='font-family:Rajdhani,sans-serif;font-size:42px;font-weight:700;color:#00e676;'>"
            "Rp " + f"{save_m:,.0f}" + "</div>"
            "<div style='font-size:13px;color:#7a9bbf;margin-top:4px;'>Per tahun: "
            "<b style='color:#00e676;'>Rp " + f"{save_y:,.0f}" + "</b></div></div>",
            unsafe_allow_html=True,
        )

        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown(
                "<div class='stat-card' style='padding:18px;'>"
                "<div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#00d4ff;'>"
                "Rp " + f"{net_roi:,.0f}" + "</div>"
                "<div class='stat-label'>Net ROI / Bulan</div></div>",
                unsafe_allow_html=True,
            )
        with r2:
            roi_disp = "Tak Terhingga" if roi_pct == 0 else f"{roi_pct:.0f}%"
            st.markdown(
                "<div class='stat-card' style='padding:18px;'>"
                "<div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#00d4ff;'>"
                + roi_disp + "</div>"
                "<div class='stat-label'>Return on Investment</div></div>",
                unsafe_allow_html=True,
            )
        with r3:
            pb_disp = "—" if payback == 0 else f"{payback:.0f} Hari"
            st.markdown(
                "<div class='stat-card' style='padding:18px;'>"
                "<div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#00d4ff;'>"
                + pb_disp + "</div>"
                "<div class='stat-label'>Balik Modal</div></div>",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # Tombol order langsung dari halaman ROI
        pkg_from_paket = paket_rec.split(" ")[0]
        ord_link_roi   = ORDER_LINKS.get(pkg_from_paket, WA_LINK_KONSUL)
        wa_roi = urllib.parse.quote(
            "Halo Pak Erwin, saya sudah coba kalkulator ROI V-Guard.\n"
            "Omzet saya Rp " + f"{omzet:,.0f}" + "/bln, estimasi kebocoran " + str(leak) + "%.\n"
            "Saya tertarik dengan paket " + paket_rec + ". Bisa dibantu konsultasi?"
        )
        rcol1, rcol2 = st.columns(2)
        with rcol1:
            st.link_button(
                "Konsultasi Hasil ROI",
                "https://wa.me/" + WA_NUMBER + "?text=" + wa_roi,
                use_container_width=True,
            )
        with rcol2:
            st.link_button(
                "Order " + pkg_from_paket + " Sekarang",
                ord_link_roi,
                use_container_width=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# 15. PORTAL KLIEN
# =============================================================================
elif menu == "Portal Klien":
    st.markdown("<div style='padding:40px 48px;'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-title'>Portal <span style='color:#00d4ff;'>Klien</span></div>"
        "<div class='page-subtitle'>Login ke dashboard monitoring Anda atau daftar sebagai klien baru</div>",
        unsafe_allow_html=True,
    )

    st.success(
        "🤝 PROGRAM KEMITRAAN V-GUARD — Komisi 10% Omset Bersih untuk setiap klien yang bergabung "
        "melalui link referral Anda. Komisi dibayar setiap bulan selama klien aktif berlangganan. "
        "Cek tab 'Program Afiliasi' di bawah untuk link referral unik Anda."
    )

    tab_log, tab_reg, tab_aff = st.tabs(["Login Dashboard", "Daftar / Order Baru", "Program Afiliasi"])

    with tab_log:
        st.markdown("<div style='max-width:480px;margin:32px auto;'>", unsafe_allow_html=True)
        st.markdown(
            "<div class='login-card'>"
            "<div style='text-align:center;margin-bottom:24px;'>"
            "<div style='font-size:40px;'>🛡️</div>"
            "<div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#e8f4ff;'>"
            "Masuk ke Sentinel Dashboard</div>"
            "<div style='font-size:13px;color:#7a9bbf;margin-top:4px;'>"
            "Masukkan kredensial yang dikirim saat aktivasi</div>"
            "</div></div>",
            unsafe_allow_html=True,
        )
        user_id_input = st.text_input("User ID Klien", placeholder="Contoh: VG-XXXXXX")
        password      = st.text_input("Password", type="password", placeholder="Password dari aktivasi")

        if st.button("Masuk ke Dashboard", type="primary", use_container_width=True):
            matched = [k for k in st.session_state.db_umum if k.get("Client_ID") == user_id_input]
            if matched:
                k_data = matched[0]
                if k_data.get("Status") == "Aktif":
                    st.success("Selamat Datang, **" + k_data["Nama Klien"] + "**! Paket **" + k_data["Produk"] + "** Aktif.")
                    st.link_button("Buka Panel " + k_data["Produk"], buat_dashboard_link(user_id_input), use_container_width=True)
                else:
                    st.error("Akun belum aktif. Selesaikan pembayaran atau hubungi Admin.")
                    st.link_button("Aktivasi via WhatsApp", WA_LINK_KONSUL)
            else:
                st.error("User ID tidak ditemukan. Hubungi Admin untuk bantuan.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_reg:
        reg_l, reg_r = st.columns([1.3, 1], gap="large")

        with reg_l:
            with st.form("form_pendaftaran"):
                st.markdown(
                    "<p style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;"
                    "color:#e8f4ff;'>Form Pendaftaran Klien</p>",
                    unsafe_allow_html=True,
                )
                nama_klien  = st.text_input("Nama Lengkap / Owner *")
                nama_usaha  = st.text_input("Nama Usaha *")
                email_klien = st.text_input("Alamat Email *", placeholder="contoh@email.com")
                no_hp       = st.text_input("Nomor WhatsApp *", placeholder="Contoh: 62812xxxx")
                produk      = st.selectbox("Pilih Paket *", ["V-LITE","V-PRO","V-ADVANCE","V-ELITE","V-ULTRA"])

                with st.expander("Syarat & Ketentuan"):
                    st.markdown("""
**1. Pembayaran:** Aktivasi dimulai setelah biaya diverifikasi Admin.
**2. Keamanan:** Data terenkripsi, tidak disebarkan ke pihak ketiga.
**3. Refund:** Tidak ada refund setelah sistem aktif.
**4. Support:** Technical support 24/7 via WhatsApp.
                    """)

                setuju = st.checkbox("Saya telah membaca dan menyetujui Syarat & Ketentuan.")
                submit = st.form_submit_button("Daftar & Dapatkan Akses AI", type="primary", use_container_width=True)

                if submit:
                    if setuju and nama_klien and no_hp and nama_usaha and email_klien:
                        new_cid = buat_client_id(nama_klien, no_hp)
                        st.session_state.db_umum.append({
                            "Nama Klien":    nama_klien,
                            "Nama Usaha":    nama_usaha,
                            "Email":         email_klien,
                            "Produk":        produk,
                            "Status":        "Menunggu Pembayaran",
                            "WhatsApp":      no_hp,
                            "Nilai Kontrak": "0",
                            "Client_ID":     new_cid,
                            "Source":        st.session_state.get("tracking_source", "organic"),
                            "Ref":           st.session_state.get("tracking_ref", ""),
                            "Timestamp":     datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        })
                        st.success("Pendaftaran berhasil! Invoice dikirim ke WhatsApp **" + no_hp + "** dalam 1x24 jam.")
                        st.info("Client ID Anda: **" + new_cid + "**")
                        st.balloons()
                    else:
                        st.error("Mohon isi semua field wajib (*) dan setujui T&C.")

        with reg_r:
            st.markdown(
                "<div style='margin-top:44px;background:#101c2e;border:1px solid #1e3352;"
                "border-radius:14px;padding:24px;'>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<div style='font-family:Rajdhani,sans-serif;font-size:17px;font-weight:700;"
                "color:#e8f4ff;margin-bottom:16px;'>Setelah Mendaftar:</div>",
                unsafe_allow_html=True,
            )
            for icon, step in [
                ("1", "Invoice dikirim via WhatsApp dalam 1×24 jam"),
                ("2", "Transfer ke rekening yang tertera di invoice"),
                ("3", "Konfirmasi pembayaran ke Admin"),
                ("4", "Tim V-Guard setup & aktivasi sistem Anda"),
                ("5", "Kredensial login dikirim & training singkat"),
            ]:
                st.markdown(
                    "<div style='display:flex;gap:12px;align-items:flex-start;margin-bottom:12px;'>"
                    "<span style='background:#00d4ff22;color:#00d4ff;border-radius:50%;width:22px;height:22px;"
                    "display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;"
                    "flex-shrink:0;font-family:Rajdhani,sans-serif;'>" + icon + "</span>"
                    "<span style='font-size:13px;color:#7a9bbf;line-height:1.5;'>" + step + "</span></div>",
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
            st.link_button("Tanya via WhatsApp", WA_LINK_KONSUL, use_container_width=True)

    with tab_aff:
        st.markdown("<div style='margin-top:24px;'>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;"
            "color:#e8f4ff;margin-bottom:4px;'>Dashboard Afiliasi & Referral</div>"
            "<div style='font-size:13px;color:#7a9bbf;margin-bottom:24px;'>"
            "Masukkan Client ID Anda untuk melihat link referral unik dan statistik komisi.</div>",
            unsafe_allow_html=True,
        )

        aff_id = st.text_input("Masukkan Client ID Anda", placeholder="Contoh: VG-XXXXXX", key="aff_id_input")

        if aff_id:
            ref_link = buat_referral_link(aff_id)
            st.markdown(
                "<div style='background:#101c2e;border:1px solid #00e67644;border-radius:12px;"
                "padding:24px;margin-bottom:16px;'>"
                "<div style='font-size:12px;color:#7a9bbf;margin-bottom:8px;"
                "font-family:JetBrains Mono,monospace;text-transform:uppercase;letter-spacing:1px;'>"
                "Link Referral Unik Anda</div>"
                "<div class='ref-link-box'>" + ref_link + "</div>"
                "<div style='font-size:12px;color:#7a9bbf;margin-top:10px;'>"
                "Setiap klien yang mendaftar via link ini akan tercatat atas nama Anda. "
                "Komisi 10% Omset Bersih dibayarkan bulanan selama klien aktif.</div>"
                "</div>",
                unsafe_allow_html=True,
            )

            wa_aff_msg = urllib.parse.quote(
                "Halo Pak Erwin, saya ingin bergabung sebagai Mitra Afiliasi V-Guard AI.\n"
                "Client ID saya: " + aff_id + "\n"
                "Mohon info lebih lanjut tentang program komisi 10% Omset Bersih."
            )
            st.link_button(
                "Daftar Program Mitra via WhatsApp",
                "https://wa.me/" + WA_NUMBER + "?text=" + wa_aff_msg,
                use_container_width=True,
            )

            a1, a2, a3 = st.columns(3)
            a1.metric("Komisi per Klien V-PRO",      "Rp 45.000 / bln")
            a2.metric("Komisi per Klien V-ADVANCE",  "Rp 120.000 / bln")
            a3.metric("Komisi per Klien V-ELITE",    "Rp 350.000 / bln")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# 16. ADMIN ACCESS — THE WAR ROOM
# =============================================================================
elif menu == "Admin Access":

    st.markdown("<div style='padding:32px 48px;'>", unsafe_allow_html=True)

    if not st.session_state.admin_logged_in:
        _, lc, _ = st.columns([1, 1, 1])
        with lc:
            st.markdown(
                "<div class='login-card'>"
                "<div style='text-align:center;margin-bottom:24px;'>"
                "<div style='font-size:40px;'>🔒</div>"
                "<div style='font-family:Rajdhani,sans-serif;font-size:24px;font-weight:700;color:#e8f4ff;'>"
                "Admin Access</div>"
                "<div style='font-size:13px;color:#7a9bbf;margin-top:4px;'>"
                "Restricted — Authorized Personnel Only</div>"
                "</div></div>",
                unsafe_allow_html=True,
            )
            admin_pw = st.text_input("Access Code", type="password", key="admin_pw_main")
            if st.button("Masuk ke War Room", type="primary", use_container_width=True, key="btn_admin_main"):
                if admin_pw == "w1nbju8282":
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("Access Code salah!")

    else:
        st.markdown(
            "<div class='page-title'>The War Room — "
            "<span style='color:#00d4ff;'>Admin Control Center</span></div>"
            "<div class='page-subtitle'>V-GUARD AI Ecosystem ©2026 — Founder Edition</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='background:#0d1626;border:1px solid #1e3352;border-radius:10px;"
            "padding:14px 20px;margin-bottom:20px;display:inline-block;'>"
            "<span style='font-size:14px;color:#7a9bbf;font-family:JetBrains Mono,monospace;'>"
            + ai_status_msg + "</span></div>",
            unsafe_allow_html=True,
        )

        if st.button("Logout", key="logout_main"):
            st.session_state.admin_logged_in = False
            st.rerun()

        war_tabs = st.tabs([
            "Dashboard Utama",
            "Agent Squad",
            "Social Media AI",
            "Aktivasi Klien",
            "Fraud Scanner",
            "Database Klien",
            "Investor Dashboard",
        ])

        # ── Tab 1: Dashboard Utama ──────────────────────────────────────────
        with war_tabs[0]:
            total_k   = len(st.session_state.db_umum)
            aktif_k   = sum(1 for k in st.session_state.db_umum if k.get("Status") == "Aktif")
            pending_k = total_k - aktif_k

            m1, m2, m3, m4, m5 = st.columns(5)
            for col, (val, lbl) in zip([m1, m2, m3, m4, m5], [
                (str(total_k),   "Total Klien"),
                (str(aktif_k),   "Klien Aktif"),
                (str(pending_k), "Menunggu Pembayaran"),
                ("99.8%",        "System Uptime"),
                (ai_status,      "AI Status"),
            ]):
                col.metric(lbl, val)

            st.divider()

            src_counts = get_source_counts()
            total_src  = sum(src_counts.values()) or 1
            st.markdown(
                "<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;"
                "color:#e8f4ff;margin-bottom:12px;'>Distribusi Sumber Trafik Pendaftar</div>",
                unsafe_allow_html=True,
            )
            src_cols = st.columns(len(SOURCE_MAP))
            for col, (src_key, src_label) in zip(src_cols, SOURCE_MAP.items()):
                count = src_counts.get(src_key, 0)
                pct   = (count / total_src * 100)
                col.metric(src_label, str(count), delta=f"{pct:.1f}%")

            # ── Product Matching Log ──────────────────────────────────────
            st.divider()
            dp_log = st.session_state.get("detected_package")
            if dp_log:
                st.markdown(
                    "<div class='match-banner'>"
                    "<div class='match-banner-title'>🎯 Sesi Aktif — Paket Terdeteksi dari Chat CS</div>"
                    "<div class='match-banner-body'>Klien sesi ini cocok dengan: <b>" + dp_log + "</b>"
                    " &nbsp;|&nbsp; Harga: " + HARGA_MAP.get(dp_log, ("—","—"))[0] + "/bln"
                    "</div></div>",
                    unsafe_allow_html=True,
                )

        # ── Tab 2: Agent Squad ──────────────────────────────────────────────
        with war_tabs[1]:
            st.markdown(
                "<div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;"
                "color:#e8f4ff;margin-bottom:16px;'>10 Elite AI Squad — Status Real-Time</div>",
                unsafe_allow_html=True,
            )

            AGENTS_STATUS = [
                ("The Auditor",       "Pemindai Integritas Transaksi",     True),
                ("The Liaison",       "Pengirim Notifikasi & Laporan",     True),
                ("The Scribe",        "Otomasi Dokumen & Admin",           True),
                ("The Visionary",     "Analis Visual Cashier (CCTV AI)",   True),
                ("The Watchdog",      "Penjaga Anomali Real-Time",         True),
                ("The Automator",     "Orkestrator Alur Kerja Bisnis",     False),
                ("The Simulator",     "Modeler Skenario & Risiko",         False),
                ("The Growth Hacker", "Analis Performa Revenue",           False),
                ("The Core Brain",    "Strategist AI Eksekutif",           False),
                ("The Concierge",     "Koordinator White-Label & Klien",   False),
            ]

            ag_cols = st.columns(2)
            for i, (name, role, active) in enumerate(AGENTS_STATUS):
                with ag_cols[i % 2]:
                    status_color = "#00e676" if active else "#ffab00"
                    status_txt   = "ACTIVE" if active else "STANDBY"
                    st.markdown(
                        "<div class='war-card'>"
                        "<div style='display:flex;justify-content:space-between;align-items:center;'>"
                        "<div>"
                        "<div class='war-title'>" + name + "</div>"
                        "<div style='font-size:12px;color:#7a9bbf;'>" + role + "</div>"
                        "</div>"
                        "<span style='background:" + status_color + "18;color:" + status_color + ";"
                        "border:1px solid " + status_color + "44;border-radius:20px;font-size:10px;"
                        "padding:3px 10px;font-family:JetBrains Mono,monospace;'>"
                        + status_txt + "</span></div></div>",
                        unsafe_allow_html=True,
                    )

            st.divider()
            st.markdown(
                "<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;"
                "color:#e8f4ff;margin-bottom:12px;'>Kill-Switch — Kontrol AI Agent per Klien</div>",
                unsafe_allow_html=True,
            )

            if not st.session_state.db_umum:
                st.info("Belum ada klien terdaftar di sesi ini.")
            else:
                ks_cols = st.columns(3)
                for i, klien in enumerate(st.session_state.db_umum):
                    cid = klien.get("Client_ID", buat_client_id(klien["Nama Klien"], klien.get("WhatsApp", "")))
                    if cid not in st.session_state.agent_kill_switch:
                        st.session_state.agent_kill_switch[cid] = True
                    cur_state = st.session_state.agent_kill_switch[cid]
                    with ks_cols[i % 3]:
                        st.markdown(
                            "<div style='background:#0d1626;border:1px solid #1e3352;border-radius:8px;"
                            "padding:12px;margin-bottom:10px;'>"
                            "<div style='font-size:13px;color:#e8f4ff;font-weight:600;'>" + klien["Nama Klien"] + "</div>"
                            "<div style='font-size:10px;color:#4a6a8a;font-family:JetBrains Mono,monospace;"
                            "margin-bottom:8px;'>" + cid + " · " + klien["Produk"] + "</div></div>",
                            unsafe_allow_html=True,
                        )
                        btn_label = "AI ON — Klik untuk Matikan" if cur_state else "AI OFF — Klik untuk Nyalakan"
                        if st.button(btn_label, key="ks_" + str(i), use_container_width=True):
                            st.session_state.agent_kill_switch[cid] = not cur_state
                            st.rerun()

        # ── Tab 3: Social Media AI ──────────────────────────────────────────
        with war_tabs[2]:
            st.markdown(
                "<div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;"
                "color:#e8f4ff;margin-bottom:4px;'>Status AI Omnichannel — Social Media</div>"
                "<div style='font-size:13px;color:#7a9bbf;margin-bottom:20px;'>"
                "Monitoring aktivitas otomatisasi konten & sinkronisasi lead dari setiap platform</div>",
                unsafe_allow_html=True,
            )

            sc         = st.session_state.social_status
            plat_names = {
                "linkedin":  "LinkedIn",
                "facebook":  "Facebook",
                "tiktok":    "TikTok",
                "instagram": "Instagram",
                "youtube":   "YouTube",
            }
            sm_cols = st.columns(5)
            for col, (plat_key, plat_label) in zip(sm_cols, plat_names.items()):
                pdata = sc[plat_key]
                with col:
                    status_badge = (
                        "<span class='social-badge-on'>AKTIF</span>"
                        if pdata["active"]
                        else "<span class='social-badge-off'>OFF</span>"
                    )
                    src_count = get_source_counts().get(plat_key, 0)
                    st.markdown(
                        "<div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;padding:18px;'>"
                        "<div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;"
                        "color:#e8f4ff;margin-bottom:6px;'>" + plat_label + "</div>"
                        + status_badge
                        + "<div style='margin-top:12px;'>"
                        "<div style='font-size:11px;color:#7a9bbf;'>Post Hari Ini</div>"
                        "<div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;"
                        "color:#00d4ff;'>" + str(pdata["posts_today"]) + "</div></div>"
                        "<div style='margin-top:8px;'>"
                        "<div style='font-size:11px;color:#7a9bbf;'>Post Terakhir</div>"
                        "<div style='font-size:13px;color:#e8f4ff;'>" + pdata["last_post"] + "</div></div>"
                        "<div style='margin-top:8px;'>"
                        "<div style='font-size:11px;color:#7a9bbf;'>Leads Masuk</div>"
                        "<div style='font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;"
                        "color:#00e676;'>" + str(pdata["leads"]) + "</div></div>"
                        "<div style='margin-top:8px;'>"
                        "<div style='font-size:11px;color:#7a9bbf;'>Pendaftar via Platform</div>"
                        "<div style='font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;"
                        "color:#ffab00;'>" + str(src_count) + "</div></div></div>",
                        unsafe_allow_html=True,
                    )
                    new_state = st.toggle(
                        "Aktifkan " + plat_label,
                        value=pdata["active"],
                        key="sm_toggle_" + plat_key,
                    )
                    if new_state != pdata["active"]:
                        st.session_state.social_status[plat_key]["active"] = new_state
                        st.rerun()

            st.divider()
            st.markdown(
                "<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;"
                "color:#e8f4ff;margin-bottom:12px;'>Log Riset Konten — The Growth Hacker AI</div>",
                unsafe_allow_html=True,
            )
            log_entries = [
                ("09:12", "LinkedIn",  "Riset topik: 'Fraud kasir minimarket 2026' — 47 artikel dipindai"),
                ("09:45", "LinkedIn",  "Draft konten: '5 Tanda Kasir Anda Sedang Curang' — SIAP PUBLISH"),
                ("10:30", "Facebook",  "Riset audit: Viral post tentang kebocoran warung — 3 angle konten dibuat"),
                ("11:00", "Instagram", "Caption generator: 2 carousel post + 1 Reels script — DIJADWALKAN"),
                ("11:30", "TikTok",    "Tren audit: #kasircurang #bisnisbocor — hook video 15 detik dibuat"),
                ("12:00", "TikTok",    "Video script 'Demo V-Guard Live' — antrian jadwal 13:00"),
            ]
            plat_colors = {
                "LinkedIn":  "#0077B5",
                "Facebook":  "#1877F2",
                "Instagram": "#E4405F",
                "TikTok":    "#69C9D0",
                "YouTube":   "#FF0000",
            }
            for ts, plat, entry in log_entries:
                color = plat_colors.get(plat, "#00d4ff")
                st.markdown(
                    "<div style='display:flex;gap:12px;align-items:flex-start;margin-bottom:8px;"
                    "background:#060b14;border:1px solid #1e3352;border-radius:6px;padding:10px 14px;'>"
                    "<span style='font-family:JetBrains Mono,monospace;font-size:11px;color:#4a6a8a;flex-shrink:0;'>"
                    + ts + "</span>"
                    "<span style='background:" + color + "22;color:" + color + ";border:1px solid " + color + "44;"
                    "border-radius:20px;font-size:10px;padding:2px 8px;font-family:JetBrains Mono,monospace;"
                    "flex-shrink:0;'>" + plat + "</span>"
                    "<span style='font-size:12px;color:#7a9bbf;line-height:1.5;'>" + entry + "</span></div>",
                    unsafe_allow_html=True,
                )

            st.markdown(
                "<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;"
                "color:#e8f4ff;margin:16px 0 12px;'>Jadwal Posting Hari Ini</div>",
                unsafe_allow_html=True,
            )
            schedule = [
                ("09:00","LinkedIn","Post Artikel","TERBIT"),
                ("10:30","Facebook","Story + Post","TERBIT"),
                ("11:15","Instagram","Carousel 5 Slide","TERBIT"),
                ("12:00","TikTok","Video 30 Detik","TERBIT"),
                ("14:00","LinkedIn","Polling Interaktif","DIJADWALKAN"),
                ("15:30","Instagram","Reels Demo V-Guard","DIJADWALKAN"),
                ("18:00","Facebook","Testimonial Post","DIJADWALKAN"),
                ("20:00","TikTok","Q&A Video","DIJADWALKAN"),
            ]
            sch_df = pd.DataFrame(schedule, columns=["Waktu","Platform","Konten","Status"])
            st.dataframe(sch_df, use_container_width=True, hide_index=True)

        # ── Tab 4: Aktivasi Klien ───────────────────────────────────────────
        with war_tabs[3]:
            st.markdown(
                "<div style='font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;"
                "color:#e8f4ff;margin-bottom:16px;'>Panel Aktivasi Per Klien</div>",
                unsafe_allow_html=True,
            )

            if not st.session_state.db_umum:
                st.info("Belum ada pendaftar. Klien baru akan muncul setelah mengisi form di Portal Klien.")
            else:
                tabel_data = []
                for k in st.session_state.db_umum:
                    tabel_data.append({
                        "Nama Klien": k.get("Nama Klien", "-"),
                        "Email":      k.get("Email", "-"),
                        "Paket":      k.get("Produk", "-"),
                        "Status":     k.get("Status", "-"),
                        "WhatsApp":   k.get("WhatsApp", "-"),
                        "Client_ID":  k.get("Client_ID", "-"),
                    })
                st.dataframe(pd.DataFrame(tabel_data), use_container_width=True, hide_index=True)
                st.divider()

                for i, klien in enumerate(st.session_state.db_umum):
                    if "Client_ID" not in klien:
                        st.session_state.db_umum[i]["Client_ID"] = buat_client_id(
                            klien["Nama Klien"], klien.get("WhatsApp", "")
                        )
                    cid          = st.session_state.db_umum[i]["Client_ID"]
                    status_kini  = klien.get("Status", "Menunggu Pembayaran")
                    dash_link    = buat_dashboard_link(cid)
                    harga_bul, harga_setup = HARGA_MAP.get(klien["Produk"], ("—", "—"))
                    is_aktif     = status_kini == "Aktif"
                    src_klien    = SOURCE_MAP.get(klien.get("Source", "organic"), "Organik")
                    ref_klien    = klien.get("Ref", "—")

                    card_cls  = "client-card-aktif" if is_aktif else "client-card-pending"
                    badge_cls = "client-badge-aktif" if is_aktif else "client-badge-pending"

                    st.markdown(
                        "<div class='" + card_cls + "'>"
                        "<div class='client-name'>" + klien["Nama Klien"] + " — " + klien.get("Nama Usaha", "-") + "</div>"
                        "<div class='client-id'>" + cid + " · " + klien["Produk"]
                        + " · Sumber: " + src_klien + " · Ref: " + ref_klien + "</div>"
                        "<div class='client-meta'>WA: " + klien.get("WhatsApp", "-")
                        + " · Email: " + klien.get("Email", "-")
                        + " · Harga: " + harga_bul + "/bln · Setup: " + harga_setup + "</div>"
                        "<span class='" + badge_cls + "'>" + status_kini + "</span>"
                        "<div class='client-link'>" + dash_link + "</div></div>",
                        unsafe_allow_html=True,
                    )

                    act1, act2, act3 = st.columns(3)
                    wa_tgt = klien.get("WhatsApp", WA_NUMBER)
                    if not wa_tgt.startswith("62"):
                        wa_tgt = "62" + wa_tgt.lstrip("0")

                    with act1:
                        if is_aktif:
                            if st.button("Deactivate", key="deact_" + str(i), use_container_width=True):
                                st.session_state.db_umum[i]["Status"] = "Menunggu Pembayaran"
                                st.rerun()
                        else:
                            if st.button("Activate", key="act_" + str(i), use_container_width=True, type="primary"):
                                st.session_state.db_umum[i]["Status"] = "Aktif"
                                st.rerun()

                    with act2:
                        wa_inv = (
                            "INVOICE V-GUARD AI\n\n"
                            "Yth. " + klien["Nama Klien"] + "\n"
                            "Usaha: " + klien.get("Nama Usaha", "-") + "\n\n"
                            "Paket: " + klien["Produk"] + "\n"
                            "Biaya Bulanan: " + harga_bul + "\n"
                            "Biaya Setup: " + harga_setup + "\n\n"
                            "Transfer ke:\nBank BCA · No. Rek: 3450074658\n"
                            "A/N: Erwin Sinaga\n\n"
                            "Konfirmasi setelah transfer untuk aktivasi segera.\n— Tim V-Guard AI"
                        )
                        st.link_button(
                            "Kirim Invoice",
                            "https://wa.me/" + wa_tgt + "?text=" + urllib.parse.quote(wa_inv),
                            use_container_width=True,
                        )

                    with act3:
                        wa_akses = (
                            "AKSES DASHBOARD V-GUARD AI\n\n"
                            "Halo " + klien["Nama Klien"] + ",\n\n"
                            + ("Sistem " + klien["Produk"] + " Anda telah AKTIF!\n\n"
                               if is_aktif
                               else "Selesaikan pembayaran untuk mengaktifkan dashboard Anda.\n\n")
                            + "Link Dashboard: " + dash_link + "\n"
                            "Client ID: " + cid + "\n\n"
                            "— Tim V-Guard AI Intelligence"
                        )
                        st.link_button(
                            "Kirim Link Dashboard",
                            "https://wa.me/" + wa_tgt + "?text=" + urllib.parse.quote(wa_akses),
                            use_container_width=True,
                        )

                    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

        # ── Tab 5: Fraud Scanner ────────────────────────────────────────────
        with war_tabs[4]:
            total_omset_bg, batas_bg, persen_bg, warn_bg = hitung_budget_guard(
                st.session_state.db_umum, st.session_state.api_cost_total
            )
            bg1, bg2, bg3 = st.columns(3)
            bg1.metric("Total Omset Kontrak",      "Rp " + f"{total_omset_bg:,.0f}")
            bg2.metric("Batas Anggaran API (20%)", "Rp " + f"{batas_bg:,.0f}")
            bg3.metric("Biaya API Terpakai",       "Rp " + f"{st.session_state.api_cost_total:,.0f}",
                       delta=f"{persen_bg:.1f}%")
            st.progress(min(persen_bg / 100, 1.0))
            if warn_bg:
                st.warning("BUDGET ALERT: " + f"{persen_bg:.1f}%" + " dari batas. Optimalkan frekuensi AI.")
            else:
                st.success("Anggaran AI aman — " + f"{persen_bg:.1f}%" + " terpakai.")

            st.divider()

            df_trx     = get_sample_transaksi()
            hasil_scan = scan_fraud_lokal(df_trx)
            n_void     = len(hasil_scan["void"])
            n_fraud    = len(hasil_scan["fraud"])
            n_sus      = len(hasil_scan["suspicious"])

            fs1, fs2, fs3 = st.columns(3)
            fs1.metric("VOID / Cancel",  n_void,  delta="Tidak Wajar" if n_void  else "Aman")
            fs2.metric("Duplikat Kasir", n_fraud, delta="Terdeteksi"  if n_fraud else "Aman")
            fs3.metric("Selisih Saldo",  n_sus,   delta="Anomali"     if n_sus   else "Aman")

            tv, tf, ts = st.tabs(["VOID / Cancel", "Duplikat Kasir", "Selisih Saldo"])
            with tv:
                if not hasil_scan["void"].empty:
                    st.error("Transaksi VOID mencurigakan ditemukan!")
                    st.dataframe(
                        hasil_scan["void"][["ID_Transaksi","Cabang","Kasir","Jumlah","Waktu"]],
                        use_container_width=True,
                    )
                else:
                    st.success("Tidak ada VOID mencurigakan.")
            with tf:
                if not hasil_scan["fraud"].empty:
                    st.error("Pola duplikat < 5 menit terdeteksi!")
                    st.dataframe(
                        hasil_scan["fraud"][["ID_Transaksi","Cabang","Kasir","Jumlah","selisih_menit"]],
                        use_container_width=True,
                    )
                else:
                    st.success("Tidak ada pola duplikat.")
            with ts:
                if not hasil_scan["suspicious"].empty:
                    st.error("Selisih saldo fisik vs sistem ditemukan!")
                    st.dataframe(
                        hasil_scan["suspicious"][["ID_Transaksi","Cabang","Kasir","Saldo_Fisik","Saldo_Sistem","selisih_saldo"]],
                        use_container_width=True,
                    )
                else:
                    st.success("Saldo seimbang.")

            if model_vguard:
                if st.button("Jalankan AI Deep Scan", type="primary"):
                    with st.spinner("Sentinel AI menganalisis..."):
                        try:
                            prompt = (
                                "Anda adalah Sentinel Fraud AI V-Guard. Analisis data transaksi berikut:\n"
                                + df_trx.to_string(index=False)
                                + "\nBerikan: 1) Indikasi Void tidak wajar, 2) Pola duplikat, "
                                "3) Selisih saldo, 4) Rekomendasi tindakan Owner. Ringkas dan taktis."
                            )
                            resp = model_vguard.generate_content(prompt)
                            result_text = resp.text.strip() if resp.text else "AI berhasil memindai — tidak ada anomali kritis tambahan ditemukan."
                            st.session_state.api_cost_total += 200
                            st.markdown("### Hasil AI Deep Scan:")
                            st.markdown(result_text)
                        except Exception as e:
                            if "429" in str(e):
                                st.error("Kuota AI habis sementara. Coba lagi nanti.")
                            else:
                                st.error("Error AI: " + str(e))
            else:
                st.info("Sambungkan GOOGLE_API_KEY di st.secrets untuk Deep Scan AI.")

            st.divider()
            ada_ancaman = n_void > 0 or n_fraud > 0 or n_sus > 0
            if ada_ancaman:
                st.error("FRAUD TERDETEKSI — Kirim peringatan ke Owner sekarang!")
                cabang_set = set()
                for dpart in hasil_scan.values():
                    if not dpart.empty and "Cabang" in dpart.columns:
                        cabang_set.update(dpart["Cabang"].unique())
                for cab in sorted(cabang_set):
                    st.link_button("Alert Owner — " + cab, buat_link_wa_alert(cab), use_container_width=True)
            else:
                st.success("Tidak ada ancaman aktif.")

        # ── Tab 6: Database Klien ───────────────────────────────────────────
        with war_tabs[5]:
            st.markdown(
                "<div style='font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;"
                "color:#e8f4ff;margin-bottom:16px;'>Database Klien V-Guard</div>",
                unsafe_allow_html=True,
            )
            if st.session_state.db_umum:
                df_db = pd.DataFrame(st.session_state.db_umum)
                if "Client_ID" in df_db.columns:
                    df_db["Dashboard_Link"] = df_db["Client_ID"].apply(buat_dashboard_link)
                    df_db["Referral_Link"]  = df_db["Client_ID"].apply(buat_referral_link)
                st.dataframe(df_db, use_container_width=True, hide_index=True)
                csv = df_db.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Database (CSV)",
                    data=csv,
                    file_name="vguard_clients.csv",
                    mime="text/csv",
                )
            else:
                st.info("Database masih kosong di sesi ini.")

        # ── Tab 7: Investor Dashboard ───────────────────────────────────────
        with war_tabs[6]:
            st.markdown(
                "<div style='font-family:Rajdhani,sans-serif;font-size:24px;font-weight:700;"
                "color:#e8f4ff;margin-bottom:4px;'>Investor Dashboard</div>"
                "<div style='font-size:14px;color:#7a9bbf;margin-bottom:24px;'>"
                "Ringkasan performa bisnis & proyeksi pertumbuhan V-Guard AI</div>",
                unsafe_allow_html=True,
            )

            total_k    = len(st.session_state.db_umum)
            aktif_k    = sum(1 for k in st.session_state.db_umum if k.get("Status") == "Aktif")
            pending_k  = total_k - aktif_k
            mrr        = hitung_proyeksi_omset(st.session_state.db_umum)
            arr        = mrr * 12

            inv1, inv2, inv3, inv4 = st.columns(4)
            inv1.metric("Total Pendaftar",  str(total_k))
            inv2.metric("Klien Aktif",      str(aktif_k))
            inv3.metric("MRR (Proyeksi)",   "Rp " + f"{mrr:,.0f}")
            inv4.metric("ARR (Proyeksi)",   "Rp " + f"{arr:,.0f}")

            st.divider()

            inv_l, inv_r = st.columns([1.3, 1], gap="large")

            with inv_l:
                st.markdown(
                    "<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;"
                    "color:#e8f4ff;margin-bottom:16px;'>Distribusi Trafik Klien per Sumber</div>",
                    unsafe_allow_html=True,
                )
                src_counts = get_source_counts()
                src_df     = pd.DataFrame({
                    "Sumber":  [SOURCE_MAP.get(k, k) for k in src_counts.keys()],
                    "Jumlah":  list(src_counts.values()),
                })
                src_df = src_df[src_df["Jumlah"] > 0]
                if not src_df.empty:
                    st.bar_chart(src_df.set_index("Sumber"), use_container_width=True, color="#00d4ff")
                else:
                    demo_src = pd.DataFrame({
                        "Sumber":  ["WhatsApp","TikTok","Facebook","Instagram","LinkedIn","Organik"],
                        "Jumlah":  [12, 8, 5, 7, 4, 3],
                    })
                    st.bar_chart(demo_src.set_index("Sumber"), use_container_width=True, color="#00d4ff")
                    st.caption("* Data demonstrasi — akan berubah sesuai pendaftar nyata")

                st.divider()

                conv_rate = (aktif_k / total_k * 100) if total_k > 0 else 0
                st.markdown(
                    "<div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;padding:20px;'>"
                    "<div style='display:flex;justify-content:space-between;margin-bottom:12px;'>"
                    "<span style='font-size:13px;color:#7a9bbf;'>Total Pendaftar</span>"
                    "<span style='font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;color:#e8f4ff;'>"
                    + str(total_k) + "</span></div>"
                    "<div style='display:flex;justify-content:space-between;margin-bottom:12px;'>"
                    "<span style='font-size:13px;color:#7a9bbf;'>Klien Aktif</span>"
                    "<span style='font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;color:#00e676;'>"
                    + str(aktif_k) + "</span></div>"
                    "<div style='display:flex;justify-content:space-between;margin-bottom:14px;'>"
                    "<span style='font-size:13px;color:#7a9bbf;'>Menunggu Pembayaran</span>"
                    "<span style='font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;color:#ffab00;'>"
                    + str(pending_k) + "</span></div>"
                    "<div style='background:#1e3352;border-radius:4px;height:8px;overflow:hidden;'>"
                    "<div style='background:linear-gradient(90deg,#00e676,#00d4ff);height:100%;width:"
                    + f"{conv_rate:.0f}" + "%;'></div></div>"
                    "<div style='font-size:11px;color:#7a9bbf;margin-top:6px;'>Conversion Rate: "
                    + f"{conv_rate:.1f}%" + "</div></div>",
                    unsafe_allow_html=True,
                )

            with inv_r:
                st.markdown(
                    "<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;"
                    "color:#e8f4ff;margin-bottom:16px;'>Proyeksi MRR per Paket</div>",
                    unsafe_allow_html=True,
                )

                paket_count = {p: 0 for p in HARGA_NUMERIK.keys()}
                for k in st.session_state.db_umum:
                    if k.get("Status") == "Aktif":
                        produk_k = k.get("Produk", "V-LITE")
                        if produk_k in paket_count:
                            paket_count[produk_k] += 1

                for paket_name, count in paket_count.items():
                    harga_n  = HARGA_NUMERIK.get(paket_name, 0)
                    kontrib  = harga_n * count
                    st.markdown(
                        "<div style='background:#101c2e;border:1px solid #1e3352;border-radius:10px;"
                        "padding:14px 18px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;'>"
                        "<div>"
                        "<div style='font-family:Rajdhani,sans-serif;font-size:15px;font-weight:700;color:#e8f4ff;'>"
                        + paket_name + "</div>"
                        "<div style='font-size:11px;color:#7a9bbf;'>" + str(count) + " klien aktif</div>"
                        "</div>"
                        "<div style='text-align:right;'>"
                        "<div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:#00d4ff;'>"
                        "Rp " + f"{kontrib:,.0f}" + "</div>"
                        "<div style='font-size:10px;color:#4a6a8a;'>/bulan</div>"
                        "</div></div>",
                        unsafe_allow_html=True,
                    )

                st.divider()

                st.markdown(
                    "<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;"
                    "color:#e8f4ff;margin-bottom:12px;'>Proyeksi Pertumbuhan 6 Bulan</div>",
                    unsafe_allow_html=True,
                )
                base_mrr = max(mrr, 1_500_000)
                proyeksi_bulan = []
                for i in range(1, 7):
                    month_name = (datetime.datetime.now() + datetime.timedelta(days=30*i)).strftime("%b %Y")
                    projected  = base_mrr * ((1.15) ** i)
                    proyeksi_bulan.append({"Bulan": month_name, "MRR (Rp)": int(projected)})

                df_proj = pd.DataFrame(proyeksi_bulan)
                st.bar_chart(df_proj.set_index("Bulan"), use_container_width=True, color="#7b2fff")
                st.caption("* Proyeksi asumsi pertumbuhan 15%/bulan")

    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# 17. FOOTER
# =============================================================================
st.markdown(
    "<div style='background:#060b14;border-top:1px solid #1e3352;padding:28px 48px;"
    "display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;'>"
    "<div>"
    "<span style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#00d4ff;'>"
    "V-Guard AI Intelligence</span>"
    "<span style='color:#7a9bbf;font-size:12px;margin-left:12px;'>V-GUARD AI Ecosystem ©2026</span>"
    "</div>"
    "<div style='font-size:12px;color:#7a9bbf;'>"
    "Digitizing Trust · Eliminating Leakage · Protecting Every Rupiah"
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)
