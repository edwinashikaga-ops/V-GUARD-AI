# =============================================================================
# V-GUARD AI INTELLIGENCE — app.py
# Full Rewrite v3.1 — Professional SaaS Edition + 3 Agent Menus Integrated
# =============================================================================

import streamlit as st
import os
import urllib.parse
import hashlib
import pandas as pd
import datetime
import re
import json
import random
from logic_vguard import *
init_vguard_core()
from snippet_1_AI_AGENTS import AI_AGENTS
from snippet_2_menu_functions import menu_visionary, menu_treasurer
# =============================================================================
# 1. PAGE CONFIG — MUST BE FIRST STREAMLIT CALL
# =============================================================================
st.set_page_config(
    page_title="V-Guard AI Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# 2. MULTI-CHANNEL TRACKING
# =============================================================================
_qp = st.query_params
if "tracking_ref" not in st.session_state:
    st.session_state["tracking_ref"] = _qp.get("ref", "")
if "tracking_source" not in st.session_state:
    st.session_state["tracking_source"] = _qp.get("source", "organic")

# =============================================================================
# 3. AI ENGINE — Google Gemini (optional)
# =============================================================================
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

_google_key  = None
ai_status    = "offline"
model_vguard = None

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
# 4. SESSION STATE DEFAULTS
# =============================================================================
_DEFAULTS = {
    "authenticated":         False,
    "admin_logged_in":       False,
    "investor_pw_ok":        False,
    "db_umum":               [],
    "db_pengajuan":          [],
    "db_referrals":          [],
    "api_cost_total":        0.0,
    "cs_chat_history":       [],
    "agent_kill_switch":     {},
    "detected_package":      None,
    "client_logged_in":      False,
    "client_data":           None,
    "agent_logs":            [],
    "fraud_scan_results":    None,
    "portal_form_submitted": False,
    "vision_logs":           [],
    "tr_last_ledger":        None,
    "lia_last_result":       None,
    "lia_last_input":        None,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# =============================================================================
# 5. CONSTANTS
# =============================================================================
WA_NUMBER      = "6282122190885"
WA_LINK_DEMO   = "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote(
    "Halo Pak Erwin, saya ingin Book Demo V-Guard AI."
)
WA_LINK_KONSUL = "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote(
    "Halo Pak Erwin, saya ingin konsultasi mengenai V-Guard AI."
)
BASE_APP_URL = "https://v-guard-ai.streamlit.app"

PRODUCT_LINKS = {
    "V-LITE":    BASE_APP_URL + "/?menu=Produk+%26+Harga#v-lite",
    "V-PRO":     BASE_APP_URL + "/?menu=Produk+%26+Harga#v-pro",
    "V-ADVANCE": BASE_APP_URL + "/?menu=Produk+%26+Harga#v-advance",
    "V-ELITE":   BASE_APP_URL + "/?menu=Produk+%26+Harga#v-elite",
    "V-ULTRA":   BASE_APP_URL + "/?menu=Produk+%26+Harga#v-ultra",
}
ORDER_LINKS = {
    "V-LITE":    "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote(
        "Halo Pak Erwin, saya ingin order Paket V-LITE. Mohon kirimkan invoice."
    ),
    "V-PRO":     "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote(
        "Halo Pak Erwin, saya ingin order Paket V-PRO. Mohon kirimkan invoice."
    ),
    "V-ADVANCE": "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote(
        "Halo Pak Erwin, saya ingin order Paket V-ADVANCE. Mohon kirimkan invoice."
    ),
    "V-ELITE":   "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote(
        "Halo Pak Erwin, saya ingin order Paket V-ELITE. Mohon kirimkan invoice."
    ),
    "V-ULTRA":   "https://wa.me/" + WA_NUMBER + "?text=" + urllib.parse.quote(
        "Halo Pak Erwin, saya ingin konsultasi Paket V-ULTRA (Enterprise Custom)."
    ),
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
KOMISI_RATE = 0.10



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
    hb, hs    = HARGA_MAP.get(pkg, ("Custom", "—"))
    plink     = PRODUCT_LINKS.get(pkg, BASE_APP_URL)
    olink     = ORDER_LINKS.get(pkg, WA_LINK_KONSUL)
    label_map = {
        "V-LITE":    "Fondasi Keamanan Digital (1 Kasir)",
        "V-PRO":     "Otomasi Penuh & Audit Bank",
        "V-ADVANCE": "Pengawas Aktif Multi-Cabang",
        "V-ELITE":   "Kedaulatan Data Korporasi",
        "V-ULTRA":   "White-Label & 10 Elite AI Squad",
    }
    emoji_map = {
        "V-LITE": "🔵", "V-PRO": "⚡", "V-ADVANCE": "🟣",
        "V-ELITE": "🟢", "V-ULTRA": "👑",
    }
    install_note = (
        "✅ **Plug & Play** — aktif mandiri dalam hitungan menit, tanpa teknisi."
        if pkg in ("V-LITE", "V-PRO")
        else "🔧 **Instalasi Profesional** — teknisi V-Guard datang ke lokasi bisnis Anda."
    )
    return (
        "\n\n---\n" + emoji_map.get(pkg, "🛡️") +
        " **Rekomendasi Terbaik: " + pkg + "**\n" +
        "_" + label_map.get(pkg, "") + "_\n\n" +
        "💰 **Biaya Bulanan:** " + hb + "\n🛠️ **Biaya Setup:** " + hs + "\n" +
        install_note + "\n\n" +
        "👉 **[Lihat Detail " + pkg + "](" + plink + ")**   " +
        "📲 **[Order via WhatsApp](" + olink + ")**\n\n" +
        "_Setiap hari tanpa V-Guard adalah hari yang berisiko. Saya siap memandu Anda! 🚀_"
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

ROI: Kebocoran rata-rata 5% omzet. V-Guard cegah 88%.
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
    return BASE_APP_URL + "/?ref=" + cid + "&source=referral"


def buat_payment_link(pkg, nama):
    hb, hs = HARGA_MAP.get(pkg, ("—", "—"))
    txt = urllib.parse.quote(
        "PEMBAYARAN V-GUARD AI\n\nYth. " + nama + "\nPaket: " + pkg + "\n"
        "Biaya Bulanan: " + hb + "\n"
        "Biaya Setup   : " + hs + "\n\n"
        "Transfer ke:\nBank BCA · 3450074658 · a/n Erwin Sinaga\n\n"
        "Konfirmasi setelah transfer ke nomor ini.\n— Tim V-Guard AI"
    )
    return "https://wa.me/" + WA_NUMBER + "?text=" + txt


def hitung_proyeksi_omset(db):
    return sum(
        HARGA_NUMERIK.get(k.get("Produk", "V-LITE"), 0)
        for k in db if k.get("Status") == "Aktif"
    )


def get_sample_transaksi():
    now = datetime.datetime.now()
    return pd.DataFrame({
        "ID_Transaksi": ["TRX-001", "TRX-002", "TRX-003", "TRX-004",
                         "TRX-005", "TRX-006", "TRX-007", "TRX-008"],
        "Cabang":       ["Outlet Sudirman", "Outlet Sudirman", "Resto Central",
                         "Cabang Tangerang", "Outlet Sudirman", "Resto Central",
                         "Cabang Tangerang", "Outlet Sudirman"],
        "Kasir":        ["Budi", "Budi", "Sari", "Andi", "Budi", "Sari", "Andi", "Dewi"],
        "Jumlah":       [150000, 150000, 500000, 200000, 150000, 300000, 50000, 75000],
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
        "Status":       ["VOID", "NORMAL", "NORMAL", "NORMAL",
                         "VOID", "NORMAL", "NORMAL", "NORMAL"],
        "Saldo_Fisik":  [0, 150000, 480000, 200000, 0, 300000, 45000, 75000],
        "Saldo_Sistem": [150000, 150000, 500000, 200000, 150000, 300000, 50000, 75000],
    })


def scan_fraud_lokal(df):
    void_df = df[df["Status"] == "VOID"].copy()
    df_s    = df.sort_values(["Kasir", "Jumlah", "Waktu"]).copy()
    df_s["selisih_menit"] = (
        df_s.groupby(["Kasir", "Jumlah"])["Waktu"]
        .diff().dt.total_seconds().div(60)
    )
    fraud_df = df_s[df_s["selisih_menit"] < 5].copy()
    df2      = df.copy()
    df2["selisih_saldo"] = df2["Saldo_Sistem"] - df2["Saldo_Fisik"]
    sus_df   = df2[df2["selisih_saldo"] != 0].copy()
    return {"void": void_df, "fraud": fraud_df, "suspicious": sus_df}

# =============================================================================
# 9. INTEGRATION STUBS — POS & YOLO CCTV
# =============================================================================

def fetch_pos_data(api_url="http://localhost:8080/api/transactions", api_key=""):
    return get_sample_transaksi()


def process_yolo_cctv_frame(frame_data):
    return {
        "camera_id":    frame_data.get("camera_id", "cam_01"),
        "timestamp":    frame_data.get("timestamp", str(datetime.datetime.now())),
        "detections":   [{"label": "person", "confidence": 0.95, "bbox": [100, 50, 200, 400]}],
        "alert":        False,
        "alert_reason": "",
    }


def trigger_alarm(reason, kasir, cabang, amount, wa_owner=WA_NUMBER):
    msg = (
        "🚨 *ALERT V-GUARD AI*\n\n"
        "📍 Cabang: " + cabang + "\n"
        "👤 Kasir: " + kasir + "\n"
        "💰 Jumlah: Rp " + "{:,.0f}".format(amount) + "\n"
        "⚠️ Alasan: " + reason + "\n"
        "🕐 Waktu: " + datetime.datetime.now().strftime("%H:%M:%S WIB") + "\n\n"
        "Segera cek rekaman CCTV & laporan kasir.\n— Sentinel AI V-Guard"
    )
    return "https://wa.me/" + wa_owner + "?text=" + urllib.parse.quote(msg)


def check_ai_fraud_alarm(pos_df, yolo_results):
    alarms    = []
    void_rows = pos_df[pos_df["Status"] == "VOID"]
    for _, row in void_rows.iterrows():
        for yolo in yolo_results:
            if yolo.get("alert"):
                alarms.append({
                    "kasir":     row["Kasir"],
                    "cabang":    row["Cabang"],
                    "jumlah":    row["Jumlah"],
                    "reason":    "VOID + CCTV: " + yolo["alert_reason"],
                    "camera_id": yolo["camera_id"],
                })
    return alarms


def check_autobilling_reminders(db_klien):
    today     = datetime.date.today()
    reminders = []
    for k in db_klien:
        due_str = k.get("invoice_due_date", "")
        if not due_str:
            continue
        try:
            due_date = datetime.date.fromisoformat(due_str)
            delta    = (due_date - today).days
            if delta in (7, 1):
                reminders.append({
                    "nama":  k.get("Nama Klien", "—"),
                    "usaha": k.get("Nama Usaha", "—"),
                    "wa":    k.get("WhatsApp", ""),
                    "paket": k.get("Produk", "V-LITE"),
                    "due":   due_str,
                    "delta": delta,
                    "cid":   k.get("Client_ID", "—"),
                })
        except Exception:
            pass
    return reminders


def track_referral(ref_cid, new_client_data, setup_amount):
    commission = int(setup_amount * KOMISI_RATE)
    entry = {
        "ref_cid":      ref_cid,
        "new_client":   new_client_data.get("Nama Klien", "—"),
        "new_usaha":    new_client_data.get("Nama Usaha", "—"),
        "paket":        new_client_data.get("Produk", "V-LITE"),
        "setup_fee":    setup_amount,
        "komisi_10pct": commission,
        "status":       "Menunggu Konfirmasi",
        "tanggal":      str(datetime.date.today()),
    }
    st.session_state.db_referrals.append(entry)

# =============================================================================
# 10. AI RESPONSE ENGINE
# =============================================================================
def get_ai_response(user_message):
    detected = detect_package_from_message(user_message)
    if detected:
        st.session_state["detected_package"] = detected

    def fallback(msg, pkg):
        m         = msg.lower()
        omzet_val = 0
        om = re.search(r"(\d[\d.,]*)\s*(juta|jt|miliar|m\b|rb|ribu)?", m)
        if om:
            try:
                raw  = float(om.group(1).replace(",", ".").replace(".", ""))
                unit = (om.group(2) or "").strip().lower()
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
            biaya = HARGA_NUMERIK.get(pkg or "V-PRO", 450_000)
            net   = saved - biaya
            roi   = (net / biaya * 100) if biaya > 0 else 0
            roi_block = (
                "\n\n💡 **Estimasi ROI:**\n"
                "- Omzet: Rp {:,.0f}/bln\n".format(omzet_val) +
                "- Kebocoran 5%: Rp {:,.0f}/bln\n".format(bocor) +
                "- Diselamatkan (88%): **Rp {:,.0f}/bln**\n".format(saved) +
                "- ROI estimasi: **{:.0f}%** 🚀".format(roi)
            )

        if any(k in m for k in ["harga", "berapa", "biaya", "tarif", "paket"]):
            base = "Tentu! Sebelum saya rekomendasikan, boleh saya tahu dulu — **jenis usaha apa** dan berapa **kasir atau cabang** Bapak/Ibu? 😊"
        elif any(k in m for k in ["cctv", "kamera", "pantau", "monitor", "visual"]):
            base = "Untuk kebutuhan **monitoring & CCTV AI**, saya rekomendasikan **V-PRO** 📹\n\n✅ CCTV AI · Audit bank otomatis · **Plug & Play** tanpa teknisi"
            if not pkg:
                base += build_package_cta("V-PRO")
        elif any(k in m for k in ["fraud", "curang", "kecurangan", "void mencurigakan", "kasir curang"]):
            base = "Untuk **deteksi fraud kasir**, solusi terbaik adalah **V-ELITE** 🛡️\n\n✅ Deep Learning Forensik · Private Server · SLA 99.9%"
            if not pkg:
                base += build_package_cta("V-ELITE")
        elif any(k in m for k in ["apa itu", "v-guard", "vguard", "tentang"]):
            base = "**V-Guard AI Intelligence** adalah sistem keamanan bisnis berbasis AI yang mengawasi kasir, stok, dan rekening bank Anda 24/7 🏆\n\n- Cegah kebocoran hingga **88%**\n- Deteksi anomali **< 5 detik**\n- ROI rata-rata **400–900%/bulan**\n\nBoleh ceritakan bisnis Bapak/Ibu? 🙏"
        elif any(k in m for k in ["roi", "hemat", "bocor", "rugi", "omzet"]):
            base = "Rata-rata bisnis kehilangan **3–15% omzet** per bulan tanpa disadari. V-Guard AI mencegah hingga **88% kebocoran** otomatis.\n\nBoleh share **omzet bulanan** bisnis Bapak/Ibu? 😊"
        elif any(k in m for k in ["book demo", "demo", "coba"]):
            base = "Demo V-Guard **gratis 30 menit** — Pak Erwin langsung tunjukkan cara sistem mendeteksi kecurangan secara real-time.\n\n📲 [Book Demo Gratis](" + WA_LINK_DEMO + ")"
        elif any(k in m for k in ["daftar", "order", "beli", "aktivasi", "mulai"]):
            base = "Siap! Untuk memulai, Bapak/Ibu bisa pilih paket:\n\n🔵 V-LITE (Rp 150rb) · ⚡ V-PRO (Rp 450rb) · 🟣 V-ADVANCE (Rp 1,2jt)\n🟢 V-ELITE (Rp 3,5jt) · 👑 V-ULTRA (Custom)\n\nBoleh saya tahu jenis usaha Bapak/Ibu agar saya pilihkan yang paling tepat? 😊"
        elif any(k in m for k in ["referral", "komisi", "ajak", "teman"]):
            base = "Program Referral V-Guard memberikan **komisi 10%** dari biaya setup klien baru yang Anda referensikan! 💰\n\nDaftarkan bisnis Anda di Portal Klien, lalu dapatkan link referral unik. Bagikan ke rekan bisnis & komisi masuk otomatis!"
        else:
            base = "Halo! Saya **Sentinel CS**, konsultan AI V-Guard AI 👋\n\nCeritakan bisnis Bapak/Ibu:\n- Berapa **kasir atau cabang**?\n- Berapa **omzet bulanan** rata-rata?\n\nSaya langsung hitung potensi kebocoran dan rekomendasikan solusi terbaik 💡"

        result = base + roi_block
        if pkg and "Order" not in result and "Rekomendasi" not in result:
            result += build_package_cta(pkg)
        return result

    if model_vguard:
        try:
            hist = []
            for m in st.session_state.cs_chat_history[:-1]:
                hist.append({
                    "role": "model" if m["role"] == "assistant" else "user",
                    "parts": [m["content"]]
                })
            chat_obj = model_vguard.start_chat(history=hist)
            bul, _   = HARGA_MAP.get(detected, ("Custom", "—")) if detected else ("—", "—")
            prompt   = CS_SYSTEM_PROMPT + "\n\nPesan Klien: " + user_message
            if detected:
                prompt += (
                    "\n\n[HINT: Paket cocok: " + detected + " (" + bul + "/bln). "
                    "Sertakan link: " + PRODUCT_LINKS[detected] + " dan " + ORDER_LINKS[detected] + ". "
                    "Akhiri dengan pertanyaan follow-up. Respons max 150 kata.]"
                )
            resp = chat_obj.send_message(prompt)
            ans  = resp.text.strip() if resp.text else ""
            if ans:
                st.session_state.api_cost_total += 200
                return ans
        except Exception:
            pass

    return fallback(user_message, detected)

# =============================================================================
# 10B. AGENT MENU FUNCTIONS
# =============================================================================


def menu_liaison():
    """Agent #4 — Tangan: POS/Moka Integration + Local Fraud Filter"""
    squad   = get_squad()
    liaison = squad.agent(4)

    st.markdown("""
    <div style='padding:32px 48px 0;'>
        <div class='page-title'>🔗 Liaison — <span style='color:#00d4ff;'>Integrasi POS & Filter Lokal</span></div>
        <div class='page-subtitle'>Agent #4 · Tangan Sistem · Hubungkan Moka/SAP/POS, filter 6-rule lokal, hemat 80% API cost.</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='padding:24px 48px;'>", unsafe_allow_html=True)

    is_active    = liaison.is_active()
    status_color = "#00e676" if is_active else "#ff3b5c"
    status_label = "ACTIVE — Filter lokal 6-rule berjalan" if is_active else "KILLED — Filter tidak aktif"

    st.markdown(
        f"<div style='background:#101c2e;border:1px solid #1e3352;border-left:3px solid {status_color};"
        f"border-radius:10px;padding:14px 20px;margin-bottom:20px;display:flex;"
        f"align-items:center;justify-content:space-between;'>"
        f"<div><span style='font-family:JetBrains Mono,monospace;font-size:10px;"
        f"color:{status_color};text-transform:uppercase;letter-spacing:1.5px;'>● {status_label}</span>"
        f"<div style='font-size:12px;color:#7a9bbf;margin-top:4px;'>"
        f"Connectors didukung: Moka · SAP · iReap · Majoo · Olsera · Pawoon · Custom API</div></div>"
        f"<div style='font-family:Rajdhani,sans-serif;font-size:13px;font-weight:700;color:#7a9bbf;'>"
        f"Log entries: {len(liaison._log)}</div></div>",
        unsafe_allow_html=True,
    )

    tab_status, tab_filter, tab_connect = st.tabs([
        "📡 Status Koneksi POS",
        "🔍 Jalankan Filter Lokal",
        "⚙️ Tambah Koneksi Baru",
    ])

    # ── TAB 1: Status koneksi ────────────────────────────────────────────────
    with tab_status:
        CONNECTORS = [
            {"id":"moka",       "name":"Moka POS",    "icon":"🟢", "endpoint":"https://api.moka.id/v2/transactions",     "status":"CONNECTED",   "latency":"142ms"},
            {"id":"sap",        "name":"SAP B1",       "icon":"🟡", "endpoint":"http://sap-server.local:50000/b1s",       "status":"TIMEOUT",     "latency":"—"},
            {"id":"ireap",      "name":"iReap POS",    "icon":"🟢", "endpoint":"http://localhost:8080/api/ireap",         "status":"CONNECTED",   "latency":"89ms"},
            {"id":"majoo",      "name":"Majoo",        "icon":"⚪", "endpoint":"https://api.majoo.id/v1/report",          "status":"BELUM_SETUP", "latency":"—"},
            {"id":"olsera",     "name":"Olsera",       "icon":"⚪", "endpoint":"https://api.olsera.com/transactions",     "status":"BELUM_SETUP", "latency":"—"},
            {"id":"pawoon",     "name":"Pawoon",       "icon":"⚪", "endpoint":"https://api.pawoon.com/v1/sales",         "status":"BELUM_SETUP", "latency":"—"},
            {"id":"custom_api", "name":"Custom API",   "icon":"🔵", "endpoint":"http://localhost:8080/api/transactions",  "status":"STUB_AKTIF",  "latency":"< 1ms"},
        ]
        color_map = {"CONNECTED":"#00e676","TIMEOUT":"#ff3b5c","BELUM_SETUP":"#4a6a8a","STUB_AKTIF":"#00d4ff"}
        label_map = {"CONNECTED":"✅ CONNECTED","TIMEOUT":"❌ TIMEOUT","BELUM_SETUP":"⚪ BELUM SETUP","STUB_AKTIF":"🔵 STUB (Demo)"}

        cols = st.columns(2)
        for i, conn in enumerate(CONNECTORS):
            with cols[i % 2]:
                c = color_map.get(conn["status"], "#7a9bbf")
                l = label_map.get(conn["status"], conn["status"])
                st.markdown(
                    f"<div style='background:#101c2e;border:1px solid #1e3352;border-left:3px solid {c};"
                    f"border-radius:10px;padding:14px 16px;margin-bottom:10px;'>"
                    f"<div style='display:flex;justify-content:space-between;align-items:flex-start;'>"
                    f"<div><div style='font-family:Rajdhani,sans-serif;font-size:15px;font-weight:700;color:#e8f4ff;'>"
                    f"{conn['icon']} {conn['name']}</div>"
                    f"<div style='font-family:JetBrains Mono,monospace;font-size:10px;color:#4a6a8a;"
                    f"margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:240px;'>"
                    f"{conn['endpoint']}</div></div>"
                    f"<div style='text-align:right;'>"
                    f"<div style='font-family:JetBrains Mono,monospace;font-size:9px;color:{c};"
                    f"border:1px solid {c}44;background:{c}11;padding:2px 8px;border-radius:20px;white-space:nowrap;'>{l}</div>"
                    f"<div style='font-size:10px;color:#7a9bbf;margin-top:4px;'>Latency: {conn['latency']}</div>"
                    f"</div></div></div>",
                    unsafe_allow_html=True,
                )

    # ── TAB 2: Filter lokal ──────────────────────────────────────────────────
    with tab_filter:
        st.markdown(
            "<div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;"
            "color:#e8f4ff;margin-bottom:6px;'>🔍 Local Filter Engine — 6 Aturan Deteksi</div>"
            "<div style='font-size:13px;color:#7a9bbf;margin-bottom:14px;'>"
            "Hanya baris anomali yang dikirim ke Cloud AI — hemat 80% biaya API.</div>",
            unsafe_allow_html=True,
        )
        RULES = [
            ("R1","VOID / Cancel langsung flag",                   "#ff3b5c"),
            ("R2","VOID rate > 20% per kasir",                    "#ff3b5c"),
            ("R3","Transaksi duplikat < 5 menit (kasir+jumlah)",  "#ffab00"),
            ("R4","Selisih saldo fisik ≠ saldo sistem",            "#ffab00"),
            ("R5","Jam tidak wajar (< 07:00 / ≥ 23:00 WIB)",     "#7b2fff"),
            ("R6","Rapid VOID > 2× dalam 10 menit",               "#ff3b5c"),
        ]
        rc = st.columns(3)
        for i, (rid, desc, color) in enumerate(RULES):
            with rc[i % 3]:
                st.markdown(
                    f"<div style='background:#101c2e;border:1px solid #1e3352;"
                    f"border-left:3px solid {color};border-radius:8px;padding:10px 12px;margin-bottom:10px;'>"
                    f"<div style='font-family:JetBrains Mono,monospace;font-size:10px;color:{color};'>{rid}</div>"
                    f"<div style='font-size:12px;color:#9ab8d4;margin-top:4px;'>{desc}</div></div>",
                    unsafe_allow_html=True,
                )

        col_run2, col_src = st.columns([1, 2])
        with col_src:
            data_src = st.radio("Sumber data:", ["Demo (Sample Data)", "Warroom DB"],
                                horizontal=True, key="liaison_src")
        with col_run2:
            run_filter = st.button("⚡ Jalankan Filter Sekarang", type="primary",
                                   key="lia_run", use_container_width=True)

        if run_filter:
            if data_src == "Demo (Sample Data)":
                df_input = get_sample_transaksi()
            else:
                db = st.session_state.get("warroom_db", [])
                df_input = pd.DataFrame(db) if db else get_sample_transaksi()
            with st.spinner("Agent Liaison memfilter transaksi..."):
                result = liaison.run(df_input)
            st.session_state["lia_last_result"] = result
            st.session_state["lia_last_input"]  = df_input

        result   = st.session_state.get("lia_last_result")
        if result and result.get("status") == "OK":
            stats     = result.get("stats", {})
            anomalies = result.get("anomalies", pd.DataFrame())
            clean     = result.get("clean", pd.DataFrame())

            s1, s2, s3, s4, s5 = st.columns(5)
            s1.metric("Total Baris",       str(stats.get("total", 0)))
            s2.metric("Anomali Terfilter", str(stats.get("anomalies", 0)),
                      delta="Naik ke AI" if stats.get("anomalies") else None,
                      delta_color="inverse" if stats.get("anomalies") else "normal")
            s3.metric("Baris Bersih",  str(stats.get("clean", 0)))
            s4.metric("Filter Rate",   stats.get("filter_rate", "—"), delta="Biaya Dihemat")
            s5.metric("API Calls Hemat", str(stats.get("api_cost_saved", 0)))

            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            r_tab_a, r_tab_b = st.tabs(["🔴 Anomali (Naik ke AI)", "🟢 Bersih (Skip API)"])
            with r_tab_a:
                if anomalies is not None and not anomalies.empty:
                    disp_cols = [c for c in
                                 ["ID_Transaksi","Cabang","Kasir","Jumlah","Status","Waktu","_reason"]
                                 if c in anomalies.columns]
                    st.dataframe(anomalies[disp_cols], use_container_width=True, hide_index=True)
                    for _, row in anomalies.drop_duplicates(subset=["Cabang"]).iterrows():
                        reason = str(row.get("_reason","")).strip().rstrip("|").strip()
                        cabang = row.get("Cabang","—")
                        alarm_msg = urllib.parse.quote(
                            f"🚨 V-GUARD LIAISON ALERT\n\n📍 Cabang: {cabang}\n"
                            f"👤 Kasir : {row.get('Kasir','—')}\n⚠️ Rule  : {reason}\n"
                            f"🕐 Waktu : {datetime.datetime.now().strftime('%H:%M:%S WIB')}\n\n"
                            f"Segera cek rekaman CCTV!\n— AgentLiaison V-Guard"
                        )
                        st.link_button(
                            f"📲 Alert — {cabang}",
                            f"https://wa.me/{WA_NUMBER}?text={alarm_msg}",
                            key=f"lia_alert_{cabang}",
                        )
                else:
                    st.success("Tidak ada anomali — semua transaksi bersih.")
            with r_tab_b:
                if clean is not None and not clean.empty:
                    disp_cols = [c for c in
                                 ["ID_Transaksi","Cabang","Kasir","Jumlah","Status","Waktu"]
                                 if c in clean.columns]
                    st.dataframe(clean[disp_cols], use_container_width=True, hide_index=True)
                else:
                    st.info("Semua baris masuk kategori anomali.")
        elif result and result.get("status") == "KILLED":
            st.error("Agent Liaison sedang di-kill. Restart dari panel Admin > AI Agents.")
        else:
            st.info("Klik 'Jalankan Filter Sekarang' untuk memulai analisis.")

    # ── TAB 3: Tambah koneksi baru ───────────────────────────────────────────
    with tab_connect:
        st.markdown(
            "<div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;"
            "color:#e8f4ff;margin-bottom:14px;'>⚙️ Uji & Daftarkan Koneksi POS</div>",
            unsafe_allow_html=True,
        )
        nc1, nc2 = st.columns(2)
        with nc1:
            new_connector = st.selectbox(
                "Tipe Connector",
                ["moka","sap","ireap","majoo","olsera","pawoon","custom_api"],
                key="lia_new_conn",
            )
            new_api_url = st.text_input("API Endpoint URL",
                                        placeholder="https://api.moka.id/v2/transactions",
                                        key="lia_new_url")
        with nc2:
            new_api_key = st.text_input("API Key (opsional)", type="password",
                                        placeholder="sk_live_xxxx", key="lia_new_key")
            st.selectbox("Polling Interval",
                         ["15 detik","30 detik","60 detik","5 menit"],
                         index=1, key="lia_poll")

        if st.button("🔌 Test & Daftarkan Koneksi", type="primary", key="lia_connect"):
            with st.spinner(f"Menguji koneksi ke {new_connector}..."):
                conn_result = liaison.connect_pos(new_connector, new_api_url, new_api_key)
            if conn_result.get("status") == "OK":
                st.success(
                    f"✅ Koneksi `{new_connector}` berhasil!\n\n"
                    f"**Endpoint:** `{conn_result.get('endpoint','—')}`\n\n"
                    f"_{conn_result.get('note','')}_"
                )
            else:
                st.error(f"❌ {conn_result.get('msg','Koneksi gagal.')}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

# =============================================================================
# 11. MASTER CSS
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
    color: #000 !important; font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important; font-size: 15px !important;
    border: none !important; border-radius: 6px !important;
    height: 46px !important; transition: all .2s ease !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 0 20px var(--border-glow) !important; }
a[data-testid="stLinkButton"] button {
    background: linear-gradient(135deg, #25D366, #128C7E) !important;
    color: white !important; font-weight: 700 !important; border-radius: 6px !important;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important; border-radius: 6px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important; box-shadow: 0 0 10px var(--border-glow) !important;
}
[data-testid="stMetric"] {
    background: var(--bg-card) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; padding: 16px !important;
}
[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 12px !important; }
[data-testid="stMetricValue"] {
    color: var(--accent) !important; font-family: 'Rajdhani', sans-serif !important; font-size: 28px !important;
}
.stTabs [data-baseweb="tab-list"] { background: var(--bg-secondary) !important; border-bottom: 1px solid var(--border) !important; }
.stTabs [data-baseweb="tab"] { color: var(--text-muted) !important; font-family: 'Rajdhani', sans-serif !important; font-weight: 600 !important; font-size: 15px !important; }
.stTabs [aria-selected="true"] { color: var(--accent) !important; border-bottom: 2px solid var(--accent) !important; }
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 8px !important; }
[data-testid="stExpander"] { border: 1px solid var(--border) !important; border-radius: 8px !important; background: var(--bg-card) !important; }
.stProgress > div > div > div { background: linear-gradient(90deg, var(--accent2), var(--accent)) !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* CHAT WIDGET */
#vg-fab-wrap { position:fixed !important; bottom:28px !important; right:28px !important; z-index:2147483647 !important; pointer-events:auto !important; }
#vg-fab { width:62px !important; height:62px !important; border-radius:50% !important; background:linear-gradient(135deg,#0091ff,#00d4ff) !important; border:none !important; cursor:pointer !important; box-shadow:0 4px 24px #00d4ff55 !important; display:flex !important; align-items:center !important; justify-content:center !important; font-size:28px !important; animation:vgFloat 3s ease-in-out infinite !important; outline:none !important; -webkit-tap-highlight-color:transparent !important; position:relative !important; }
#vg-fab:hover { animation:none !important; transform:scale(1.1) !important; }
#vg-fab:active { transform:scale(0.95) !important; }
@keyframes vgFloat { 0%,100%{transform:translateY(0px);} 50%{transform:translateY(-8px);} }
#vg-notif { position:absolute !important; top:3px !important; right:3px !important; width:14px !important; height:14px !important; background:#ff3b5c !important; border-radius:50% !important; border:2px solid #060b14 !important; display:none !important; animation:vgPulse 1.5s ease infinite !important; }
#vg-chatbox { position:fixed !important; bottom:104px !important; right:28px !important; width:370px !important; max-height:540px !important; background:#0d1626 !important; border:1px solid #1e3352 !important; border-radius:18px !important; display:none !important; flex-direction:column !important; box-shadow:0 12px 48px #00000099 !important; overflow:hidden !important; z-index:2147483646 !important; pointer-events:auto !important; }
#vg-chatbox.vg-open { display:flex !important; }
@keyframes vgPulse { 0%,100%{opacity:1;} 50%{opacity:.3;} }
#vg-header { background:linear-gradient(135deg,#060b14,#0a1628); border-bottom:1px solid #1e3352; padding:12px 16px; display:flex; align-items:center; gap:10px; flex-shrink:0; user-select:none; }
#vg-msgs { flex:1; overflow-y:auto; padding:14px 12px; display:flex; flex-direction:column; gap:10px; scroll-behavior:smooth; }
#vg-msgs::-webkit-scrollbar { width:4px; }
#vg-msgs::-webkit-scrollbar-thumb { background:#1e3352; border-radius:2px; }
.vg-bot { background:#101c2e; border:1px solid #1e3352; border-radius:14px 14px 14px 4px; padding:10px 14px; font-size:13px; line-height:1.65; color:#e8f4ff; max-width:92%; align-self:flex-start; }
.vg-usr { background:linear-gradient(135deg,#0091ff,#00d4ff); border-radius:14px 14px 4px 14px; padding:10px 14px; font-size:13px; line-height:1.65; color:#000; font-weight:600; max-width:86%; align-self:flex-end; }
.vg-typing { display:flex; gap:5px; padding:4px 2px; align-items:center; }
.vg-typing span { width:8px; height:8px; background:#00d4ff; border-radius:50%; display:inline-block; animation:vgDot 1.3s infinite ease; }
.vg-typing span:nth-child(2) { animation-delay:.18s; }
.vg-typing span:nth-child(3) { animation-delay:.36s; }
@keyframes vgDot { 0%,80%,100%{opacity:.25;transform:scale(.8);} 40%{opacity:1;transform:scale(1);} }
#vg-pills { padding:8px 12px; display:flex; flex-wrap:wrap; gap:6px; border-top:1px solid #1e3352; flex-shrink:0; background:#0d1626; }
.vg-pill { background:#101c2e; border:1px solid #1e3352; color:#7a9bbf; font-size:11px; padding:4px 10px; border-radius:20px; cursor:pointer; transition:all .18s; white-space:nowrap; user-select:none; }
.vg-pill:hover { border-color:#00d4ff; color:#00d4ff; background:#00d4ff11; }
#vg-inputrow { display:flex; gap:8px; padding:10px 12px; border-top:1px solid #1e3352; background:#060b14; flex-shrink:0; align-items:flex-end; }
#vg-input { flex:1; background:#101c2e; border:1px solid #1e3352; border-radius:10px; padding:9px 12px; font-size:13px; color:#e8f4ff; outline:none; font-family:'Inter',sans-serif; resize:none; max-height:90px; min-height:38px; line-height:1.5; transition:border-color .18s; box-sizing:border-box; }
#vg-input:focus { border-color:#00d4ff; box-shadow:0 0 8px #00d4ff22; }
#vg-input::placeholder { color:#4a6a8a; }
#vg-send { background:linear-gradient(135deg,#0091ff,#00d4ff); border:none; border-radius:10px; width:42px; height:42px; cursor:pointer; color:#000; font-size:18px; display:flex; align-items:center; justify-content:center; transition:transform .15s,box-shadow .15s; flex-shrink:0; outline:none; }
#vg-send:hover { transform:scale(1.08); box-shadow:0 2px 14px #00d4ff44; }
#vg-send:active { transform:scale(0.93); }

/* PAGE SECTIONS */
.hero-section { background:linear-gradient(135deg,#060b14 0%,#0a1628 50%,#080f1e 100%); padding:60px 48px 48px; position:relative; overflow:hidden; border-bottom:1px solid var(--border); }
.hero-section::before { content:''; position:absolute; top:-50%; right:-10%; width:600px; height:600px; background:radial-gradient(circle,#00d4ff11 0%,transparent 70%); pointer-events:none; }
.hero-badge { display:inline-block; background:linear-gradient(135deg,#00d4ff22,#0091ff22); border:1px solid var(--accent); color:var(--accent) !important; font-family:'JetBrains Mono',monospace !important; font-size:11px !important; padding:4px 14px; border-radius:20px; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:20px; }
.hero-title { font-family:'Rajdhani',sans-serif !important; font-size:58px !important; font-weight:700 !important; line-height:1.1 !important; color:var(--text-primary) !important; margin-bottom:8px !important; }
.hero-title .accent { color:var(--accent) !important; }
.hero-subtitle { font-size:19px !important; color:var(--text-muted) !important; line-height:1.7 !important; max-width:520px; margin-bottom:36px !important; }
.stat-card { background:linear-gradient(135deg,var(--bg-card),var(--bg-secondary)); border:1px solid var(--border); border-radius:12px; padding:28px 20px; text-align:center; }
.stat-number { font-family:'Rajdhani',sans-serif !important; font-size:44px !important; font-weight:700 !important; background:linear-gradient(135deg,var(--accent),var(--accent3)); -webkit-background-clip:text !important; -webkit-text-fill-color:transparent !important; background-clip:text !important; }
.stat-label { font-size:13px !important; color:var(--text-muted) !important; margin-top:4px; }
.feature-card { background:var(--bg-card); border:1px solid var(--border); border-radius:12px; padding:24px; height:100%; transition:all .3s ease; }
.feature-card:hover { border-color:var(--accent); transform:translateY(-3px); box-shadow:0 8px 30px #00d4ff11; }
.feature-title { font-family:'Rajdhani',sans-serif !important; font-size:17px !important; font-weight:700 !important; color:var(--text-primary) !important; margin-bottom:8px; }
.feature-desc { font-size:13px !important; color:var(--text-muted) !important; line-height:1.6; }
.testimonial-card { background:var(--bg-card); border:1px solid var(--border); border-radius:12px; padding:24px; border-left:3px solid var(--accent); }
.testimonial-text { font-size:14px !important; color:var(--text-primary) !important; line-height:1.7; font-style:italic; margin-bottom:16px; }
.testimonial-author { font-family:'Rajdhani',sans-serif !important; font-size:15px !important; font-weight:700 !important; color:var(--accent) !important; }
.testimonial-role { font-size:12px !important; color:var(--text-muted) !important; }
.stars { color:var(--gold) !important; font-size:14px; margin-bottom:10px; }
.section-header { font-family:'Rajdhani',sans-serif !important; font-size:36px !important; font-weight:700 !important; color:var(--text-primary) !important; text-align:center; margin-bottom:8px !important; }
.section-subheader { font-size:16px !important; color:var(--text-muted) !important; text-align:center; margin-bottom:36px !important; }
.section-accent { color:var(--accent) !important; }
.section-wrapper { padding:56px 48px; border-bottom:1px solid var(--border); }
.section-wrapper-alt { padding:56px 48px; background:var(--bg-secondary); border-bottom:1px solid var(--border); }
.page-title { font-family:'Rajdhani',sans-serif !important; font-size:34px !important; font-weight:700 !important; color:var(--text-primary) !important; margin-bottom:4px !important; }
.page-subtitle { font-size:15px !important; color:var(--text-muted) !important; margin-bottom:32px !important; }
.demo-mockup { background:var(--bg-card); border:1px solid var(--border); border-radius:12px; padding:16px; font-family:'JetBrains Mono',monospace; font-size:12px; color:var(--text-muted); line-height:1.8; }
.demo-dot { display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:4px; }
.demo-red { background:#ff5f57; } .demo-yellow { background:#febc2e; } .demo-green { background:#28c840; }
.sidebar-logo { font-family:'Rajdhani',sans-serif !important; font-size:22px !important; font-weight:700 !important; color:var(--accent) !important; letter-spacing:1px; text-align:center; }
.sidebar-tagline { font-size:10px !important; color:var(--text-muted) !important; text-align:center; letter-spacing:2px; text-transform:uppercase; }
.status-dot { display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--success); margin-right:6px; animation:vgPulse 2s infinite; }
.pkg-card { background:#101c2e; border:1px solid #1e3352; border-radius:14px; padding:22px 16px 20px; display:flex; flex-direction:column; height:100%; transition:all .3s ease; position:relative; }
.pkg-card:hover { border-color:#00d4ff; box-shadow:0 0 28px #00d4ff11; transform:translateY(-4px); }
.pkg-card-ultra { background:linear-gradient(160deg,#12100a,#1a1500,#0e0e0e); border:1px solid #ffd70055; border-radius:14px; padding:22px 16px 20px; display:flex; flex-direction:column; height:100%; transition:all .3s ease; position:relative; }
.pkg-card-ultra:hover { border-color:#ffd700; box-shadow:0 0 32px #ffd70022; transform:translateY(-4px); }
.pkg-card-popular { background:#101c2e; border:1.5px solid #0091ff; border-radius:14px; padding:22px 16px 20px; display:flex; flex-direction:column; height:100%; transition:all .3s ease; position:relative; }
.pkg-card-popular:hover { border-color:#00d4ff; box-shadow:0 0 28px #00d4ff11; transform:translateY(-4px); }
.pkg-features-grow { flex-grow:1; }
.hot-label { position:absolute; top:-12px; left:50%; transform:translateX(-50%); background:linear-gradient(135deg,#0091ff,#00d4ff); color:#000 !important; font-family:'Rajdhani',sans-serif !important; font-size:10px !important; font-weight:700 !important; padding:3px 14px; border-radius:20px; letter-spacing:1px; white-space:nowrap; }
.ultra-label { position:absolute; top:-12px; left:50%; transform:translateX(-50%); background:linear-gradient(135deg,#b8860b,#ffd700); color:#000 !important; font-family:'Rajdhani',sans-serif !important; font-size:10px !important; font-weight:700 !important; padding:3px 14px; border-radius:20px; letter-spacing:1px; white-space:nowrap; }
.tier-badge { display:inline-block; font-family:'JetBrains Mono',monospace !important; font-size:10px !important; letter-spacing:1.5px; text-transform:uppercase; padding:3px 10px; border-radius:20px; margin-bottom:10px; }
.badge-entry { background:#00d4ff18; color:#00d4ff !important; border:1px solid #00d4ff55; }
.badge-pro   { background:#0091ff18; color:#6ac8ff !important; border:1px solid #0091ff55; }
.badge-adv   { background:#7b2fff18; color:#b49fff !important; border:1px solid #7b2fff55; }
.badge-ent   { background:#00e67618; color:#00e676 !important; border:1px solid #00e67655; }
.badge-ultra { background:#ffd70018; color:#ffd700 !important; border:1px solid #ffd70055; }
.pkg-name       { font-family:'Rajdhani',sans-serif !important; font-size:20px !important; font-weight:700 !important; color:#e8f4ff !important; margin-bottom:2px; }
.pkg-name-ultra { font-family:'Rajdhani',sans-serif !important; font-size:20px !important; font-weight:700 !important; color:#ffd700 !important; margin-bottom:2px; }
.pkg-focus      { font-size:11px !important; color:#7a9bbf !important; line-height:1.4; margin-bottom:14px; }
.pkg-price      { font-family:'Rajdhani',sans-serif !important; font-size:24px !important; font-weight:700 !important; color:#00d4ff !important; margin-bottom:2px; }
.pkg-price-ultra{ font-family:'Rajdhani',sans-serif !important; font-size:24px !important; font-weight:700 !important; color:#ffd700 !important; margin-bottom:2px; }
.pkg-period     { font-size:11px !important; color:#7a9bbf !important; margin-bottom:4px; }
.pkg-setup      { font-size:11px !important; color:#4a6a8a !important; margin-bottom:14px; }
.pkg-divider    { border:none; border-top:1px solid #1e3352; margin:12px 0; }
.pkg-feature       { font-size:12px !important; color:#9ab8d4 !important; padding:3px 0; display:flex; align-items:flex-start; gap:6px; line-height:1.4; }
.pkg-feature-ultra { font-size:12px !important; color:#d4b84a !important; padding:3px 0; display:flex; align-items:flex-start; gap:6px; line-height:1.4; }
.pkg-check       { color:#00e676 !important; flex-shrink:0; font-size:11px; }
.pkg-check-ultra { color:#ffd700 !important; flex-shrink:0; font-size:11px; }
.install-pill { display:inline-block; font-family:'JetBrains Mono',monospace !important; font-size:9px !important; padding:2px 8px; border-radius:20px; margin-top:8px; }
.install-pnp  { background:#00e67618; color:#00e676 !important; border:1px solid #00e67644; }
.install-pro  { background:#ffab0018; color:#ffab00 !important; border:1px solid #ffab0044; }
.client-card-aktif   { background:#101c2e; border:1px solid #1e3352; border-left:3px solid #00e676; border-radius:12px; padding:20px; margin-bottom:14px; }
.client-card-pending { background:#101c2e; border:1px solid #1e3352; border-left:3px solid #ffab00; border-radius:12px; padding:20px; margin-bottom:14px; }
.client-badge-aktif  { display:inline-block; background:#00e67618; color:#00e676 !important; border:1px solid #00e67644; border-radius:20px; font-size:10px !important; padding:2px 10px; font-family:'JetBrains Mono',monospace !important; }
.client-badge-pending{ display:inline-block; background:#ffab0018; color:#ffab00 !important; border:1px solid #ffab0044; border-radius:20px; font-size:10px !important; padding:2px 10px; font-family:'JetBrains Mono',monospace !important; }
.login-card   { background:var(--bg-card); border:1px solid var(--border); border-radius:14px; padding:36px; }
.ref-link-box { background:#060b14; border:1px solid #1e3352; border-radius:8px; padding:12px 16px; font-family:'JetBrains Mono',monospace; font-size:12px; color:#00d4ff; word-break:break-all; }
.agent-card         { background:#101c2e; border:1px solid #1e3352; border-radius:12px; padding:16px; transition:all .3s ease; position:relative; }
.agent-card:hover   { border-color:#00d4ff; box-shadow:0 4px 20px #00d4ff11; }
.agent-card-active  { border-left:3px solid #00e676; }
.agent-card-offline { border-left:3px solid #ff3b5c; }
.cctv-frame   { background:#000; border:2px solid #1e3352; border-radius:8px; aspect-ratio:16/9; display:flex; align-items:center; justify-content:center; position:relative; overflow:hidden; }
.cctv-overlay { position:absolute; top:8px; left:8px; font-family:'JetBrains Mono',monospace; font-size:10px; color:#00e676; background:#00000088; padding:4px 8px; border-radius:4px; }
.cctv-alert   { position:absolute; top:8px; right:8px; font-family:'JetBrains Mono',monospace; font-size:10px; color:#ff3b5c; background:#00000088; padding:4px 8px; border-radius:4px; animation:vgPulse 1s infinite; }
.investor-stat     { background:linear-gradient(135deg,#0d1626,#101c2e); border:1px solid #1e3352; border-radius:12px; padding:24px; text-align:center; }
.investor-stat-num { font-family:'Rajdhani',sans-serif !important; font-size:36px !important; font-weight:700 !important; color:#ffd700 !important; }
.investor-stat-lbl { font-size:12px !important; color:#7a9bbf !important; margin-top:4px; }
.pain-card  { background:var(--bg-card); border:1px solid var(--border); border-radius:10px; padding:20px; margin-bottom:12px; border-left:3px solid var(--danger); }
.pain-card:hover { border-color:var(--accent); background:var(--bg-hover); }
.pain-title { font-family:'Rajdhani',sans-serif !important; font-size:16px !important; font-weight:700 !important; color:var(--text-primary) !important; }
.pain-desc  { font-size:13px !important; color:var(--text-muted) !important; margin-top:4px; }
.match-banner       { background:linear-gradient(135deg,#00d4ff18,#0091ff11); border:1px solid #00d4ff55; border-left:3px solid #00d4ff; border-radius:10px; padding:16px 20px; margin-bottom:16px; }
.match-banner-title { font-family:'Rajdhani',sans-serif !important; font-size:15px !important; font-weight:700 !important; color:#00d4ff !important; margin-bottom:4px; }
.match-banner-body  { font-size:13px !important; color:#9ab8d4 !important; }
.ref-card         { background:#101c2e; border:1px solid #1e3352; border-radius:10px; padding:16px 20px; margin-bottom:10px; border-left:3px solid #ffd700; }
.ref-card-paid    { border-left-color:#00e676; }
.ref-badge-pending{ display:inline-block; background:#ffd70018; color:#ffd700 !important; border:1px solid #ffd70044; border-radius:20px; font-size:10px !important; padding:2px 10px; font-family:'JetBrains Mono',monospace !important; }
.ref-badge-paid   { display:inline-block; background:#00e67618; color:#00e676 !important; border:1px solid #00e67644; border-radius:20px; font-size:10px !important; padding:2px 10px; font-family:'JetBrains Mono',monospace !important; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 12. THE CONCIERGE CHAT WIDGET
# =============================================================================
CHAT_WIDGET_HTML = r"""
<div id="vg-fab-wrap">
    <button id="vg-fab" aria-label="Chat Sentinel CS" title="Chat dengan Sentinel CS">
        🛡️<div id="vg-notif"></div>
    </button>
</div>
<div id="vg-chatbox" role="dialog" aria-label="Sentinel CS Chat" aria-modal="true">
    <div id="vg-header">
        <div style="width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,#0091ff,#00d4ff);display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;">🛡️</div>
        <div style="flex:1;min-width:0;">
            <div style="font-family:'Rajdhani',sans-serif;font-size:15px;font-weight:700;color:#e8f4ff;">Sentinel CS</div>
            <div style="font-size:10px;color:#00e676;font-family:'JetBrains Mono',monospace;"><span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#00e676;margin-right:5px;animation:vgPulse 2s infinite;"></span>Online · Siap membantu</div>
        </div>
        <button id="vg-close" aria-label="Tutup chat" style="background:transparent;border:none;color:#7a9bbf;font-size:22px;cursor:pointer;padding:4px 8px;line-height:1;border-radius:6px;transition:color .15s;outline:none;flex-shrink:0;">✕</button>
    </div>
    <div id="vg-msgs">
        <div class="vg-bot">Halo! 👋 Saya <strong>Sentinel CS</strong>, konsultan AI V-Guard.<br><br>Ceritakan bisnis Bapak/Ibu — berapa <strong>kasir atau cabang</strong> dan <strong>omzet bulanan</strong> Anda?<br><br>Saya langsung hitung potensi kebocoran &amp; rekomendasikan paket terbaik 💡</div>
    </div>
    <div id="vg-pills">
        <span class="vg-pill" data-msg="Apa itu V-Guard?">🛡️ Tentang V-Guard</span>
        <span class="vg-pill" data-msg="Lihat semua paket dan harga">📦 Lihat Paket</span>
        <span class="vg-pill" data-msg="Saya punya warung 1 kasir">🏪 Usaha Kecil</span>
        <span class="vg-pill" data-msg="Saya khawatir kasir curang, apa solusinya?">🔍 Deteksi Fraud</span>
        <span class="vg-pill" data-msg="Hitung ROI untuk omzet 50 juta per bulan">💰 Hitung ROI</span>
        <span class="vg-pill" data-msg="Saya ingin book demo gratis">🎯 Book Demo</span>
        <span class="vg-pill" data-msg="Bagaimana program referral dan komisi?">🔗 Referral</span>
    </div>
    <div id="vg-inputrow">
        <textarea id="vg-input" rows="1" placeholder="Ceritakan bisnis Anda..."></textarea>
        <button id="vg-send" aria-label="Kirim pesan">➤</button>
    </div>
</div>
<script>
(function(){
'use strict';
var isOpen=false,isBusy=false;
var fab=document.getElementById('vg-fab'),chatbox=document.getElementById('vg-chatbox'),notif=document.getElementById('vg-notif'),closeBtn=document.getElementById('vg-close'),msgs=document.getElementById('vg-msgs'),input=document.getElementById('vg-input'),sendBtn=document.getElementById('vg-send');
if(!fab||!chatbox||!msgs||!input||!sendBtn||!closeBtn){return;}
function openChat(){isOpen=true;chatbox.classList.add('vg-open');if(notif)notif.style.display='none';fab.style.animation='none';msgs.scrollTop=msgs.scrollHeight;setTimeout(function(){input.focus();},200);}
function closeChat(){isOpen=false;chatbox.classList.remove('vg-open');fab.style.animation='';}
function toggleChat(){if(isOpen)closeChat();else openChat();}
function addBubble(html,isUser){var div=document.createElement('div');div.className=isUser?'vg-usr':'vg-bot';div.innerHTML=html;msgs.appendChild(div);msgs.scrollTop=msgs.scrollHeight;return div;}
function showTyping(){var e=document.getElementById('vg-typing');if(e)e.remove();var div=document.createElement('div');div.className='vg-bot';div.id='vg-typing';div.innerHTML='<div class="vg-typing"><span></span><span></span><span></span></div>';msgs.appendChild(div);msgs.scrollTop=msgs.scrollHeight;}
function removeTyping(){var t=document.getElementById('vg-typing');if(t)t.remove();}
function escHtml(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
var rules=[
{keys:['warung','1 kasir','kios','lapak','usaha kecil','kecil'],reply:'Untuk usaha skala ini, saya rekomendasikan <strong>V-LITE</strong> (Rp 150.000/bln). Plug &amp; Play — aktif dalam menit! 🔵<br><br>💡 Mau saya hitung estimasi kebocoran Bapak/Ibu?'},
{keys:['cafe','kafe','resto','restoran','pantau','monitor','cctv','kamera'],reply:'Untuk pantau toko &amp; CCTV AI, saya rekomendasikan <strong>V-PRO</strong> (Rp 450.000/bln). Termasuk audit bank otomatis! ⚡<br><br>Berapa cabang yang Bapak/Ibu kelola?'},
{keys:['cabang','multi','minimarket','supermarket','franchise','stok'],reply:'Untuk multi-cabang &amp; manajemen stok, <strong>V-ADVANCE</strong> adalah solusinya (Rp 1.200.000/bln). 🟣<br><br>Berapa total kasir Bapak/Ibu?'},
{keys:['fraud','curang','kecurangan','void mencurigakan','kasir curang'],reply:'Untuk deteksi fraud kasir, saya rekomendasikan <strong>V-ELITE</strong>. Deep Learning + Private Server + SLA 99.9% 🟢<br><br>Mau saya jadwalkan demo?'},
{keys:['enterprise','korporasi','white label','rebranding','lisensi'],reply:'Untuk enterprise &amp; white-label, <strong>V-ULTRA</strong> adalah pilihan terbaik. 10 Elite AI Squad! 👑<br><br>Boleh saya hubungkan dengan Founder?'},
{keys:['harga','biaya','berapa','tarif'],reply:'Tentu! Boleh saya tahu:<br>• <strong>Jenis usaha</strong> apa?<br>• Berapa <strong>kasir atau cabang</strong>?<br><br>Saya langsung rekomendasikan yang paling sesuai 😊'},
{keys:['semua paket','lihat paket'],reply:'V-Guard tersedia 5 tier:<br><br>🔵 <strong>V-LITE</strong> Rp 150rb · ⚡ <strong>V-PRO</strong> Rp 450rb<br>🟣 <strong>V-ADVANCE</strong> Rp 1,2jt · 🟢 <strong>V-ELITE</strong> Rp 3,5jt<br>👑 <strong>V-ULTRA</strong> Custom<br><br>Ceritakan bisnis Anda 😊'},
{keys:['demo','coba','book demo','gratis'],reply:'Demo V-Guard <strong>GRATIS 30 menit</strong>!<br><br>📲 <a href="https://wa.me/6282122190885?text=Halo+Pak+Erwin%2C+saya+ingin+Book+Demo+V-Guard+AI." target="_blank" style="color:#00d4ff;">Klik di sini untuk Book Demo</a>'},
{keys:['roi','hemat','bocor','omzet','rugi'],reply:'Rata-rata bisnis kehilangan <strong>3–15% omzet</strong>/bulan. V-Guard mencegah <strong>88% kebocoran</strong>!<br><br>Boleh share omzet bulanan? Saya hitung ROI-nya 💡'},
{keys:['apa itu','v-guard','vguard','tentang'],reply:'<strong>V-Guard AI</strong> adalah sistem keamanan bisnis AI 24/7 🏆<br><br>• Cegah kebocoran <strong>88%</strong><br>• Deteksi anomali &lt;5 detik<br>• ROI <strong>400–900%/bln</strong><br><br>Boleh ceritakan bisnis Anda? 🙏'},
{keys:['referral','komisi','ajak','teman'],reply:'Program Referral V-Guard: <strong>komisi 10%</strong> dari biaya setup klien baru! 💰<br><br>Dapatkan link referral unik di Portal Klien. Mau saya bantu daftarkan?'},
{keys:['daftar','order','beli','aktivasi','mulai'],reply:'Siap! Pilih paket:<br>🔵 V-LITE (150rb) · ⚡ V-PRO (450rb) · 🟣 V-ADVANCE (1,2jt)<br>🟢 V-ELITE (3,5jt) · 👑 V-ULTRA (Custom)<br><br>Jenis usaha Bapak/Ibu? 😊'},
];
function roiCalc(msg){var m=msg.toLowerCase();if(m.indexOf('omzet')===-1&&m.indexOf('roi')===-1&&m.indexOf('juta')===-1&&m.indexOf('jt')===-1)return null;var re=/(\d[\d.,]*)\s*(juta|jt|miliar|m\b|rb|ribu)?/i,match=m.match(re);if(!match)return null;var raw=parseFloat(match[1].replace(/,/g,'.').replace(/\./g,''))||0,unit=(match[2]||'').toLowerCase(),omzet=raw;if(unit==='juta'||unit==='jt')omzet=raw*1e6;else if(unit==='miliar'||unit==='m')omzet=raw*1e9;else if(unit==='rb'||unit==='ribu')omzet=raw*1e3;if(omzet<1e6)return null;var bocor=omzet*.05,saved=bocor*.88,biaya=450000,net=saved-biaya,roi=Math.round(net/biaya*100),fmt=function(n){return Math.round(n).toLocaleString('id-ID');};return '💡 <strong>Estimasi ROI:</strong><br>📊 Omzet: Rp '+fmt(omzet)+'/bln<br>💸 Kebocoran: Rp '+fmt(bocor)+'/bln<br>✅ Diselamatkan: <strong>Rp '+fmt(saved)+'/bln</strong><br>📈 ROI: <strong>'+roi+'%</strong> 🚀<br><br>Rekomendasi: <strong>V-PRO</strong>. Mau lihat detail?';}
function getFallback(msg){var roi=roiCalc(msg);if(roi)return roi;var m=msg.toLowerCase();for(var i=0;i<rules.length;i++){var r=rules[i];for(var j=0;j<r.keys.length;j++){if(m.indexOf(r.keys[j])!==-1)return r.reply;}}return 'Halo! 👋 Saya <strong>Sentinel CS</strong>.<br><br>Ceritakan bisnis Anda:<br>• Berapa <strong>kasir/cabang</strong>?<br>• Berapa <strong>omzet bulanan</strong>?<br><br>Saya rekomendasikan solusi terbaik! 💡';}
function processMsg(text){if(isBusy||!text.trim())return;isBusy=true;addBubble(escHtml(text.trim()),true);showTyping();setTimeout(function(){removeTyping();addBubble(getFallback(text.trim()),false);isBusy=false;},700+Math.random()*800);}
function sendMsg(){var text=input.value;if(!text.trim()||isBusy)return;input.value='';input.style.height='auto';processMsg(text);}
input.addEventListener('input',function(){this.style.height='auto';this.style.height=Math.min(this.scrollHeight,90)+'px';});
fab.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();toggleChat();});
fab.addEventListener('touchend',function(e){e.preventDefault();e.stopPropagation();toggleChat();});
closeBtn.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();closeChat();});
sendBtn.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();sendMsg();});
input.addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMsg();}});
var pills=document.querySelectorAll('.vg-pill');
pills.forEach(function(pill){pill.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();var msg=this.getAttribute('data-msg');if(msg){if(!isOpen)openChat();setTimeout(function(){processMsg(msg);},100);}});});
chatbox.addEventListener('click',function(e){e.stopPropagation();});
chatbox.addEventListener('touchend',function(e){e.stopPropagation();});
document.addEventListener('click',function(e){if(isOpen&&!chatbox.contains(e.target)&&e.target!==fab)closeChat();});
fab.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();toggleChat();}});
setTimeout(function(){if(!isOpen&&notif)notif.style.display='block';},4000);
setTimeout(function(){if(!isOpen)openChat();},14000);
})();
</script>
"""

# =============================================================================
# 13. SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("""
    <div style='padding:20px 0 16px;border-bottom:1px solid #1e3352;margin-bottom:16px;'>
        <div class='sidebar-logo'>V-GUARD AI</div>
        <div class='sidebar-tagline'>Digital Business Auditor</div>
        <div style='text-align:center;margin-top:8px;font-size:11px;color:#7a9bbf;font-family:JetBrains Mono,monospace;'>
            <span class='status-dot'></span>System Online · v3.1
        </div>
    </div>""", unsafe_allow_html=True)

    if os.path.exists("erwin.jpg"):
        st.image("erwin.jpg", use_container_width=True)
        st.markdown("""
        <div style='text-align:center;margin:10px 0 16px;'>
            <p style='color:#e8f4ff;font-weight:bold;margin-bottom:2px;font-size:14px;'>Erwin Sinaga</p>
            <p style='color:#7a9bbf;font-size:12px;'>Founder & CEO</p>
        </div>""", unsafe_allow_html=True)

    _ref = st.session_state.get("tracking_ref", "")
    _src = st.session_state.get("tracking_source", "organic")
    if _ref:
        st.markdown(
            "<div style='background:#00d4ff11;border:1px solid #00d4ff33;border-radius:6px;"
            "padding:6px 10px;margin-bottom:10px;font-size:10px;color:#00d4ff;"
            "font-family:JetBrains Mono,monospace;'>🔗 Ref: " + _ref + " · " + SOURCE_MAP.get(_src, _src) + "</div>",
            unsafe_allow_html=True,
        )

    dp = st.session_state.get("detected_package")
    if dp:
        hb, _ = HARGA_MAP.get(dp, ("Custom", "—"))
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

    PUBLIC_MENU  = ["Beranda", "Produk & Harga", "Kalkulator ROI", "Portal Klien"]
    PRIVATE_MENU = []
    if st.session_state.authenticated:
        if st.session_state.investor_pw_ok:
            PRIVATE_MENU.append("Investor Area")
        if st.session_state.admin_logged_in:
            PRIVATE_MENU.append("Admin Access")
            PRIVATE_MENU.append("👁️ Visionary CCTV")
            PRIVATE_MENU.append("💰 Treasurer")
            PRIVATE_MENU.append("🔗 Liaison POS")

    MENU_OPTIONS = PUBLIC_MENU + PRIVATE_MENU
    menu = st.radio("", MENU_OPTIONS, label_visibility="collapsed")

    if not st.session_state.authenticated:
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        st.markdown(
            "<p style='color:#4a6a8a;font-size:10px;text-transform:uppercase;"
            "letter-spacing:1.5px;margin-bottom:6px;'>Admin / Investor</p>",
            unsafe_allow_html=True,
        )
        _sidebar_pw = st.text_input(
            "Access Code", type="password",
            key="sidebar_access_code",
            placeholder="Masukkan kode akses..."
        )
        if st.button("Masuk", key="btn_sidebar_auth", use_container_width=True):
            if _sidebar_pw == "w1nbju8282":
                st.session_state.authenticated   = True
                st.session_state.admin_logged_in = True
                st.session_state.investor_pw_ok  = True
                st.rerun()
            elif _sidebar_pw == "investor2026":
                st.session_state.authenticated  = True
                st.session_state.investor_pw_ok = True
                st.rerun()
            else:
                st.error("Kode akses salah.")

# =============================================================================
# 14. FLOATING CHAT WIDGET — rendered on EVERY page
# =============================================================================
st.markdown(CHAT_WIDGET_HTML, unsafe_allow_html=True)

# =============================================================================
# 15. PAGE ROUTING
# =============================================================================
if menu == "Beranda":
    st.markdown("""
    <div class="hero-section">
        <div class="hero-badge">AI-Powered Fraud Detection &nbsp;·&nbsp; 24/7 Autonomous</div>
        <div class="hero-title">Hentikan <span class="accent">Kebocoran</span><br>Bisnis Anda. Sekarang.</div>
        <div class="hero-subtitle">V-Guard AI mengawasi setiap Rupiah di kasir, stok, dan rekening bank Anda
        secara otomatis — mendeteksi kecurangan sebelum Anda menyadarinya.</div>
    </div>""", unsafe_allow_html=True)

    c1, c2, _ = st.columns([1.2, 1.2, 3])
    with c1:
        st.link_button("Book Demo Gratis", WA_LINK_DEMO, use_container_width=True)
    with c2:
        st.link_button("Chat Konsultasi", WA_LINK_KONSUL, use_container_width=True)
    st.markdown("<div style='height:48px;'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-wrapper'>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    for col, (n, l) in zip([s1,s2,s3,s4],[
        ("88%","Kebocoran Berhasil Dicegah"),("24/7","Monitoring Otomatis"),
        ("< 5 Dtk","Deteksi Real-Time"),("5 Tier","Solusi Semua Skala"),
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
    for col, group in zip([pc1,pc2,pc3],[PAINS[:2],PAINS[2:4],PAINS[4:]]):
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
        ("🚨","Anomaly Detection Engine","Tandai VOID, refund, dan diskon mencurigakan secara otomatis dalam detik."),
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
        for icon, val, lbl in [("🔍","3 Anomali","Terdeteksi malam ini"),("📲","1 Alert","Dikirim ke Owner"),("📊","100%","Audit Coverage"),("⚡","0.2ms","Response Time")]:
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
    for col, (text, author, role, result) in zip([t1,t2,t3],TESTI):
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
    <div style='background:linear-gradient(135deg,#0d1a2e,#0a1628);padding:48px;
                text-align:center;border-top:1px solid #1e3352;border-bottom:1px solid #1e3352;'>
        <div style='font-family:Rajdhani,sans-serif;font-size:36px;font-weight:700;color:#e8f4ff;margin-bottom:12px;'>Siap Menutup Kebocoran Bisnis Anda?</div>
        <div style='font-size:15px;color:#7a9bbf;margin-bottom:28px;'>Konsultasi gratis 30 menit dengan tim V-Guard AI. Tidak ada kewajiban apapun.</div>
    </div>""", unsafe_allow_html=True)
    _, cf1, cf2, _ = st.columns([1,1,1,1])
    with cf1:
        st.link_button("Book Demo Gratis", WA_LINK_DEMO, use_container_width=True)
    with cf2:
        st.link_button("Chat Sekarang", WA_LINK_KONSUL, use_container_width=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

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
        feat_html  = "".join("<div class='pkg-feature" + ("-ultra" if pkg["ultra"] else "") + "'><span class='pkg-check" + ("-ultra" if pkg["ultra"] else "") + "'>✓</span>" + f + "</div>" for f in pkg["features"])
        install_html = "<span class='install-pill install-pnp'>Plug &amp; Play</span>" if pkg["plug_play"] else "<span class='install-pill install-pro'>Teknisi Profesional</span>"
        if pkg["popular"]:  label_html = "<div class='hot-label'>TERLARIS</div>";   card_cls = "pkg-card-popular"
        elif pkg["ultra"]:  label_html = "<div class='ultra-label'>EKSKLUSIF</div>"; card_cls = "pkg-card-ultra"
        else:               label_html = "";                                          card_cls = "pkg-card"
        name_cls  = "pkg-name-ultra" if pkg["ultra"] else "pkg-name"
        price_cls = "pkg-price-ultra" if pkg["ultra"] else "pkg-price"
        pkg_key   = "V-" + pkg["key"]
        ord_link  = ORDER_LINKS.get(pkg_key, WA_LINK_KONSUL)
        order_btn = "<a href='" + ord_link + "' target='_blank' style='display:block;margin-top:14px;padding:10px;text-align:center;background:linear-gradient(135deg,#0091ff,#00d4ff);color:#000;font-family:Rajdhani,sans-serif;font-size:13px;font-weight:700;border-radius:6px;text-decoration:none;'>Order Sekarang</a>"
        cards_html += "<div style='flex:1;min-width:0;padding-top:16px;'><div class='" + card_cls + "' style='height:100%;'>" + label_html + "<span class='tier-badge " + pkg["badge_cls"] + "'>" + pkg["badge_txt"] + "</span><div class='" + name_cls + "'>" + pkg["name"] + "</div><div class='pkg-focus'>" + pkg["focus"] + "</div><hr class='pkg-divider'><div class='" + price_cls + "'>" + pkg["price"] + "</div><div class='pkg-period'>" + pkg["period"] + "</div><div class='pkg-setup'>" + pkg["setup"] + "</div>" + install_html + "<hr class='pkg-divider'><div class='pkg-features-grow'>" + feat_html + "</div>" + order_btn + "</div></div>"
    st.markdown("<div style='display:flex;flex-direction:row;gap:12px;align-items:stretch;width:100%;margin-bottom:24px;'>" + cards_html + "</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='padding:0 48px 16px;'><div style='background:#060b14;border:1px solid #1e3352;border-radius:8px;padding:14px 20px;font-size:12px;color:#7a9bbf;line-height:1.8;'><b style='color:#00e676;'>Plug &amp; Play (V-LITE &amp; V-PRO):</b> Setup mandiri, tanpa teknisi. &nbsp;&nbsp;<b style='color:#ffab00;'>Teknisi Profesional (V-ADVANCE ke atas):</b> Integrasi oleh teknisi V-Guard di lokasi Anda.</div></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    _, ctm, _ = st.columns([1.5,1,1.5])
    with ctm:
        st.link_button("Konsultasi Paket via WhatsApp", WA_LINK_KONSUL, use_container_width=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

elif menu == "Kalkulator ROI":
    st.markdown("<div style='padding:40px 48px;'>", unsafe_allow_html=True)
    st.markdown("<div class='page-title'>🧮 Kalkulator <span style='color:#00d4ff;'>ROI V-Guard</span></div><div class='page-subtitle'>Hitung estimasi penghematan dan ROI bulanan bisnis Anda secara real-time.</div>", unsafe_allow_html=True)
    col_form, col_result = st.columns([1,1.2], gap="large")
    with col_form:
        st.markdown("<div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;padding:24px;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#00d4ff;margin-bottom:16px;'>Input Data Bisnis</div>", unsafe_allow_html=True)
        jenis_usaha   = st.selectbox("Jenis Usaha",["Warung / 1 Kasir","Toko Ritel / Cafe","Minimarket","Multi-Cabang","Korporasi"],key="roi_jenis")
        omzet_input   = st.number_input("Omzet Bulanan (Rp)",min_value=0,value=50_000_000,step=5_000_000,key="roi_omzet")
        jml_kasir     = st.number_input("Jumlah Kasir",min_value=1,value=2,step=1,key="roi_kasir")
        jml_cabang    = st.number_input("Jumlah Cabang / Outlet",min_value=1,value=1,step=1,key="roi_cabang")
        kebocoran_pct = st.slider("Estimasi Kebocoran Saat Ini (%)",1,20,5,key="roi_bocor")
        if jenis_usaha=="Warung / 1 Kasir": auto_pkg="V-LITE"
        elif jenis_usaha in ("Toko Ritel / Cafe","Minimarket"): auto_pkg="V-PRO"
        elif jenis_usaha=="Multi-Cabang": auto_pkg="V-ADVANCE"
        else: auto_pkg="V-ELITE"
        pkg_options   = ["V-LITE","V-PRO","V-ADVANCE","V-ELITE"]
        paket_dipilih = st.selectbox("Paket Yang Ingin Dievaluasi",pkg_options,index=pkg_options.index(auto_pkg) if auto_pkg in pkg_options else 1,key="roi_paket")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_result:
        biaya_paket  = HARGA_NUMERIK.get(paket_dipilih, 450_000)
        bocor_rp     = omzet_input * (kebocoran_pct / 100)
        diselamatkan = bocor_rp * 0.88
        net_saved    = diselamatkan - biaya_paket
        roi_pct      = (net_saved / biaya_paket * 100) if biaya_paket > 0 else 0
        payback_hari = (biaya_paket / diselamatkan * 30) if diselamatkan > 0 else 0
        hb, hs       = HARGA_MAP.get(paket_dipilih, ("—","—"))
        st.markdown(
            "<div style='background:linear-gradient(135deg,#0d1626,#101c2e);border:1px solid #1e3352;border-radius:12px;padding:24px;margin-bottom:16px;'>"
            "<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#00d4ff;margin-bottom:20px;'>Hasil Kalkulasi — " + paket_dipilih + "</div>"
            "<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;'>"
            "<div style='background:#060b14;border:1px solid #1e3352;border-radius:8px;padding:16px;text-align:center;'><div style='font-size:11px;color:#7a9bbf;margin-bottom:4px;'>Kebocoran/Bulan</div><div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#ff3b5c;'>Rp {:,.0f}</div></div>".format(bocor_rp) +
            "<div style='background:#060b14;border:1px solid #1e3352;border-radius:8px;padding:16px;text-align:center;'><div style='font-size:11px;color:#7a9bbf;margin-bottom:4px;'>Diselamatkan (88%)</div><div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#00e676;'>Rp {:,.0f}</div></div>".format(diselamatkan) +
            "<div style='background:#060b14;border:1px solid #1e3352;border-radius:8px;padding:16px;text-align:center;'><div style='font-size:11px;color:#7a9bbf;margin-bottom:4px;'>Biaya Paket/Bulan</div><div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#ffab00;'>" + hb + "</div></div>" +
            "<div style='background:#060b14;border:1px solid #1e3352;border-radius:8px;padding:16px;text-align:center;'><div style='font-size:11px;color:#7a9bbf;margin-bottom:4px;'>Net Saving/Bulan</div><div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#00d4ff;'>Rp {:,.0f}</div></div>".format(net_saved) +
            "</div><div style='background:linear-gradient(135deg,#00e67611,#00d4ff11);border:1px solid #00e67633;border-radius:10px;padding:20px;text-align:center;'>"
            "<div style='font-size:12px;color:#7a9bbf;margin-bottom:4px;'>ROI Bulanan Estimasi</div>"
            "<div style='font-family:Rajdhani,sans-serif;font-size:56px;font-weight:700;background:linear-gradient(135deg,#00e676,#00d4ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>{:.0f}%</div>".format(roi_pct) +
            "<div style='font-size:12px;color:#7a9bbf;'>Payback Period: ±{:.0f} hari</div></div></div>".format(payback_hari),
            unsafe_allow_html=True,
        )
        st.link_button("Order " + paket_dipilih + " — " + hb + "/bln", ORDER_LINKS.get(paket_dipilih, WA_LINK_KONSUL), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

elif menu == "Portal Klien":
    st.markdown("<div style='padding:32px 48px;'>", unsafe_allow_html=True)
    st.markdown("<div class='page-title'>🏠 Portal <span style='color:#00d4ff;'>Klien</span></div><div class='page-subtitle'>Masuk dengan Client ID Anda, atau ajukan pembelian baru.</div>", unsafe_allow_html=True)

    if st.session_state.client_logged_in and st.session_state.client_data:
        klien  = st.session_state.client_data
        cid    = klien.get("Client_ID","—")
        pkg    = klien.get("Produk","V-LITE")
        status = klien.get("Status","Menunggu Pembayaran")
        hb, hs = HARGA_MAP.get(pkg,("—","—"))
        status_label = "🟢 AKTIF" if status=="Aktif" else "🟡 Menunggu Aktivasi"

        st.markdown(
            "<div style='background:linear-gradient(135deg,#060b14,#0a1628);border:1px solid #1e3352;"
            "border-radius:14px;padding:24px;margin-bottom:24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;'>"
            "<div><div style='font-family:Rajdhani,sans-serif;font-size:24px;font-weight:700;color:#e8f4ff;'>Selamat datang, " + klien.get("Nama Klien","Klien") + " 👋</div>"
            "<div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#00d4ff;margin-top:4px;'>" + cid + " · " + pkg + " · " + status_label + "</div></div>"
            "<div style='text-align:right;'><div style='font-size:12px;color:#7a9bbf;'>Paket</div>"
            "<div style='font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;color:#00d4ff;'>" + pkg + "</div>"
            "<div style='font-size:11px;color:#7a9bbf;'>" + hb + "/bln</div></div></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='background:linear-gradient(135deg,#ffd70011,#ffab0011);border:1px solid #ffd70033;"
            "border-left:3px solid #ffd700;border-radius:10px;padding:14px 20px;margin-bottom:20px;'>"
            "<div style='font-family:Rajdhani,sans-serif;font-size:14px;font-weight:700;color:#ffd700;margin-bottom:4px;'>🎉 Dapatkan Komisi Penjualan 10%!</div>"
            "<div style='font-size:13px;color:#9ab8d4;'>Referensikan rekan bisnis Anda dan dapatkan <strong style='color:#ffd700;'>komisi 10% dari biaya setup</strong> untuk setiap klien baru yang berhasil bergabung.</div></div>",
            unsafe_allow_html=True,
        )

        portal_tabs = st.tabs(["📋 Akun Saya","🔗 Referral & Komisi","📊 Dashboard","📁 Dokumen"])

        with portal_tabs[0]:
            c1, c2 = st.columns(2)
            with c1:
                sc = "#00e676" if status=="Aktif" else "#ffab00"
                st.markdown(
                    "<div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;padding:20px;'>"
                    "<div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:#00d4ff;margin-bottom:16px;'>Informasi Akun</div>"
                    "<div style='font-size:13px;color:#7a9bbf;margin-bottom:8px;'><b style='color:#e8f4ff;'>Nama:</b> " + klien.get("Nama Klien","—") + "</div>"
                    "<div style='font-size:13px;color:#7a9bbf;margin-bottom:8px;'><b style='color:#e8f4ff;'>Usaha:</b> " + klien.get("Nama Usaha","—") + "</div>"
                    "<div style='font-size:13px;color:#7a9bbf;margin-bottom:8px;'><b style='color:#e8f4ff;'>WhatsApp:</b> " + klien.get("WhatsApp","—") + "</div>"
                    "<div style='font-size:13px;color:#7a9bbf;margin-bottom:8px;'><b style='color:#e8f4ff;'>Paket:</b> " + pkg + "</div>"
                    "<div style='font-size:13px;color:#7a9bbf;margin-bottom:8px;'><b style='color:#e8f4ff;'>Status:</b> <span style='color:" + sc + ";'>" + status + "</span></div>"
                    "<div style='font-size:13px;color:#7a9bbf;'><b style='color:#e8f4ff;'>Client ID:</b> <span style='font-family:JetBrains Mono,monospace;color:#00d4ff;'>" + cid + "</span></div></div>",
                    unsafe_allow_html=True,
                )
            with c2:
                if status=="Aktif":
                    st.markdown("<div style='background:#00e67611;border:1px solid #00e67633;border-radius:12px;padding:20px;'><div style='font-size:12px;color:#00e676;font-family:JetBrains Mono,monospace;text-transform:uppercase;margin-bottom:8px;'>✅ Akun Aktif</div><div style='font-size:13px;color:#7a9bbf;'>Sistem V-Guard AI aktif mengawasi bisnis Anda 24/7.</div><div style='margin-top:12px;font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#00e676;'>Live</div></div>", unsafe_allow_html=True)
                else:
                    pay_link = buat_payment_link(pkg, klien.get("Nama Klien","Klien"))
                    st.markdown("<div style='background:#ffab0011;border:1px solid #ffab0033;border-radius:12px;padding:20px;margin-bottom:12px;'><div style='font-size:12px;color:#ffab00;font-family:JetBrains Mono,monospace;text-transform:uppercase;margin-bottom:8px;'>⏳ Menunggu Aktivasi</div><div style='font-size:13px;color:#7a9bbf;margin-bottom:12px;'>Selesaikan pembayaran untuk mengaktifkan akun Anda.</div></div>", unsafe_allow_html=True)
                    st.link_button("📲 Bayar via WhatsApp", pay_link, use_container_width=True)

        with portal_tabs[1]:
            ref_link = buat_referral_link(cid)
            st.markdown("<div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;padding:24px;margin-bottom:16px;'><div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#ffd700;margin-bottom:8px;'>🔗 Link Referral Unik Anda</div><div style='font-size:13px;color:#7a9bbf;margin-bottom:16px;'>Setiap referral yang berhasil aktivasi, Anda mendapatkan <strong style='color:#ffd700;'>komisi 10% dari biaya setup</strong>!</div><div class='ref-link-box'>" + ref_link + "</div><div style='margin-top:12px;font-size:12px;color:#7a9bbf;'>💰 <b>Contoh komisi:</b><br>V-PRO (setup Rp 750.000) → Komisi <b style='color:#ffd700;'>Rp 75.000</b><br>V-ELITE (setup Rp 10.000.000) → Komisi <b style='color:#ffd700;'>Rp 1.000.000</b></div></div>", unsafe_allow_html=True)
            wa_share_txt = urllib.parse.quote("Halo! Saya sudah pakai V-Guard AI untuk keamanan bisnis saya — hasilnya luar biasa!\n\nCoba daftar di sini: " + ref_link)
            st.link_button("📲 Bagikan via WhatsApp","https://wa.me/?text="+wa_share_txt,use_container_width=True)
            my_refs = [r for r in st.session_state.db_referrals if r.get("ref_cid")==cid]
            if my_refs:
                total_komisi = sum(r.get("komisi_10pct",0) for r in my_refs)
                rc1,rc2=st.columns(2)
                rc1.metric("Total Referral",len(my_refs))
                rc2.metric("Total Komisi","Rp {:,.0f}".format(total_komisi))
            else:
                st.info("Belum ada referral. Mulai bagikan link Anda sekarang!")

        with portal_tabs[2]:
            if status=="Aktif":
                d1,d2,d3,d4=st.columns(4)
                d1.metric("VOID Hari Ini","2",delta="▲ dari kemarin",delta_color="inverse")
                d2.metric("Normal","18",delta="✓ Sehat")
                d3.metric("Alert Terkirim","1",delta="via WhatsApp")
                d4.metric("Uptime","99.9%",delta="30 hari terakhir")
                if pkg in ("V-ADVANCE","V-ELITE","V-ULTRA"):
                    df_sample=fetch_pos_data()
                    hasil=scan_fraud_lokal(df_sample)
                    sa,sb,sc2=st.columns(3)
                    sa.metric("VOID Mencurigakan",len(hasil["void"]))
                    sb.metric("Pola Duplikat",len(hasil["fraud"]))
                    sc2.metric("Selisih Saldo",len(hasil["suspicious"]))
                    st.dataframe(df_sample[["ID_Transaksi","Kasir","Jumlah","Status","Waktu"]].head(6),use_container_width=True,hide_index=True)
            else:
                st.info("Dashboard akan tersedia setelah akun Anda diaktifkan.")

        with portal_tabs[3]:
            docs=[("📋","Kontrak Langganan","Dokumen perjanjian layanan","Tersedia"),("🧾","Invoice Terakhir","Invoice "+datetime.date.today().strftime("%B %Y"),"PDF"),("📘","Panduan Onboarding","Langkah aktivasi & setup","Tersedia"),("🔒","Kebijakan Privasi","SLA & data privacy","Tersedia"),("📊","Laporan Bulanan","Laporan AI "+datetime.date.today().strftime("%B %Y"),"PDF" if status=="Aktif" else "Dalam Proses")]
            for icon,name,desc,badge in docs:
                bc="#00e676" if badge in ("Tersedia","PDF") else "#ffab00"
                st.markdown("<div style='background:#101c2e;border:1px solid #1e3352;border-radius:8px;padding:14px 18px;margin-bottom:8px;display:flex;align-items:center;gap:14px;'><span style='font-size:22px;'>"+icon+"</span><div style='flex:1;'><div style='font-size:14px;color:#e8f4ff;font-weight:500;'>"+name+"</div><div style='font-size:12px;color:#7a9bbf;'>"+desc+"</div></div><span style='font-family:JetBrains Mono,monospace;font-size:10px;color:"+bc+";border:1px solid "+bc+"44;background:"+bc+"11;padding:3px 10px;border-radius:20px;'>"+badge+"</span></div>",unsafe_allow_html=True)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        if st.button("Logout Portal", key="portal_logout"):
            st.session_state.client_logged_in=False
            st.session_state.client_data=None
            st.rerun()

    else:
        tab_login, tab_daftar = st.tabs(["🔑 Login Client ID","📝 Ajukan Pembelian Baru"])
        with tab_login:
            _,lc,_=st.columns([1,1.2,1])
            with lc:
                st.markdown("<div class='login-card'>",unsafe_allow_html=True)
                st.markdown("<div style='text-align:center;margin-bottom:20px;'><div style='font-size:36px;'>🔑</div><div style='font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;color:#e8f4ff;'>Login Portal Klien</div><div style='font-size:13px;color:#7a9bbf;margin-top:4px;'>Masukkan Client ID yang diberikan tim V-Guard</div></div>",unsafe_allow_html=True)
                cid_input=st.text_input("Client ID",placeholder="VG-XXXXXX",key="portal_cid")
                if st.button("Masuk ke Portal",type="primary",use_container_width=True,key="btn_portal_login"):
                    found=next((k for k in st.session_state.db_umum if k.get("Client_ID","").upper()==cid_input.strip().upper()),None)
                    if found:
                        st.session_state.client_logged_in=True
                        st.session_state.client_data=found
                        st.rerun()
                    else:
                        st.error("Client ID tidak ditemukan. Hubungi tim V-Guard untuk bantuan.")
                st.markdown("</div>",unsafe_allow_html=True)

        with tab_daftar:
            if st.session_state.get("portal_form_submitted"):
                st.success("✅ Pengajuan diterima! Tim V-Guard akan menghubungi Anda dalam 1×24 jam.")
                if st.button("Ajukan Lagi",key="btn_reset_form"):
                    st.session_state.portal_form_submitted=False
                    st.rerun()
            else:
                _,fc,_=st.columns([0.5,2,0.5])
                with fc:
                    st.markdown("<div class='login-card'>",unsafe_allow_html=True)
                    st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:20px;font-weight:700;color:#00d4ff;margin-bottom:16px;'>📝 Formulir Pendaftaran</div>",unsafe_allow_html=True)
                    nama_klien=st.text_input("Nama Lengkap *",placeholder="Budi Santoso",key="form_nama")
                    nama_usaha=st.text_input("Nama Usaha *",placeholder="Toko Maju Jaya",key="form_usaha")
                    wa_klien=st.text_input("Nomor WhatsApp *",placeholder="08123456789",key="form_wa")
                    paket_form=st.selectbox("Paket yang Diminati *",["V-LITE","V-PRO","V-ADVANCE","V-ELITE","V-ULTRA"],key="form_paket")
                    catatan=st.text_area("Ceritakan singkat bisnis Anda",placeholder="Toko kelontong 2 kasir, omzet ±20jt/bln...",height=80,key="form_catatan")
                    ref_src=st.session_state.get("tracking_ref","")
                    if ref_src:
                        st.markdown("<div style='background:#ffd70011;border:1px solid #ffd70033;border-radius:8px;padding:10px 14px;margin-bottom:12px;font-size:12px;color:#ffd700;'>🔗 Anda mendaftar melalui link referral: <b>"+ref_src+"</b></div>",unsafe_allow_html=True)
                    if st.button("Kirim Pengajuan",type="primary",use_container_width=True,key="btn_submit_form"):
                        if nama_klien and nama_usaha and wa_klien:
                            cid_baru=buat_client_id(nama_klien,wa_klien)
                            pengajuan={"Client_ID":cid_baru,"Nama Klien":nama_klien,"Nama Usaha":nama_usaha,"WhatsApp":wa_klien,"Produk":paket_form,"Status":"Menunggu Pembayaran","Catatan":catatan,"Tanggal":str(datetime.date.today()),"Source":"Portal Klien","Ref":ref_src}
                            st.session_state.db_umum.append(pengajuan)
                            st.session_state.db_pengajuan.append(pengajuan)
                            if ref_src:
                                sfm={"V-LITE":250_000,"V-PRO":750_000,"V-ADVANCE":3_500_000,"V-ELITE":10_000_000,"V-ULTRA":0}
                                sf=sfm.get(paket_form,0)
                                if sf>0: track_referral(ref_src,pengajuan,sf)
                            st.session_state.portal_form_submitted=True
                            st.rerun()
                        else:
                            st.error("Lengkapi semua field yang wajib diisi (*).")
                    st.markdown("</div>",unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

elif menu == "👁️ Visionary CCTV":
    if not st.session_state.authenticated or not st.session_state.admin_logged_in:
        st.error("🔒 Akses ditolak. Login sebagai Admin terlebih dahulu.")
        st.stop()
    menu_visionary()

elif menu == "💰 Treasurer":
    if not st.session_state.authenticated or not st.session_state.admin_logged_in:
        st.error("🔒 Akses ditolak. Login sebagai Admin terlebih dahulu.")
        st.stop()
    menu_treasurer()

elif menu == "🔗 Liaison POS":
    if not st.session_state.authenticated or not st.session_state.admin_logged_in:
        st.error("🔒 Akses ditolak. Login sebagai Admin terlebih dahulu.")
        st.stop()
    menu_liaison()

elif menu == "Investor Area":
    if not st.session_state.authenticated or not st.session_state.investor_pw_ok:
        st.error("🔒 Akses ditolak. Masukkan kode akses investor di sidebar.")
        st.stop()

    st.markdown("<div style='padding:32px 48px;'>", unsafe_allow_html=True)
    st.markdown("<div class='page-title'>📈 Investor <span style='color:#ffd700;'>Area</span></div><div class='page-subtitle'>V-Guard AI — Ekosistem Keamanan Bisnis Digital Indonesia</div>", unsafe_allow_html=True)
    st.markdown("<div style='background:linear-gradient(135deg,#0d1626,#1a1500);border:1px solid #ffd70033;border-radius:14px;padding:24px;margin-bottom:24px;'><div style='font-family:JetBrains Mono,monospace;font-size:10px;color:#ffd700;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;'>CONFIDENTIAL — INVESTOR BRIEF</div><div style='font-family:Rajdhani,sans-serif;font-size:28px;font-weight:700;color:#ffd700;margin-bottom:4px;'>V-Guard AI Intelligence</div><div style='font-size:14px;color:#7a9bbf;'>AI-Powered Business Security Ecosystem · Indonesia Market</div></div>", unsafe_allow_html=True)
    inv_stats=[("TAM","Rp 4,2 Triliun","Total Addressable Market Indonesia"),("ARPU","Rp 650.000","Average Revenue Per User/bulan"),("Churn Target","< 3%","Monthly churn rate target"),("Gross Margin","78%","Target margin produk SaaS"),("CAC","Rp 850.000","Customer Acquisition Cost estimasi"),("LTV","Rp 23,4 Jt","Customer Lifetime Value (36 bln)")]
    cols=st.columns(3)
    for i,(title,val,desc) in enumerate(inv_stats):
        with cols[i%3]:
            st.markdown("<div class='investor-stat'><div class='investor-stat-num'>"+val+"</div><div style='font-family:Rajdhani,sans-serif;font-size:14px;font-weight:700;color:#e8f4ff;margin-top:4px;'>"+title+"</div><div class='investor-stat-lbl'>"+desc+"</div></div>",unsafe_allow_html=True)
            st.markdown("<div style='height:10px;'></div>",unsafe_allow_html=True)
    st.divider()
    inv_tabs=st.tabs(["📊 Proyeksi Keuangan","🗺️ Roadmap","💡 Model Bisnis"])
    with inv_tabs[0]:
        data_proj={"Bulan":["Q1 2026","Q2 2026","Q3 2026","Q4 2026","Q1 2027","Q2 2027"],"Klien":[15,45,120,280,500,900],"MRR (Rp Jt)":[8,28,78,182,325,585],"Net Profit (Rp Jt)":[-5,2,18,52,110,220]}
        st.dataframe(pd.DataFrame(data_proj),use_container_width=True,hide_index=True)
        st.markdown("<div style='background:#101c2e;border:1px solid #1e3352;border-radius:8px;padding:14px 18px;margin-top:12px;font-size:12px;color:#7a9bbf;'>⚠️ Proyeksi berdasarkan asumsi pertumbuhan organik + digital marketing. Angka aktual dapat berbeda.</div>",unsafe_allow_html=True)
    with inv_tabs[1]:
        roadmap=[("Q1 2026","🚀 Launch","Peluncuran V-LITE & V-PRO. Target 50 klien awal.","done"),("Q2 2026","⚡ Growth","Aktivasi V-ADVANCE & V-ELITE. Ekspansi 5 kota.","active"),("Q3 2026","🌐 Scale","Launch V-ULTRA & white-label. Rekrut 10 reseller.","upcoming"),("Q4 2026","🏆 Series A Prep","Konsolidasi data, audit keuangan, pitch Series A.","upcoming"),("2027","🌏 Expansion","Ekspansi ke Malaysia & Philippines. 1.000+ klien.","upcoming")]
        for quarter,title,desc,status_r in roadmap:
            color="#00e676" if status_r=="done" else "#00d4ff" if status_r=="active" else "#7a9bbf"
            st.markdown("<div style='background:#101c2e;border:1px solid #1e3352;border-left:3px solid "+color+";border-radius:8px;padding:16px 20px;margin-bottom:10px;display:flex;align-items:flex-start;gap:16px;'><div style='font-family:JetBrains Mono,monospace;font-size:11px;color:"+color+";min-width:60px;margin-top:2px;'>"+quarter+"</div><div><div style='font-family:Rajdhani,sans-serif;font-size:15px;font-weight:700;color:#e8f4ff;'>"+title+"</div><div style='font-size:13px;color:#7a9bbf;margin-top:4px;'>"+desc+"</div></div></div>",unsafe_allow_html=True)
    with inv_tabs[2]:
        st.markdown("<div style='display:grid;grid-template-columns:1fr 1fr;gap:16px;'><div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;padding:20px;'><div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:#00d4ff;margin-bottom:12px;'>💰 Revenue Streams</div><div style='font-size:13px;color:#7a9bbf;line-height:1.8;'>● Langganan bulanan (SaaS MRR)<br>● Biaya setup & implementasi<br>● White-label licensing (V-ULTRA)<br>● Komisi referral program<br>● API usage fees (enterprise)</div></div><div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;padding:20px;'><div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:#ffd700;margin-bottom:12px;'>🛡️ Keunggulan Kompetitif</div><div style='font-size:13px;color:#7a9bbf;line-height:1.8;'>● AI local-first (bahasa & konteks Indonesia)<br>● 5-tier pricing menjangkau semua segmen<br>● CCTV + Kasir + Bank dalam 1 platform<br>● Plug & Play — tidak butuh IT team<br>● WhatsApp-native alert system</div></div></div>",unsafe_allow_html=True)
    st.divider()
    st.link_button("📲 Jadwalkan Meeting dengan Founder", WA_LINK_KONSUL)
    if st.button("Logout Investor Area",key="inv_logout"):
        st.session_state.investor_pw_ok=False
        st.session_state.authenticated=False
        st.rerun()
    st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("<div style='height:80px;'></div>",unsafe_allow_html=True)

elif menu == "Admin Access":
    if not st.session_state.authenticated or not st.session_state.admin_logged_in:
        st.error("🔒 Akses ditolak. Masukkan kode admin di sidebar.")
        st.stop()

    st.markdown("<div style='padding:32px 48px;'>", unsafe_allow_html=True)
    st.markdown("<div class='page-title'>⚔️ The War Room — <span style='color:#00d4ff;'>Admin Control Center</span></div><div class='page-subtitle'>V-GUARD AI Ecosystem ©2026 — Founder Edition</div>", unsafe_allow_html=True)

    col_logout = st.columns([4,1])[1]
    with col_logout:
        if st.button("Logout",key="logout_main"):
            st.session_state.admin_logged_in=False
            st.session_state.investor_pw_ok=False
            st.session_state.authenticated=False
            st.rerun()

    war_tabs = st.tabs(["📊 Dashboard","🤖 AI Agents","📹 Monitor CCTV","🚨 Fraud Scanner","📋 Pengajuan Masuk","👥 Aktivasi Klien","🔗 Referral Dashboard","⏰ Auto-Billing","🗄️ Database"])

    with war_tabs[0]:
        total_k=len(st.session_state.db_umum)
        aktif_k=sum(1 for k in st.session_state.db_umum if k.get("Status")=="Aktif")
        pending_k=sum(1 for k in st.session_state.db_umum if k.get("Status")=="Menunggu Pembayaran")
        mrr=hitung_proyeksi_omset(st.session_state.db_umum)
        total_ref=len(st.session_state.db_referrals)
        total_kom=sum(r.get("komisi_10pct",0) for r in st.session_state.db_referrals)
        m1,m2,m3,m4,m5,m6=st.columns(6)
        m1.metric("Total Klien",str(total_k))
        m2.metric("Klien Aktif",str(aktif_k))
        m3.metric("Pending",str(pending_k))
        m4.metric("MRR","Rp {:,.0f}".format(mrr))
        m5.metric("Total Referral",str(total_ref))
        m6.metric("Total Komisi","Rp {:,.0f}".format(total_kom))
        st.markdown("<div style='height:16px;'></div>",unsafe_allow_html=True)
        st.markdown("""
        <div class='demo-mockup'>
            <div style='margin-bottom:12px;'><span class='demo-dot demo-red'></span><span class='demo-dot demo-yellow'></span><span class='demo-dot demo-green'></span><span style='margin-left:12px;color:#7a9bbf;font-size:11px;'>v-guard-warroom / system-log</span></div>
            <span style='color:#00e676;'>✓</span> [SYSTEM] V-Guard AI v3.1 — Boot selesai<br>
            <span style='color:#00d4ff;'>▸</span> [SENTINEL] 10 AI Agents terdaftar · 8 Aktif · 2 Standby<br>
            <span style='color:#00e676;'>✓</span> [LIAISON] Fraud scanner lokal aktif — filter anomali only<br>
            <span style='color:#00d4ff;'>▸</span> [CONCIERGE] Chat widget aktif di semua halaman<br>
            <span style='color:#ffab00;'>▸</span> [AUDITOR] Sinkronisasi mutasi bank — jadwal 06:00 WIB<br>
            <span style='color:#00e676;'>✓</span> [WHISPERBOT] WhatsApp gateway — Connected<br>
            <span style='color:#ffd700;'>▸</span> [COLLECTOR] Auto-billing H-7 check — Aktif<br>
            <span style='color:#7a9bbf;'>_</span>
        </div>""", unsafe_allow_html=True)
        dp_log=st.session_state.get("detected_package")
        if dp_log:
            bul,_=HARGA_MAP.get(dp_log,("—","—"))
            st.markdown("<div class='match-banner' style='margin-top:16px;'><div class='match-banner-title'>🎯 Paket Terdeteksi dari Sesi Chat CS</div><div class='match-banner-body'>Cocok: <b>"+dp_log+"</b> — "+bul+"/bln</div></div>",unsafe_allow_html=True)

    with war_tabs[1]:
        st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#e8f4ff;margin-bottom:4px;'>🤖 10 Elite AI Agent Squad</div><div style='font-size:13px;color:#7a9bbf;margin-bottom:20px;'>Status real-time seluruh agen AI dalam ekosistem V-Guard.</div>",unsafe_allow_html=True)
        agent_statuses=["active","active","active","active","active","standby","active","active","standby","active"]
        for row_start in range(0,10,2):
            cols2=st.columns(2)
            for i,col in enumerate(cols2):
                idx=row_start+i
                if idx>=len(AI_AGENTS): break
                agent=AI_AGENTS[idx]
                st_code=agent_statuses[idx]
                cmap={"active":"#00e676","standby":"#ffab00","offline":"#ff3b5c"}
                lmap={"active":"ACTIVE","standby":"STANDBY","offline":"OFFLINE"}
                color=cmap.get(st_code,"#7a9bbf")
                label=lmap.get(st_code,"UNKNOWN")
                ks=st.session_state.agent_kill_switch.get(agent["id"],False)
                with col:
                    cb="agent-card-active" if not ks else "agent-card-offline"
                    sc2="#ff3b5c" if ks else color
                    sl="KILLED" if ks else label
                    st.markdown("<div class='agent-card "+cb+"'><div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;'><div style='display:flex;align-items:center;gap:8px;'><span style='font-size:22px;'>"+agent["icon"]+"</span><div><div style='font-family:Rajdhani,sans-serif;font-size:15px;font-weight:700;color:#e8f4ff;'>Agent #"+str(agent["id"])+" · "+agent["name"]+"</div><div style='font-size:11px;color:#7a9bbf;'>"+agent["role"]+"</div></div></div><span style='font-family:JetBrains Mono,monospace;font-size:9px;color:"+sc2+";border:1px solid "+sc2+"44;background:"+sc2+"11;padding:2px 8px;border-radius:20px;'>"+sl+"</span></div><div style='font-size:12px;color:#7a9bbf;line-height:1.5;'>"+agent["desc"]+"</div></div>",unsafe_allow_html=True)
                    btn_label="🔴 Kill Agent" if not ks else "🟢 Restart Agent"
                    if st.button(btn_label,key="ks_"+str(agent["id"]),use_container_width=True):
                        st.session_state.agent_kill_switch[agent["id"]]=not ks
                        st.rerun()
                    st.markdown("<div style='height:4px;'></div>",unsafe_allow_html=True)

    with war_tabs[2]:
        st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#e8f4ff;margin-bottom:4px;'>📹 Monitor CCTV — Visual Cashier Audit</div><div style='font-size:13px;color:#7a9bbf;margin-bottom:20px;'>Live feed dari kamera klien.</div>",unsafe_allow_html=True)
        cam_locations=["Outlet Sudirman — Kasir 1","Outlet Sudirman — Kasir 2","Resto Central — Kasir Utama","Cabang Tangerang — Pintu Masuk"]
        cam_cols=st.columns(2)
        for i,loc in enumerate(cam_locations):
            with cam_cols[i%2]:
                now_str=datetime.datetime.now().strftime("%H:%M:%S")
                alert_html="<div class='cctv-alert'>⚠ VOID DETECTED</div>" if i==0 else "<div style='position:absolute;top:8px;right:8px;font-family:JetBrains Mono,monospace;font-size:10px;color:#00e676;background:#00000088;padding:4px 8px;border-radius:4px;'>✓ NORMAL</div>"
                st.markdown("<div class='cctv-frame' style='margin-bottom:12px;'><div style='text-align:center;'><div style='font-size:32px;margin-bottom:6px;'>📹</div><div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#1e3352;'>"+loc+"</div><div style='font-size:10px;color:#7a9bbf;margin-top:4px;'>Feed tersedia setelah hardware terpasang</div></div><div class='cctv-overlay'>● REC "+now_str+" · Cam "+str(i+1)+"</div>"+alert_html+"</div>",unsafe_allow_html=True)
        if st.button("🤖 Simulasi Deteksi YOLO (Demo)",key="btn_yolo_demo"):
            demo_frame={"camera_id":"cam_01","timestamp":str(datetime.datetime.now())}
            st.json(process_yolo_cctv_frame(demo_frame))

    with war_tabs[3]:
        st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#e8f4ff;margin-bottom:4px;'>🚨 Fraud Intelligence Scanner</div><div style='font-size:13px;color:#7a9bbf;margin-bottom:16px;'>Filter lokal anomali sebelum dikirim ke API — hemat biaya hingga 80%.</div>",unsafe_allow_html=True)
        df_trx=fetch_pos_data()
        hasil=scan_fraud_lokal(df_trx)
        fs1,fs2,fs3=st.columns(3)
        fs1.metric("VOID / Cancel",len(hasil["void"]),delta="Tidak Wajar" if not hasil["void"].empty else "Aman")
        fs2.metric("Duplikat Kasir",len(hasil["fraud"]),delta="Terdeteksi" if not hasil["fraud"].empty else "Aman")
        fs3.metric("Selisih Saldo",len(hasil["suspicious"]),delta="Anomali" if not hasil["suspicious"].empty else "Aman")
        if st.button("⚡ Jalankan AI Fraud Alarm Check",key="btn_ai_alarm"):
            yolo_results=[process_yolo_cctv_frame({"camera_id":"cam_0"+str(i+1),"timestamp":str(datetime.datetime.now())}) for i in range(2)]
            alarms=check_ai_fraud_alarm(df_trx,yolo_results)
            if alarms:
                st.error("⚠️ "+str(len(alarms))+" alarm fraud terdeteksi!")
                for alarm in alarms:
                    wa_alarm=trigger_alarm(alarm["reason"],alarm["kasir"],alarm["cabang"],alarm["jumlah"])
                    st.markdown("<div style='background:#ff3b5c11;border:1px solid #ff3b5c33;border-radius:8px;padding:12px 16px;margin-bottom:8px;'><b style='color:#ff3b5c;'>⚠ ALARM</b><br>Kasir: "+alarm["kasir"]+" · Cabang: "+alarm["cabang"]+" · Jumlah: Rp {:,.0f}".format(alarm["jumlah"])+"<br>Alasan: "+alarm["reason"]+"</div>",unsafe_allow_html=True)
                    st.link_button("📲 Kirim Alert ke Owner — "+alarm["cabang"],wa_alarm,key="alarm_"+alarm["kasir"]+"_"+alarm["cabang"])
            else:
                st.success("✅ Tidak ada mismatch kasir vs CCTV.")
        tv,tf,ts=st.tabs(["VOID","Duplikat","Selisih"])
        with tv:
            if not hasil["void"].empty:
                st.error("Transaksi VOID mencurigakan!")
                st.dataframe(hasil["void"][["ID_Transaksi","Cabang","Kasir","Jumlah","Waktu"]],use_container_width=True)
                for cab in hasil["void"]["Cabang"].unique():
                    st.link_button("Alert Owner — "+cab,trigger_alarm("VOID Mencurigakan","—",cab,0),key="voidalert_"+cab)
            else:
                st.success("Tidak ada VOID mencurigakan.")
        with tf:
            if not hasil["fraud"].empty:
                st.error("Pola duplikat terdeteksi!")
                st.dataframe(hasil["fraud"][["ID_Transaksi","Cabang","Kasir","Jumlah","selisih_menit"]],use_container_width=True)
            else:
                st.success("Tidak ada pola duplikat.")
        with ts:
            if not hasil["suspicious"].empty:
                st.error("Selisih saldo ditemukan!")
                st.dataframe(hasil["suspicious"][["ID_Transaksi","Cabang","Kasir","Saldo_Fisik","Saldo_Sistem","selisih_saldo"]],use_container_width=True)
            else:
                st.success("Saldo seimbang.")

    with war_tabs[4]:
        pending_list=[k for k in st.session_state.db_umum if k.get("Status")=="Menunggu Pembayaran"]
        if not pending_list:
            st.info("Tidak ada pengajuan pending saat ini.")
        else:
            for i,klien in enumerate(pending_list):
                cid_p=klien.get("Client_ID","—")
                pkg_p=klien.get("Produk","V-LITE")
                hb_p,hs_p=HARGA_MAP.get(pkg_p,("—","—"))
                wa_tgt=klien.get("WhatsApp",WA_NUMBER)
                if not wa_tgt.startswith("62"): wa_tgt="62"+wa_tgt.lstrip("0")
                ref_badge=""
                if klien.get("Ref"):
                    ref_badge="<span style='background:#ffd70011;color:#ffd700;border:1px solid #ffd70044;border-radius:20px;font-size:10px;padding:2px 8px;font-family:JetBrains Mono,monospace;margin-left:8px;'>🔗 Ref: "+klien["Ref"]+"</span>"
                st.markdown("<div class='client-card-pending'><div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;'><div><div style='font-family:Rajdhani,sans-serif;font-size:17px;font-weight:700;color:#e8f4ff;'>"+klien.get("Nama Klien","—")+" — "+klien.get("Nama Usaha","—")+"</div><div style='font-family:JetBrains Mono,monospace;font-size:10px;color:#00d4ff;margin-bottom:4px;'>"+cid_p+" · "+pkg_p+" · "+hb_p+"/bln "+ref_badge+"</div><div style='font-size:12px;color:#7a9bbf;'>WA: "+klien.get("WhatsApp","—")+" · Daftar: "+klien.get("Tanggal","—")+"</div></div><span class='client-badge-pending'>Menunggu Pembayaran</span></div></div>",unsafe_allow_html=True)
                pc1,pc2,pc3=st.columns(3)
                with pc1:
                    st.link_button("💳 Kirim Link Pembayaran",buat_payment_link(pkg_p,klien.get("Nama Klien","Klien")),use_container_width=True,key="pay_"+cid_p+"_"+str(i))
                with pc2:
                    db_idx=next((j for j,k in enumerate(st.session_state.db_umum) if k.get("Client_ID")==cid_p),None)
                    if db_idx is not None:
                        if st.button("✅ Aktivasi Akun",key="aktiv_"+cid_p+"_"+str(i),type="primary",use_container_width=True):
                            st.session_state.db_umum[db_idx]["Status"]="Aktif"
                            for r in st.session_state.db_referrals:
                                if r.get("new_client")==klien.get("Nama Klien") and r.get("status")=="Menunggu Konfirmasi":
                                    r["status"]="Terbayar"
                            st.rerun()
                with pc3:
                    akses_txt=urllib.parse.quote("Halo "+klien.get("Nama Klien","Klien")+",\n\n✅ Akun V-Guard Anda telah AKTIF!\n\n🔑 Client ID: "+cid_p+"\n🔗 Dashboard: "+BASE_APP_URL+"\n📦 Paket: "+pkg_p+"\n\n— Tim V-Guard AI")
                    st.link_button("📲 Kirim Akses Klien","https://wa.me/"+wa_tgt+"?text="+akses_txt,use_container_width=True,key="access_"+cid_p+"_"+str(i))
                st.markdown("<div style='height:8px;'></div>",unsafe_allow_html=True)

    with war_tabs[5]:
        with st.expander("➕ Tambah Klien Manual"):
            ac1,ac2=st.columns(2)
            with ac1:
                new_nama=st.text_input("Nama Klien",key="new_nama")
                new_usaha=st.text_input("Nama Usaha",key="new_usaha")
                new_wa=st.text_input("WhatsApp",key="new_wa")
            with ac2:
                new_produk=st.selectbox("Produk",["V-LITE","V-PRO","V-ADVANCE","V-ELITE","V-ULTRA"],key="new_produk")
                new_status=st.selectbox("Status Awal",["Menunggu Pembayaran","Aktif"],key="new_status")
                new_due=st.date_input("Jatuh Tempo Invoice",key="new_due",value=datetime.date.today()+datetime.timedelta(days=30))
            if st.button("Tambahkan Klien",type="primary",key="btn_add_client"):
                if new_nama and new_wa:
                    cid_new=buat_client_id(new_nama,new_wa)
                    st.session_state.db_umum.append({"Client_ID":cid_new,"Nama Klien":new_nama,"Nama Usaha":new_usaha,"WhatsApp":new_wa,"Produk":new_produk,"Status":new_status,"Tanggal":str(datetime.date.today()),"invoice_due_date":str(new_due),"Source":"Admin Manual"})
                    st.success("Klien ditambahkan! Client ID: "+cid_new)
                    st.rerun()
                else:
                    st.error("Nama dan WhatsApp wajib diisi.")
        if not st.session_state.db_umum:
            st.info("Belum ada klien terdaftar.")
        else:
            for i,klien in enumerate(st.session_state.db_umum):
                if "Client_ID" not in klien:
                    st.session_state.db_umum[i]["Client_ID"]=buat_client_id(klien["Nama Klien"],klien.get("WhatsApp",""))
                cid_c=st.session_state.db_umum[i]["Client_ID"]
                is_aktif=klien.get("Status")=="Aktif"
                hb_c,hs_c=HARGA_MAP.get(klien.get("Produk","V-LITE"),("—","—"))
                cc_cls="client-card-aktif" if is_aktif else "client-card-pending"
                cb_cls="client-badge-aktif" if is_aktif else "client-badge-pending"
                st.markdown("<div class='"+cc_cls+"'><div style='font-family:Rajdhani,sans-serif;font-size:17px;font-weight:700;color:#e8f4ff;'>"+klien.get("Nama Klien","—")+" — "+klien.get("Nama Usaha","-")+"</div><div style='font-family:JetBrains Mono,monospace;font-size:10px;color:#00d4ff;margin-bottom:6px;'>"+cid_c+" · "+klien.get("Produk","V-LITE")+"</div><div style='font-size:12px;color:#7a9bbf;margin-bottom:8px;'>WA: "+klien.get("WhatsApp","-")+" · "+hb_c+"/bln · Setup: "+hs_c+"</div><span class='"+cb_cls+"'>"+("Aktif" if is_aktif else "Menunggu Pembayaran")+"</span></div>",unsafe_allow_html=True)
                wa_tgt2=klien.get("WhatsApp",WA_NUMBER)
                if not wa_tgt2.startswith("62"): wa_tgt2="62"+wa_tgt2.lstrip("0")
                ac1,ac2,ac3,ac4=st.columns(4)
                with ac1:
                    if is_aktif:
                        if st.button("⏸ Deactivate",key="deact_"+str(i),use_container_width=True):
                            st.session_state.db_umum[i]["Status"]="Menunggu Pembayaran"
                            st.rerun()
                    else:
                        if st.button("✅ Activate",key="act_"+str(i),use_container_width=True,type="primary"):
                            st.session_state.db_umum[i]["Status"]="Aktif"
                            st.rerun()
                with ac2:
                    inv_txt=urllib.parse.quote("INVOICE V-GUARD AI\n\nYth. "+klien.get("Nama Klien","")+"Paket: "+klien.get("Produk","")+" Bulanan: "+hb_c+" Setup: "+hs_c+"\n\nTransfer: BCA 3450074658 a/n Erwin Sinaga\n— Tim V-Guard AI")
                    st.link_button("🧾 Invoice","https://wa.me/"+wa_tgt2+"?text="+inv_txt,use_container_width=True,key="inv_"+str(i))
                with ac3:
                    akses_txt2=urllib.parse.quote("Halo "+klien.get("Nama Klien","")+",\n\n✅ Akun V-Guard Anda AKTIF!\n\n🔑 Client ID: "+cid_c+"\n🔗 Portal: "+BASE_APP_URL+"\n📦 Paket: "+klien.get("Produk","")+"\n\n— Tim V-Guard AI")
                    st.link_button("🔑 Kirim Akses","https://wa.me/"+wa_tgt2+"?text="+akses_txt2,use_container_width=True,key="akses_"+str(i))
                with ac4:
                    ref_link3=buat_referral_link(cid_c)
                    ref_txt=urllib.parse.quote("Link referral Anda: "+ref_link3+"\nKomisi 10% dari setiap klien baru yang berhasil!")
                    st.link_button("🔗 Referral","https://wa.me/"+wa_tgt2+"?text="+ref_txt,use_container_width=True,key="ref_"+str(i))
                st.markdown("<div style='height:4px;'></div>",unsafe_allow_html=True)

    with war_tabs[6]:
        db_refs=st.session_state.db_referrals
        rm1,rm2,rm3,rm4=st.columns(4)
        rm1.metric("Total Referral",str(len(db_refs)))
        rm2.metric("Total Komisi","Rp {:,.0f}".format(sum(r.get("komisi_10pct",0) for r in db_refs)))
        rm3.metric("Komisi Pending","Rp {:,.0f}".format(sum(r.get("komisi_10pct",0) for r in db_refs if r.get("status")=="Menunggu Konfirmasi")))
        rm4.metric("Komisi Terbayar","Rp {:,.0f}".format(sum(r.get("komisi_10pct",0) for r in db_refs if r.get("status")=="Terbayar")))
        if not db_refs:
            st.info("Belum ada data referral.")
        else:
            for i,r in enumerate(db_refs):
                is_paid=r.get("status")=="Terbayar"
                st.markdown("<div class='ref-card"+" ref-card-paid" if is_paid else "<div class='ref-card"+"'><div style='display:flex;justify-content:space-between;align-items:flex-start;'><div><div style='font-size:14px;color:#e8f4ff;font-weight:600;'>"+r.get("new_client","—")+" — "+r.get("new_usaha","—")+"</div><div style='font-size:12px;color:#7a9bbf;'>Dari: <b style='color:#00d4ff;'>"+r.get("ref_cid","—")+"</b> · "+r.get("paket","—")+" · Komisi: <b style='color:#ffd700;'>Rp {:,.0f}</b></div>".format(r.get("komisi_10pct",0))+"</div><span class='"+("ref-badge-paid" if is_paid else "ref-badge-pending")+"'>"+r.get("status","—")+"</span></div></div>",unsafe_allow_html=True)
                if not is_paid:
                    if st.button("✅ Tandai Terbayar",key="pay_ref_"+str(i),use_container_width=False):
                        st.session_state.db_referrals[i]["status"]="Terbayar"
                        st.rerun()
            st.divider()
            df_refs=pd.DataFrame(db_refs)
            st.download_button("⬇️ Download Referral CSV",data=df_refs.to_csv(index=False).encode("utf-8"),file_name="vguard_referrals_"+str(datetime.date.today())+".csv",mime="text/csv")

    with war_tabs[7]:
        reminders=check_autobilling_reminders(st.session_state.db_umum)
        if reminders:
            st.warning("⚠️ "+str(len(reminders))+" klien mendekati jatuh tempo invoice!")
            for rem in reminders:
                color="#ff3b5c" if rem["delta"]==1 else "#ffab00"
                label="H-1 🚨 BESOK JATUH TEMPO" if rem["delta"]==1 else "H-7 Akan jatuh tempo"
                wa_rem=rem["wa"]
                if wa_rem and not wa_rem.startswith("62"): wa_rem="62"+wa_rem.lstrip("0")
                due_info="BESOK!" if rem["delta"]==1 else "dalam "+str(rem["delta"])+" hari"
                msg_rem=urllib.parse.quote(("🚨 URGENT — " if rem["delta"]==1 else "⏰ ")+"PENGINGAT INVOICE V-GUARD AI\n\nYth. "+rem["nama"]+",\n\nInvoice paket "+rem["paket"]+" Anda jatuh tempo "+rem["due"]+" ("+due_info+").\n\nTransfer: BCA 3450074658 a/n Erwin Sinaga\n— Tim V-Guard AI")
                st.markdown("<div style='background:#101c2e;border:1px solid "+color+"44;border-left:3px solid "+color+";border-radius:8px;padding:14px 18px;margin-bottom:10px;'><div style='font-family:Rajdhani,sans-serif;font-size:15px;font-weight:700;color:"+color+";margin-bottom:4px;'>"+label+"</div><div style='font-size:13px;color:#e8f4ff;'>"+rem["nama"]+" — "+rem["usaha"]+"</div><div style='font-size:12px;color:#7a9bbf;'>Paket: "+rem["paket"]+" · Due: "+rem["due"]+"</div></div>",unsafe_allow_html=True)
                if wa_rem:
                    st.link_button("📲 Kirim Reminder ke "+rem["nama"],"https://wa.me/"+wa_rem+"?text="+msg_rem,key="rem_"+rem["cid"])
        else:
            st.success("✅ Tidak ada invoice yang mendekati jatuh tempo saat ini.")

    with war_tabs[8]:
        if st.session_state.db_umum:
            df_db=pd.DataFrame(st.session_state.db_umum)
            if "Client_ID" in df_db.columns:
                df_db["Dashboard_Link"]=df_db["Client_ID"].apply(buat_dashboard_link)
                df_db["Referral_Link"]=df_db["Client_ID"].apply(buat_referral_link)
            st.dataframe(df_db,use_container_width=True,hide_index=True)
            st.download_button("⬇️ Download CSV Klien",data=df_db.to_csv(index=False).encode("utf-8"),file_name="vguard_clients_"+str(datetime.date.today())+".csv",mime="text/csv")
            if st.button("🗑️ Reset Semua Data",key="btn_reset_db"):
                st.session_state.db_umum=[]
                st.session_state.db_pengajuan=[]
                st.session_state.db_referrals=[]
                st.rerun()
        else:
            st.info("Database masih kosong.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

# =============================================================================
# 21. FOOTER
# =============================================================================
st.markdown(
    "<div style='background:#060b14;border-top:1px solid #1e3352;padding:28px 48px;"
    "display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;'>"
    "<div><span style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#00d4ff;'>"
    "V-Guard AI Intelligence</span>"
    "<span style='color:#7a9bbf;font-size:12px;margin-left:12px;'>V-GUARD AI Ecosystem ©2026</span></div>"
    "<div style='font-size:12px;color:#7a9bbf;'>Digitizing Trust · Eliminating Leakage · Protecting Every Rupiah</div></div>",
    unsafe_allow_html=True,
)
