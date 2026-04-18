# =============================================================================
# V-GUARD AI INTELLIGENCE — app.py  (V-GUARD AI Ecosystem ©2026)
# Full Rewrite v2.1 — Professional SaaS Edition
# Changelog v2.1:
#   - Admin/Investor menu diprivatisasi (hanya muncul saat authenticated)
#   - The Concierge Chat widget fully functional (z-index fixed, event listeners fixed)
#   - fetch_pos_data() stub + YOLO integration module
#   - AI Fraud Alarm komparasi kasir vs CCTV
#   - Auto-Billing H-7 reminder
#   - Referral link per klien + komisi 10%
#   - Admin Referral Dashboard (daftar referral, status, kalkulasi komisi)
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
    "authenticated":        False,   # Admin/Investor gate
    "admin_logged_in":      False,
    "investor_pw_ok":       False,
    "db_umum":              [],      # list of client dicts
    "db_pengajuan":         [],      # list of pending orders from portal
    "db_referrals":         [],      # list of referral tracking dicts
    "api_cost_total":       0.0,
    "cs_chat_history":      [],
    "agent_kill_switch":    {},
    "detected_package":     None,
    "pending_quick":        None,
    "client_logged_in":     False,
    "client_data":          None,
    "agent_logs":           [],
    "fraud_scan_results":   None,
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

KOMISI_RATE = 0.10  # 10%

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
    return BASE_APP_URL + "/?ref=" + cid + "&source=referral"

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
# 9. INTEGRATION STUBS — POS & YOLO CCTV
# =============================================================================

def fetch_pos_data(api_url: str = "http://localhost:8080/api/transactions", api_key: str = "") -> pd.DataFrame:
    """
    Fetch real-time POS (Point-of-Sale) transaction data from local kasir server.

    Integration Guide:
    ------------------
    1. Set `api_url` to your local kasir API endpoint.
       Example: "http://192.168.1.100:8080/api/transactions?limit=50"
    2. Pass `api_key` if your kasir server requires authentication.
       The key will be sent as Bearer token in the Authorization header.
    3. Response format expected (JSON array):
       [
         {
           "id": "TRX-001",
           "branch": "Outlet A",
           "cashier": "Budi",
           "amount": 150000,
           "timestamp": "2026-04-18T10:00:00",
           "status": "NORMAL",
           "physical_balance": 150000,
           "system_balance": 150000
         },
         ...
       ]
    4. On production: replace the stub below with actual requests.get() call.

    Returns:
        pd.DataFrame with columns matching get_sample_transaksi() schema.
    """
    # ── STUB: return sample data ──────────────────────────────────────────────
    # TODO (production): uncomment and configure below:
    #
    # import requests
    # headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    # try:
    #     resp = requests.get(api_url, headers=headers, timeout=5)
    #     resp.raise_for_status()
    #     raw = resp.json()
    #     df = pd.DataFrame(raw)
    #     df.rename(columns={
    #         "id": "ID_Transaksi", "branch": "Cabang", "cashier": "Kasir",
    #         "amount": "Jumlah", "timestamp": "Waktu", "status": "Status",
    #         "physical_balance": "Saldo_Fisik", "system_balance": "Saldo_Sistem"
    #     }, inplace=True)
    #     df["Waktu"] = pd.to_datetime(df["Waktu"])
    #     return df
    # except Exception as e:
    #     st.warning(f"Gagal terhubung ke server kasir: {e}")
    #     return get_sample_transaksi()  # fallback
    # ─────────────────────────────────────────────────────────────────────────
    return get_sample_transaksi()


def process_yolo_cctv_frame(frame_data: dict) -> dict:
    """
    Process a single CCTV frame through YOLO object detection.

    Integration Guide:
    ------------------
    1. Install: pip install ultralytics opencv-python
    2. Place model at: models/vguard_yolo.pt
       (Fine-tuned on suspicious behavior: item concealment, unscanned items, etc.)
    3. Send frames via websocket or HTTP POST from CCTV DVR to this function.

    frame_data expected keys:
        - "frame_b64": base64-encoded JPEG frame string
        - "camera_id": str (e.g. "cam_01")
        - "timestamp": ISO timestamp string

    Returns dict with:
        - "camera_id": str
        - "timestamp": str
        - "detections": list of {"label": str, "confidence": float, "bbox": [x,y,w,h]}
        - "alert": bool — True if suspicious behavior detected
        - "alert_reason": str
    """
    # ── STUB ──────────────────────────────────────────────────────────────────
    # TODO (production):
    #
    # import cv2, base64, numpy as np
    # from ultralytics import YOLO
    # model = YOLO("models/vguard_yolo.pt")
    #
    # img_bytes = base64.b64decode(frame_data["frame_b64"])
    # np_arr = np.frombuffer(img_bytes, np.uint8)
    # frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    # results = model(frame, conf=0.45)
    # detections = []
    # alert = False
    # alert_reason = ""
    # SUSPICIOUS_LABELS = {"unscanned_item", "item_concealment", "cash_swap", "void_gesture"}
    # for r in results:
    #     for box in r.boxes:
    #         label = model.names[int(box.cls)]
    #         conf  = float(box.conf)
    #         bbox  = box.xywh[0].tolist()
    #         detections.append({"label": label, "confidence": conf, "bbox": bbox})
    #         if label in SUSPICIOUS_LABELS and conf > 0.6:
    #             alert = True
    #             alert_reason = f"Terdeteksi: {label} (conf={conf:.2f}) di {frame_data['camera_id']}"
    # return {"camera_id": frame_data["camera_id"], "timestamp": frame_data["timestamp"],
    #         "detections": detections, "alert": alert, "alert_reason": alert_reason}
    # ─────────────────────────────────────────────────────────────────────────
    return {
        "camera_id": frame_data.get("camera_id", "cam_01"),
        "timestamp": frame_data.get("timestamp", str(datetime.datetime.now())),
        "detections": [{"label": "person", "confidence": 0.95, "bbox": [100,50,200,400]}],
        "alert": False,
        "alert_reason": "",
    }


def trigger_alarm(reason: str, kasir: str, cabang: str, amount: float, wa_owner: str = WA_NUMBER):
    """
    Trigger a WhatsApp fraud alarm to the business owner.

    Called when:
    - AI Fraud Alarm: mismatch between kasir data and CCTV detection
    - VOID pattern detected
    - Saldo selisih > threshold

    In production, integrate with WhatsApp Business API or Fonnte/WA Gateway.
    Here we generate a pre-filled WA link as action button.
    """
    msg = (
        f"🚨 *ALERT V-GUARD AI*\n\n"
        f"📍 Cabang: {cabang}\n"
        f"👤 Kasir: {kasir}\n"
        f"💰 Jumlah: Rp {amount:,.0f}\n"
        f"⚠️ Alasan: {reason}\n"
        f"🕐 Waktu: {datetime.datetime.now().strftime('%H:%M:%S WIB')}\n\n"
        f"Segera cek rekaman CCTV & laporan kasir.\n— Sentinel AI V-Guard"
    )
    wa_link = f"https://wa.me/{wa_owner}?text=" + urllib.parse.quote(msg)
    return wa_link


def check_ai_fraud_alarm(pos_df: pd.DataFrame, yolo_results: list) -> list:
    """
    Compare POS kasir data with YOLO CCTV detections to identify mismatches.

    Logic:
    - If YOLO detects 'unscanned_item' or 'item_concealment' at a timestamp
      where the kasir shows VOID or zero transaction → HIGH RISK fraud flag.
    - Returns list of alarm dicts.

    In production, correlate by camera_id → branch → cashier.
    """
    alarms = []
    void_rows = pos_df[pos_df["Status"] == "VOID"]
    for _, row in void_rows.iterrows():
        for yolo in yolo_results:
            if yolo.get("alert"):
                alarms.append({
                    "kasir":    row["Kasir"],
                    "cabang":   row["Cabang"],
                    "jumlah":   row["Jumlah"],
                    "reason":   f"VOID + CCTV: {yolo['alert_reason']}",
                    "camera_id":yolo["camera_id"],
                })
    return alarms


def check_autobilling_reminders(db_klien: list) -> list:
    """
    Check clients with invoices due in 7 days (H-7) and 1 day (H-1).
    Returns list of reminder dicts for admin action.

    In production:
    - Store invoice_due_date per client in db_umum.
    - Run this check daily via cron/scheduler.
    - Automatically send WA message via Fonnte or WA Business API.
    """
    today = datetime.date.today()
    reminders = []
    for k in db_klien:
        due_str = k.get("invoice_due_date", "")
        if not due_str:
            continue
        try:
            due_date = datetime.date.fromisoformat(due_str)
            delta = (due_date - today).days
            if delta in (7, 1):
                reminders.append({
                    "nama":    k.get("Nama Klien","—"),
                    "usaha":   k.get("Nama Usaha","—"),
                    "wa":      k.get("WhatsApp",""),
                    "paket":   k.get("Produk","V-LITE"),
                    "due":     due_str,
                    "delta":   delta,
                    "cid":     k.get("Client_ID","—"),
                })
        except Exception:
            pass
    return reminders


def track_referral(ref_cid: str, new_client_data: dict, setup_amount: int):
    """
    Log a referral conversion and calculate 10% commission on setup fee.
    Appends to st.session_state.db_referrals.
    """
    commission = int(setup_amount * KOMISI_RATE)
    entry = {
        "ref_cid":      ref_cid,
        "new_client":   new_client_data.get("Nama Klien","—"),
        "new_usaha":    new_client_data.get("Nama Usaha","—"),
        "paket":        new_client_data.get("Produk","V-LITE"),
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
            base = "Tentu! Sebelum saya rekomendasikan, boleh saya tahu dulu — **jenis usaha apa** dan berapa **kasir atau cabang** Bapak/Ibu? 😊"
        elif any(k in m for k in ["cctv","kamera","pantau","monitor","visual"]):
            base = "Untuk kebutuhan **monitoring & CCTV AI**, saya rekomendasikan **V-PRO** 📹\n\n✅ CCTV AI — teks transaksi tampil di rekaman\n✅ Audit bank otomatis · **Plug & Play** tanpa teknisi"
            if not pkg: base += build_package_cta("V-PRO")
        elif any(k in m for k in ["fraud","curang","kecurangan","void mencurigakan","kasir curang"]):
            base = "Untuk **deteksi fraud kasir**, solusi terbaik adalah **V-ELITE** 🛡️\n\n✅ Deep Learning Forensik · Private Server · SLA 99.9%"
            if not pkg: base += build_package_cta("V-ELITE")
        elif any(k in m for k in ["apa itu","v-guard","vguard","tentang"]):
            base = "**V-Guard AI Intelligence** adalah sistem keamanan bisnis berbasis AI yang mengawasi kasir, stok, dan rekening bank Anda 24/7 🏆\n\n- Cegah kebocoran hingga **88%**\n- Deteksi anomali **< 5 detik**\n- ROI rata-rata **400–900%/bulan**\n\nBoleh ceritakan bisnis Bapak/Ibu? 🙏"
        elif any(k in m for k in ["roi","hemat","bocor","rugi","omzet"]):
            base = "Rata-rata bisnis kehilangan **3–15% omzet** per bulan tanpa disadari. V-Guard AI mencegah hingga **88% kebocoran** otomatis.\n\nBoleh share **omzet bulanan** bisnis Bapak/Ibu? 😊"
        elif any(k in m for k in ["book demo","demo","coba"]):
            base = f"Demo V-Guard **gratis 30 menit** — Pak Erwin langsung tunjukkan cara sistem mendeteksi kecurangan secara real-time.\n\n📲 [Book Demo Gratis]({WA_LINK_DEMO})"
        elif any(k in m for k in ["daftar","order","beli","aktivasi","mulai"]):
            base = "Siap! Untuk memulai, Bapak/Ibu bisa pilih paket yang sesuai:\n\n🔵 V-LITE (Rp 150rb) · ⚡ V-PRO (Rp 450rb) · 🟣 V-ADVANCE (Rp 1,2jt)\n🟢 V-ELITE (Rp 3,5jt) · 👑 V-ULTRA (Custom)\n\nBoleh saya tahu jenis usaha Bapak/Ibu agar saya pilihkan yang paling tepat? 😊"
        elif any(k in m for k in ["referral","komisi","ajak","teman"]):
            base = "Program Referral V-Guard memberikan **komisi 10%** dari biaya setup klien baru yang Anda referensikan! 💰\n\nDaftarkan bisnis Anda dulu di Portal Klien, lalu dapatkan link referral unik Anda. Bagikan ke rekan bisnis & komisi masuk otomatis!"
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

/* ── FLOATING CHAT WIDGET — z-index fixed, pointer-events ensured ── */
#vg-fab {
    position: fixed !important;
    bottom: 24px !important;
    right: 24px !important;
    width: 60px !important;
    height: 60px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #0091ff, #00d4ff) !important;
    border: none !important;
    cursor: pointer !important;
    z-index: 2147483647 !important;   /* max possible z-index */
    box-shadow: 0 4px 24px #00d4ff55 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 26px !important;
    transition: transform .2s ease, box-shadow .2s ease !important;
    animation: vgFloat 3s ease-in-out infinite !important;
    pointer-events: auto !important;
    outline: none !important;
    -webkit-tap-highlight-color: transparent !important;
}
#vg-fab:hover  { transform: scale(1.12) !important; box-shadow: 0 6px 32px #00d4ff77 !important; }
#vg-fab:active { transform: scale(0.96) !important; }
@keyframes vgFloat {
    0%,100% { transform: translateY(0px); }
    50%      { transform: translateY(-7px); }
}
#vg-fab:hover { animation: none !important; }

#vg-notif {
    position: absolute !important;
    top: 2px !important;
    right: 2px !important;
    width: 14px !important;
    height: 14px !important;
    background: #ff3b5c !important;
    border-radius: 50% !important;
    border: 2px solid #060b14 !important;
    pointer-events: none !important;
    animation: vgPulse 1.5s ease infinite !important;
}
@keyframes vgPulse { 0%,100%{opacity:1;} 50%{opacity:.4;} }

#vg-chatbox {
    position: fixed !important;
    bottom: 100px !important;
    right: 24px !important;
    width: 360px !important;
    height: 520px !important;
    background: #0d1626 !important;
    border: 1px solid #1e3352 !important;
    border-radius: 18px !important;
    display: none !important;
    flex-direction: column !important;
    box-shadow: 0 12px 48px #00000088 !important;
    overflow: hidden !important;
    z-index: 2147483646 !important;
    pointer-events: auto !important;
    transition: opacity .25s ease, transform .25s ease !important;
    transform-origin: bottom right !important;
}
#vg-chatbox.vg-open {
    display: flex !important;
    opacity: 1 !important;
    transform: scale(1) !important;
}

#vg-header {
    background: linear-gradient(135deg, #060b14, #0a1628);
    border-bottom: 1px solid #1e3352;
    padding: 13px 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
    user-select: none;
}
#vg-msgs {
    flex: 1;
    overflow-y: auto;
    padding: 14px 12px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    scroll-behavior: smooth;
}
#vg-msgs::-webkit-scrollbar{width:4px;}
#vg-msgs::-webkit-scrollbar-track{background:transparent;}
#vg-msgs::-webkit-scrollbar-thumb{background:#1e3352;border-radius:2px;}

.vg-bot { background:#101c2e; border:1px solid #1e3352; border-radius:14px 14px 14px 4px; padding:10px 14px; font-size:13px; line-height:1.65; color:#e8f4ff; max-width:92%; align-self:flex-start; }
.vg-usr { background:linear-gradient(135deg,#0091ff,#00d4ff); border-radius:14px 14px 4px 14px; padding:10px 14px; font-size:13px; line-height:1.65; color:#000; font-weight:600; max-width:86%; align-self:flex-end; }

.vg-typing { display:flex; gap:5px; padding:4px 2px; align-items:center; }
.vg-typing span { width:8px; height:8px; background:#00d4ff; border-radius:50%; display:inline-block; animation:vgDot 1.3s infinite ease; }
.vg-typing span:nth-child(2){animation-delay:.18s;}
.vg-typing span:nth-child(3){animation-delay:.36s;}
@keyframes vgDot { 0%,80%,100%{opacity:.25;transform:scale(.8);} 40%{opacity:1;transform:scale(1);} }

#vg-pills {
    padding: 8px 12px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    border-top: 1px solid #1e3352;
    flex-shrink: 0;
    background: #0d1626;
}
.vg-pill {
    background: #101c2e;
    border: 1px solid #1e3352;
    color: #7a9bbf;
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 20px;
    cursor: pointer;
    transition: all .18s;
    white-space: nowrap;
    user-select: none;
    -webkit-tap-highlight-color: transparent;
}
.vg-pill:hover  { border-color:#00d4ff; color:#00d4ff; background:#00d4ff11; }
.vg-pill:active { background:#00d4ff22; }

#vg-inputrow {
    display: flex;
    gap: 8px;
    padding: 10px 12px;
    border-top: 1px solid #1e3352;
    background: #060b14;
    flex-shrink: 0;
    align-items: flex-end;
}
#vg-input {
    flex: 1;
    background: #101c2e;
    border: 1px solid #1e3352;
    border-radius: 10px;
    padding: 9px 12px;
    font-size: 13px;
    color: #e8f4ff;
    outline: none;
    font-family: 'Inter', sans-serif;
    resize: none;
    max-height: 90px;
    min-height: 38px;
    line-height: 1.5;
    transition: border-color .18s;
}
#vg-input:focus { border-color: #00d4ff; box-shadow: 0 0 8px #00d4ff22; }
#vg-input::placeholder { color: #4a6a8a; }
#vg-send {
    background: linear-gradient(135deg, #0091ff, #00d4ff);
    border: none;
    border-radius: 10px;
    width: 40px;
    height: 40px;
    cursor: pointer;
    color: #000;
    font-size: 17px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform .15s, box-shadow .15s;
    flex-shrink: 0;
    outline: none;
    -webkit-tap-highlight-color: transparent;
}
#vg-send:hover  { transform: scale(1.08); box-shadow: 0 2px 14px #00d4ff44; }
#vg-send:active { transform: scale(0.94); }

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
.status-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--success);margin-right:6px;animation:vgPulse 2s infinite;}

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
.agent-card-offline{border-left:3px solid #ff3b5c;}

/* ── CCTV MONITOR ── */
.cctv-frame{background:#000;border:2px solid #1e3352;border-radius:8px;aspect-ratio:16/9;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;}
.cctv-overlay{position:absolute;top:8px;left:8px;font-family:'JetBrains Mono',monospace;font-size:10px;color:#00e676;background:#00000088;padding:4px 8px;border-radius:4px;}
.cctv-alert{position:absolute;top:8px;right:8px;font-family:'JetBrains Mono',monospace;font-size:10px;color:#ff3b5c;background:#00000088;padding:4px 8px;border-radius:4px;animation:vgPulse 1s infinite;}

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

/* ── REFERRAL CARDS ── */
.ref-card{background:#101c2e;border:1px solid #1e3352;border-radius:10px;padding:16px 20px;margin-bottom:10px;border-left:3px solid #ffd700;}
.ref-card-paid{border-left-color:#00e676;}
.ref-badge-pending{display:inline-block;background:#ffd70018;color:#ffd700!important;border:1px solid #ffd70044;border-radius:20px;font-size:10px!important;padding:2px 10px;font-family:'JetBrains Mono',monospace!important;}
.ref-badge-paid{display:inline-block;background:#00e67618;color:#00e676!important;border:1px solid #00e67644;border-radius:20px;font-size:10px!important;padding:2px 10px;font-family:'JetBrains Mono',monospace!important;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 12. THE CONCIERGE CHAT WIDGET — Fully Functional, Fixed z-index & Events
# =============================================================================
CHAT_WIDGET_HTML = """
<div id="vg-fab" role="button" aria-label="Chat dengan Sentinel CS" tabindex="0">
    🛡️
    <div id="vg-notif"></div>
</div>

<div id="vg-chatbox" role="dialog" aria-label="Sentinel CS Chat">
    <!-- Header -->
    <div id="vg-header">
        <div style="width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,#0091ff,#00d4ff);
                    display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;">🛡️</div>
        <div style="flex:1;min-width:0;">
            <div style="font-family:'Rajdhani',sans-serif;font-size:15px;font-weight:700;color:#e8f4ff;">Sentinel CS</div>
            <div style="font-size:10px;color:#00e676;font-family:'JetBrains Mono',monospace;">
                <span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#00e676;
                             margin-right:5px;animation:vgPulse 2s infinite;"></span>Online · Siap membantu
            </div>
        </div>
        <button id="vg-close" aria-label="Tutup chat"
                style="background:transparent;border:none;color:#7a9bbf;font-size:20px;
                       cursor:pointer;padding:4px 6px;line-height:1;border-radius:6px;
                       transition:color .15s;outline:none;">✕</button>
    </div>

    <!-- Messages -->
    <div id="vg-msgs">
        <div class="vg-bot">
            Halo! 👋 Saya <strong>Sentinel CS</strong>, konsultan AI V-Guard.<br><br>
            Ceritakan bisnis Bapak/Ibu — berapa <strong>kasir atau cabang</strong>
            dan <strong>omzet bulanan</strong> Anda?<br><br>
            Saya langsung hitung potensi kebocoran &amp; rekomendasikan paket terbaik 💡
        </div>
    </div>

    <!-- Quick Pills -->
    <div id="vg-pills">
        <span class="vg-pill" data-msg="Apa itu V-Guard?">🛡️ Tentang V-Guard</span>
        <span class="vg-pill" data-msg="Lihat semua paket dan harga">📦 Lihat Paket</span>
        <span class="vg-pill" data-msg="Saya punya warung 1 kasir">🏪 Usaha Kecil</span>
        <span class="vg-pill" data-msg="Saya khawatir kasir curang, apa solusinya?">🔍 Deteksi Fraud</span>
        <span class="vg-pill" data-msg="Hitung ROI untuk omzet 50 juta per bulan">💰 Hitung ROI</span>
        <span class="vg-pill" data-msg="Saya ingin book demo gratis">🎯 Book Demo</span>
        <span class="vg-pill" data-msg="Bagaimana program referral dan komisi?">🔗 Referral</span>
    </div>

    <!-- Input Row -->
    <div id="vg-inputrow">
        <textarea id="vg-input" rows="1" placeholder="Ceritakan bisnis Anda..."></textarea>
        <button id="vg-send" aria-label="Kirim pesan">➤</button>
    </div>
</div>

<script>
(function() {
    'use strict';

    /* ── State ── */
    var isOpen    = false;
    var isBusy    = false;
    var history   = [];

    /* ── Elements ── */
    var fab      = document.getElementById('vg-fab');
    var chatbox  = document.getElementById('vg-chatbox');
    var notif    = document.getElementById('vg-notif');
    var closeBtn = document.getElementById('vg-close');
    var msgs     = document.getElementById('vg-msgs');
    var input    = document.getElementById('vg-input');
    var sendBtn  = document.getElementById('vg-send');
    var pills    = document.querySelectorAll('.vg-pill');

    /* ── Guard: abort if elements missing (e.g. re-render) ── */
    if (!fab || !chatbox) return;

    /* ── Toggle ── */
    function openChat() {
        isOpen = true;
        chatbox.classList.add('vg-open');
        notif.style.display = 'none';
        fab.style.animation = 'none';
        scrollBottom();
        setTimeout(function(){ input.focus(); }, 180);
    }
    function closeChat() {
        isOpen = false;
        chatbox.classList.remove('vg-open');
        fab.style.animation = '';
    }
    function toggleChat() { if (isOpen) closeChat(); else openChat(); }

    /* ── Scroll ── */
    function scrollBottom() {
        msgs.scrollTop = msgs.scrollHeight;
    }

    /* ── Add bubble ── */
    function addBubble(html, isUser) {
        var div = document.createElement('div');
        div.className = isUser ? 'vg-usr' : 'vg-bot';
        div.innerHTML = html;
        msgs.appendChild(div);
        scrollBottom();
        return div;
    }

    /* ── Typing indicator ── */
    function showTyping() {
        var div = document.createElement('div');
        div.className = 'vg-bot';
        div.id = 'vg-typing';
        div.innerHTML = '<div class="vg-typing"><span></span><span></span><span></span></div>';
        msgs.appendChild(div);
        scrollBottom();
    }
    function removeTyping() {
        var t = document.getElementById('vg-typing');
        if (t) t.remove();
    }

    /* ── Fallback rules ── */
    var rules = [
        { keys:['warung','1 kasir','kios','lapak','usaha kecil','kecil'],
          reply:'Untuk usaha skala ini, saya rekomendasikan <strong>V-LITE</strong> (Rp 150.000/bln). Plug &amp; Play — aktif dalam menit tanpa teknisi! 🔵<br><br>💡 Mau saya bantu hitung estimasi kebocoran bulanan Bapak/Ibu?' },
        { keys:['cafe','kafe','resto','restoran','pantau','monitor','cctv','kamera','visual'],
          reply:'Untuk pantau toko &amp; CCTV AI, saya rekomendasikan <strong>V-PRO</strong> (Rp 450.000/bln). Termasuk audit bank otomatis &amp; laporan PDF harian! ⚡<br><br>Berapa cabang yang Bapak/Ibu kelola saat ini?' },
        { keys:['cabang','multi','minimarket','supermarket','franchise','stok','banyak kasir'],
          reply:'Untuk multi-cabang &amp; manajemen stok, <strong>V-ADVANCE</strong> adalah solusinya (Rp 1.200.000/bln). CCTV AI + Alarm Fraud WhatsApp otomatis! 🟣<br><br>Berapa total kasir Bapak/Ibu?' },
        { keys:['fraud','curang','kecurangan','void mencurigakan','kasir curang','deteksi fraud'],
          reply:'Untuk deteksi fraud kasir level enterprise, saya rekomendasikan <strong>V-ELITE</strong>. Deep Learning Forensik + Private Server + SLA 99.9% 🟢<br><br>Mau saya jadwalkan demo langsung dengan Pak Erwin?' },
        { keys:['enterprise','korporasi','white label','rebranding','lisensi'],
          reply:'Untuk kebutuhan enterprise &amp; white-label, <strong>V-ULTRA</strong> adalah pilihan terbaik. 10 Elite AI Squad + Custom Platform. 👑<br><br>Boleh saya hubungkan langsung dengan Founder kami untuk konsultasi strategis?' },
        { keys:['harga','biaya','berapa','tarif'],
          reply:'Tentu! Sebelum saya rekomendasikan paket yang tepat, boleh saya tahu dulu:<br><br>• <strong>Jenis usaha</strong> apa yang Bapak/Ibu kelola?<br>• Berapa <strong>kasir atau cabang</strong>?<br><br>Dengan info itu, saya langsung rekomendasikan yang paling sesuai 😊' },
        { keys:['semua paket','lihat paket','daftar paket'],
          reply:'V-Guard tersedia dalam 5 tier:<br><br>🔵 <strong>V-LITE</strong> — Rp 150rb/bln · 1 kasir<br>⚡ <strong>V-PRO</strong> — Rp 450rb/bln · CCTV AI<br>🟣 <strong>V-ADVANCE</strong> — Rp 1,2jt/bln · Multi-cabang<br>🟢 <strong>V-ELITE</strong> — Rp 3,5jt/bln · Enterprise<br>👑 <strong>V-ULTRA</strong> — Custom · White Label<br><br>Ceritakan bisnis Anda dan saya pilihkan yang paling cocok 😊' },
        { keys:['demo','coba','book demo','gratis'],
          reply:'Demo V-Guard <strong>GRATIS 30 menit</strong> — Pak Erwin langsung tunjukkan cara sistem mendeteksi kecurangan secara real-time!<br><br>📲 <a href="https://wa.me/6282122190885?text=Halo+Pak+Erwin%2C+saya+ingin+Book+Demo+V-Guard+AI." target="_blank" style="color:#00d4ff;text-decoration:underline;">Klik di sini untuk Book Demo</a>' },
        { keys:['roi','hemat','bocor','omzet','rugi'],
          reply:'Rata-rata bisnis kehilangan <strong>3–15% omzet</strong> setiap bulan tanpa disadari. V-Guard AI mencegah hingga <strong>88% kebocoran</strong> secara otomatis.<br><br>Boleh share omzet bulanan bisnis Bapak/Ibu? Saya hitung ROI-nya sekarang! 💡' },
        { keys:['apa itu','v-guard','vguard','tentang','fungsi'],
          reply:'<strong>V-Guard AI Intelligence</strong> adalah sistem keamanan bisnis berbasis AI yang bekerja 24/7 mengawasi setiap Rupiah di kasir, stok &amp; rekening bank Anda 🏆<br><br>• Cegah kebocoran hingga <strong>88%</strong><br>• Deteksi anomali &lt; 5 detik<br>• ROI rata-rata <strong>400–900%/bulan</strong><br><br>Boleh ceritakan bisnis Bapak/Ibu? 🙏' },
        { keys:['referral','komisi','ajak','teman','affiliate'],
          reply:'Program Referral V-Guard memberikan <strong>komisi 10%</strong> dari biaya setup klien baru yang Anda referensikan! 💰<br><br>Daftarkan bisnis Anda dulu di Portal Klien, lalu dapatkan <strong>link referral unik</strong> Anda. Bagikan ke rekan bisnis &amp; komisi masuk otomatis!<br><br>Mau saya bantu daftarkan bisnis Anda sekarang?' },
        { keys:['daftar','order','beli','aktivasi','mulai','gabung'],
          reply:'Siap! Untuk memulai, Bapak/Ibu bisa pilih paket yang sesuai kebutuhan:<br><br>🔵 V-LITE (Rp 150rb) · ⚡ V-PRO (Rp 450rb) · 🟣 V-ADVANCE (Rp 1,2jt)<br>🟢 V-ELITE (Rp 3,5jt) · 👑 V-ULTRA (Custom)<br><br>Boleh saya tahu jenis usaha Bapak/Ibu agar saya pilihkan yang paling tepat? 😊' },
    ];

    function getFallback(msg) {
        var m = msg.toLowerCase();
        /* ROI calculation inline */
        var roiMatch = m.match(/(\d[\d.,]*)\s*(juta|jt|miliar|m\b|rb|ribu)?/);
        if (roiMatch && (m.includes('omzet') || m.includes('roi') || m.includes('juta') || m.includes('jt'))) {
            var raw = parseFloat(roiMatch[1].replace(/,/g,'.').replace(/\./g,'')) || 0;
            var unit = (roiMatch[2]||'').toLowerCase();
            var omzet = raw;
            if (unit==='juta'||unit==='jt') omzet = raw * 1e6;
            else if (unit==='miliar'||unit==='m') omzet = raw * 1e9;
            else if (unit==='rb'||unit==='ribu') omzet = raw * 1e3;
            if (omzet >= 1e6) {
                var bocor  = omzet * 0.05;
                var saved  = bocor * 0.88;
                var biaya  = 450000;
                var net    = saved - biaya;
                var roi    = Math.round(net / biaya * 100);
                return '💡 <strong>Estimasi ROI V-Guard untuk bisnis Bapak/Ibu:</strong><br><br>' +
                       '📊 Omzet: Rp ' + Math.round(omzet).toLocaleString('id') + '/bln<br>' +
                       '💸 Kebocoran ~5%: Rp ' + Math.round(bocor).toLocaleString('id') + '/bln<br>' +
                       '✅ Diselamatkan (88%): <strong>Rp ' + Math.round(saved).toLocaleString('id') + '/bln</strong><br>' +
                       '📈 ROI Estimasi: <strong>' + roi + '%</strong> 🚀<br><br>' +
                       'Saya rekomendasikan <strong>V-PRO</strong> sebagai starting point. Mau lihat detail paket?';
            }
        }
        for (var i=0; i<rules.length; i++) {
            var r = rules[i];
            for (var j=0; j<r.keys.length; j++) {
                if (m.indexOf(r.keys[j]) !== -1) return r.reply;
            }
        }
        return 'Halo! 👋 Saya <strong>Sentinel CS</strong>, konsultan AI V-Guard.<br><br>' +
               'Ceritakan bisnis Bapak/Ibu:<br>• Berapa <strong>kasir/cabang</strong>?<br>' +
               '• Berapa <strong>omzet bulanan</strong>?<br><br>' +
               'Saya langsung rekomendasikan solusi terbaik &amp; hitung ROI-nya! 💡';
    }

    /* ── Send message ── */
    function sendMsg() {
        if (isBusy) return;
        var text = input.value.trim();
        if (!text) return;
        input.value = '';
        input.style.height = 'auto';
        processMsg(text);
    }

    function processMsg(text) {
        isBusy = true;
        addBubble(escHtml(text), true);
        history.push({ role:'user', content: text });
        showTyping();

        var delay = 800 + Math.random() * 700;
        setTimeout(function() {
            removeTyping();
            var reply = getFallback(text);
            addBubble(reply, false);
            history.push({ role:'assistant', content: reply });
            isBusy = false;
        }, delay);
    }

    function escHtml(s) {
        return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    }

    /* ── Auto-resize textarea ── */
    input.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 90) + 'px';
    });

    /* ── Event listeners ── */
    /* FAB click */
    fab.addEventListener('click', function(e) {
        e.stopPropagation();
        toggleChat();
    });
    /* FAB keyboard */
    fab.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleChat(); }
    });

    /* Close button */
    closeBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        closeChat();
    });

    /* Send button */
    sendBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        sendMsg();
    });

    /* Enter key in textarea (Shift+Enter = newline) */
    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMsg();
        }
    });

    /* Quick pills */
    pills.forEach(function(pill) {
        pill.addEventListener('click', function(e) {
            e.stopPropagation();
            if (!isBusy) {
                var msg = this.getAttribute('data-msg');
                if (msg) {
                    if (!isOpen) openChat();
                    processMsg(msg);
                }
            }
        });
    });

    /* Click inside chatbox should not close */
    chatbox.addEventListener('click', function(e) { e.stopPropagation(); });

    /* Close on outside click */
    document.addEventListener('click', function() { if (isOpen) closeChat(); });

    /* Notification dot after 4s */
    setTimeout(function() {
        if (!isOpen) notif.style.display = 'block';
    }, 4000);

    /* Proactive message after 12s */
    setTimeout(function() {
        if (!isOpen) {
            openChat();
        }
    }, 14000);

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
            <span class='status-dot'></span>System Online · v2.1
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
        # Auto-track referral if a ref is present and not yet logged
        referral_already_logged = any(
            r.get("ref_cid") == _ref for r in st.session_state.db_referrals
        )
        st.markdown(
            "<div style='background:#00d4ff11;border:1px solid #00d4ff33;border-radius:6px;"
            "padding:6px 10px;margin-bottom:10px;font-size:10px;color:#00d4ff;"
            "font-family:JetBrains Mono,monospace;'>🔗 Ref: " + _ref + " · " + SOURCE_MAP.get(_src,_src) + "</div>",
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

    # ── Public menu always visible ──
    PUBLIC_MENU = ["Beranda", "Produk & Harga", "Kalkulator ROI", "Portal Klien"]

    # ── Private menu only visible when admin authenticated ──
    PRIVATE_MENU = ["Investor Area", "Admin Access"] if st.session_state.authenticated else []

    MENU_OPTIONS = PUBLIC_MENU + PRIVATE_MENU
    menu = st.radio("", MENU_OPTIONS, label_visibility="collapsed")

    # Admin quick-login in sidebar (only show if NOT authenticated)
    if not st.session_state.authenticated:
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        st.markdown(
            "<p style='color:#4a6a8a;font-size:10px;text-transform:uppercase;"
            "letter-spacing:1.5px;margin-bottom:6px;'>Admin / Investor</p>",
            unsafe_allow_html=True,
        )
        _sidebar_pw = st.text_input("Access Code", type="password", key="sidebar_access_code",
                                     placeholder="Masukkan kode akses...")
        if st.button("Masuk", key="btn_sidebar_auth", use_container_width=True):
            if _sidebar_pw in ("w1nbju8282", "investor2026"):
                st.session_state.authenticated = True
                st.session_state.admin_logged_in   = (_sidebar_pw == "w1nbju8282")
                st.session_state.investor_pw_ok    = (_sidebar_pw in ("w1nbju8282","investor2026"))
                st.rerun()
            else:
                st.error("Kode akses salah.")

# =============================================================================
# 14. FLOATING CHAT WIDGET — rendered on EVERY page
# =============================================================================
st.markdown(CHAT_WIDGET_HTML, unsafe_allow_html=True)

# =============================================================================
# 15. PAGE: BERANDA
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
# 16. PAGE: PRODUK & HARGA
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
# 17. PAGE: KALKULATOR ROI
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
# 18. PAGE: PORTAL KLIEN
# =============================================================================
elif menu == "Portal Klien":
    st.markdown("<div style='padding:32px 48px;'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-title'>🏠 Portal <span style='color:#00d4ff;'>Klien</span></div>"
        "<div class='page-subtitle'>Masuk dengan Client ID Anda, atau ajukan pembelian baru.</div>",
        unsafe_allow_html=True,
    )

    if st.session_state.client_logged_in and st.session_state.client_data:
        klien = st.session_state.client_data
        cid   = klien.get("Client_ID","—")
        pkg   = klien.get("Produk","V-LITE")
        status = klien.get("Status","Menunggu Pembayaran")
        hb, hs = HARGA_MAP.get(pkg, ("—","—"))

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

        # Referral announcement banner
        ref_link = buat_referral_link(cid)
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#ffd70011,#ffab0011);border:1px solid #ffd70033;border-left:3px solid #ffd700;border-radius:10px;padding:14px 20px;margin-bottom:20px;'>
            <div style='font-family:Rajdhani,sans-serif;font-size:14px;font-weight:700;color:#ffd700;margin-bottom:4px;'>🎉 Dapatkan Komisi Penjualan 10%!</div>
            <div style='font-size:13px;color:#9ab8d4;'>Referensikan rekan bisnis Anda menggunakan link referral unik Anda dan dapatkan <strong style="color:#ffd700;">komisi 10% dari biaya setup</strong> untuk setiap klien baru yang berhasil bergabung.</div>
        </div>
        """, unsafe_allow_html=True)

        portal_tabs = st.tabs(["📋 Akun Saya", "🔗 Referral & Komisi", "📊 Dashboard", "📁 Dokumen"])

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
                    st.markdown("""
                    <div style='background:#00e67611;border:1px solid #00e67633;border-radius:12px;padding:20px;margin-bottom:12px;'>
                        <div style='font-size:12px;color:#00e676;font-family:JetBrains Mono,monospace;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>✅ Akun Aktif</div>
                        <div style='font-size:13px;color:#7a9bbf;'>Sistem V-Guard AI aktif mengawasi bisnis Anda 24/7.</div>
                        <div style='margin-top:12px;font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#00e676;'>Live</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    pay_link = buat_payment_link(pkg, klien.get("Nama Klien","Klien"))
                    st.markdown("""
                    <div style='background:#ffab0011;border:1px solid #ffab0033;border-radius:12px;padding:20px;margin-bottom:12px;'>
                        <div style='font-size:12px;color:#ffab00;font-family:JetBrains Mono,monospace;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>⏳ Menunggu Aktivasi</div>
                        <div style='font-size:13px;color:#7a9bbf;margin-bottom:12px;'>Selesaikan pembayaran untuk mengaktifkan akun Anda.</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.link_button("📲 Bayar via WhatsApp", pay_link, use_container_width=True)

        with portal_tabs[1]:
            st.markdown(f"""
            <div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;padding:24px;margin-bottom:16px;'>
                <div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#ffd700;margin-bottom:8px;'>🔗 Link Referral Unik Anda</div>
                <div style='font-size:13px;color:#7a9bbf;margin-bottom:16px;'>Bagikan link ini ke rekan bisnis Anda. Setiap referral yang berhasil aktivasi, Anda mendapatkan <strong style="color:#ffd700;">komisi 10% dari biaya setup</strong>!</div>
                <div class='ref-link-box'>{ref_link}</div>
                <div style='margin-top:12px;font-size:12px;color:#7a9bbf;'>
                    💰 <b>Contoh komisi:</b> Referral masuk paket V-PRO (setup Rp 750.000) → Anda dapat <b style="color:#ffd700;">Rp 75.000</b><br>
                    💰 V-ADVANCE (setup Rp 3.500.000) → Komisi <b style="color:#ffd700;">Rp 350.000</b><br>
                    💰 V-ELITE (setup Rp 10.000.000) → Komisi <b style="color:#ffd700;">Rp 1.000.000</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

            wa_share = "https://wa.me/?text=" + urllib.parse.quote(
                f"Halo! Saya sudah pakai V-Guard AI untuk keamanan bisnis saya — hasilnya luar biasa!\n\n"
                f"Sistem AI ini otomatis deteksi fraud kasir, pantau stok, & audit rekening bank 24/7.\n\n"
                f"Coba daftar di sini (link khusus saya): {ref_link}"
            )
            st.link_button("📲 Bagikan via WhatsApp", wa_share, use_container_width=True)

            # Show user's referral results
            my_refs = [r for r in st.session_state.db_referrals if r.get("ref_cid") == cid]
            if my_refs:
                st.markdown("<div style='margin-top:20px;font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:#e8f4ff;margin-bottom:12px;'>📊 Referral Saya</div>", unsafe_allow_html=True)
                total_komisi = sum(r.get("komisi_10pct",0) for r in my_refs)
                komisi_terbayar = sum(r.get("komisi_10pct",0) for r in my_refs if r.get("status")=="Terbayar")
                rc1, rc2 = st.columns(2)
                rc1.metric("Total Referral", len(my_refs))
                rc2.metric("Total Komisi", f"Rp {total_komisi:,.0f}")
                for r in my_refs:
                    badge_cls = "ref-badge-paid" if r.get("status")=="Terbayar" else "ref-badge-pending"
                    card_cls  = "ref-card ref-card-paid" if r.get("status")=="Terbayar" else "ref-card"
                    st.markdown(f"""
                    <div class='{card_cls}'>
                        <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                            <div>
                                <div style='font-size:14px;color:#e8f4ff;font-weight:500;'>{r.get("new_client","—")} — {r.get("new_usaha","—")}</div>
                                <div style='font-size:12px;color:#7a9bbf;'>{r.get("paket","—")} · Setup: Rp {r.get("setup_fee",0):,.0f} · Komisi: <b style="color:#ffd700;">Rp {r.get("komisi_10pct",0):,.0f}</b></div>
                                <div style='font-size:11px;color:#4a6a8a;margin-top:2px;'>{r.get("tanggal","—")}</div>
                            </div>
                            <span class='{badge_cls}'>{r.get("status","—")}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Belum ada referral yang masuk. Mulai bagikan link Anda sekarang!")

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
                    df_sample = fetch_pos_data()
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

                    # Show referral info if coming from referral link
                    ref_src = st.session_state.get("tracking_ref","")
                    if ref_src:
                        st.markdown(f"""
                        <div style='background:#ffd70011;border:1px solid #ffd70033;border-radius:8px;padding:10px 14px;margin-bottom:12px;font-size:12px;color:#ffd700;'>
                            🔗 Anda mendaftar melalui link referral: <b>{ref_src}</b>
                        </div>
                        """, unsafe_allow_html=True)

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
                                "Ref": ref_src,
                            }
                            st.session_state.db_umum.append(pengajuan)
                            st.session_state.db_pengajuan.append(pengajuan)
                            # Track referral commission if came from ref link
                            if ref_src:
                                setup_fee = {
                                    "V-LITE": 250_000, "V-PRO": 750_000, "V-ADVANCE": 3_500_000,
                                    "V-ELITE": 10_000_000, "V-ULTRA": 0
                                }.get(paket_form, 0)
                                if setup_fee > 0:
                                    track_referral(ref_src, pengajuan, setup_fee)
                            st.session_state.portal_form_submitted = True
                            st.rerun()
                        else:
                            st.error("Lengkapi semua field yang wajib diisi (*).")
                    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

# =============================================================================
# 19. PAGE: INVESTOR AREA  (private — only shown when authenticated)
# =============================================================================
elif menu == "Investor Area":
    if not st.session_state.authenticated:
        st.error("Akses ditolak. Masukkan kode akses di sidebar.")
        st.stop()

    st.markdown("<div style='padding:32px 48px;'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-title'>📈 Investor <span style='color:#ffd700;'>Area</span></div>"
        "<div class='page-subtitle'>V-Guard AI — Ekosistem Keamanan Bisnis Digital Indonesia</div>",
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div style='background:linear-gradient(135deg,#0d1626,#1a1500);border:1px solid #ffd70033;border-radius:14px;padding:24px;margin-bottom:24px;'>
        <div style='font-family:JetBrains Mono,monospace;font-size:10px;color:#ffd700;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;'>CONFIDENTIAL — INVESTOR BRIEF</div>
        <div style='font-family:Rajdhani,sans-serif;font-size:28px;font-weight:700;color:#ffd700;margin-bottom:4px;'>V-Guard AI Intelligence</div>
        <div style='font-size:14px;color:#7a9bbf;'>AI-Powered Business Security Ecosystem · Indonesia Market</div>
    </div>
    """, unsafe_allow_html=True)

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
        st.markdown("""<div style='background:#101c2e;border:1px solid #1e3352;border-radius:8px;padding:14px 18px;margin-top:12px;font-size:12px;color:#7a9bbf;'>⚠️ Proyeksi berdasarkan asumsi pertumbuhan organik + digital marketing. Angka aktual dapat berbeda tergantung eksekusi dan kondisi pasar.</div>""", unsafe_allow_html=True)

    with inv_tabs[1]:
        roadmap = [
            ("Q1 2026","🚀 Launch","Peluncuran V-LITE & V-PRO. Target 50 klien awal dari network founder.","done"),
            ("Q2 2026","⚡ Growth","Aktivasi V-ADVANCE & V-ELITE. Ekspansi ke 5 kota besar.","active"),
            ("Q3 2026","🌐 Scale","Launch V-ULTRA & white-label. Rekrut 10 reseller aktif.","upcoming"),
            ("Q4 2026","🏆 Series A Prep","Konsolidasi data, audit keuangan, pitch Series A.","upcoming"),
            ("2027","🌏 Expansion","Ekspansi ke Malaysia & Philippines. 1.000+ klien aktif.","upcoming"),
        ]
        for quarter, title, desc, status_r in roadmap:
            color = "#00e676" if status_r=="done" else "#00d4ff" if status_r=="active" else "#7a9bbf"
            st.markdown(f"<div style='background:#101c2e;border:1px solid #1e3352;border-left:3px solid {color};border-radius:8px;padding:16px 20px;margin-bottom:10px;display:flex;align-items:flex-start;gap:16px;'><div style='font-family:JetBrains Mono,monospace;font-size:11px;color:{color};min-width:60px;margin-top:2px;'>{quarter}</div><div><div style='font-family:Rajdhani,sans-serif;font-size:15px;font-weight:700;color:#e8f4ff;'>{title}</div><div style='font-size:13px;color:#7a9bbf;margin-top:4px;'>{desc}</div></div></div>", unsafe_allow_html=True)

    with inv_tabs[2]:
        st.markdown("""
        <div style='display:grid;grid-template-columns:1fr 1fr;gap:16px;'>
            <div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;padding:20px;'>
                <div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:#00d4ff;margin-bottom:12px;'>💰 Revenue Streams</div>
                <div style='font-size:13px;color:#7a9bbf;line-height:1.8;'>
                ● Langganan bulanan (SaaS MRR)<br>● Biaya setup & implementasi<br>● White-label licensing (V-ULTRA)<br>● Komisi referral program<br>● API usage fees (enterprise)
                </div>
            </div>
            <div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;padding:20px;'>
                <div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:#ffd700;margin-bottom:12px;'>🛡️ Keunggulan Kompetitif</div>
                <div style='font-size:13px;color:#7a9bbf;line-height:1.8;'>
                ● AI local-first (bahasa & konteks Indonesia)<br>● 5-tier pricing menjangkau semua segmen<br>● CCTV + Kasir + Bank dalam 1 platform<br>● Plug & Play — tidak butuh IT team<br>● WhatsApp-native alert system
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.link_button("📲 Jadwalkan Meeting dengan Founder", WA_LINK_KONSUL, use_container_width=False)
    if st.button("Logout Investor Area", key="inv_logout"):
        st.session_state.investor_pw_ok = False
        st.session_state.authenticated  = False
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

# =============================================================================
# 20. PAGE: ADMIN ACCESS — WAR ROOM (private)
# =============================================================================
elif menu == "Admin Access":
    if not st.session_state.authenticated or not st.session_state.admin_logged_in:
        st.error("Akses ditolak. Masukkan kode admin di sidebar.")
        st.stop()

    st.markdown("<div style='padding:32px 48px;'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-title'>⚔️ The War Room — <span style='color:#00d4ff;'>Admin Control Center</span></div>"
        "<div class='page-subtitle'>V-GUARD AI Ecosystem ©2026 — Founder Edition</div>",
        unsafe_allow_html=True,
    )

    col_logout = st.columns([4,1])[1]
    with col_logout:
        if st.button("Logout", key="logout_main"):
            st.session_state.admin_logged_in = False
            st.session_state.investor_pw_ok  = False
            st.session_state.authenticated   = False
            st.rerun()

    war_tabs = st.tabs([
        "📊 Dashboard",
        "🤖 AI Agents",
        "📹 Monitor CCTV",
        "🚨 Fraud Scanner",
        "📋 Pengajuan Masuk",
        "👥 Aktivasi Klien",
        "🔗 Referral Dashboard",
        "⏰ Auto-Billing",
        "🗄️ Database",
    ])

    # ── TAB 0: DASHBOARD ──────────────────────────────────────────────
    with war_tabs[0]:
        total_k   = len(st.session_state.db_umum)
        aktif_k   = sum(1 for k in st.session_state.db_umum if k.get("Status")=="Aktif")
        pending_k = sum(1 for k in st.session_state.db_umum if k.get("Status")=="Menunggu Pembayaran")
        mrr       = hitung_proyeksi_omset(st.session_state.db_umum)
        total_ref = len(st.session_state.db_referrals)
        total_kom = sum(r.get("komisi_10pct",0) for r in st.session_state.db_referrals)

        m1,m2,m3,m4,m5,m6 = st.columns(6)
        m1.metric("Total Klien", str(total_k))
        m2.metric("Klien Aktif", str(aktif_k))
        m3.metric("Pending", str(pending_k))
        m4.metric("MRR", f"Rp {mrr:,.0f}")
        m5.metric("Total Referral", str(total_ref))
        m6.metric("Total Komisi", f"Rp {total_kom:,.0f}")

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='demo-mockup'>
            <div style='margin-bottom:12px;'>
                <span class='demo-dot demo-red'></span><span class='demo-dot demo-yellow'></span><span class='demo-dot demo-green'></span>
                <span style='margin-left:12px;color:#7a9bbf;font-size:11px;'>v-guard-warroom / system-log</span>
            </div>
            <span style='color:#00e676;'>✓</span> [SYSTEM] V-Guard AI v2.1 — Boot selesai<br>
            <span style='color:#00d4ff;'>▸</span> [SENTINEL] 10 AI Agents terdaftar · 8 Aktif · 2 Standby<br>
            <span style='color:#00e676;'>✓</span> [LIAISON] Fraud scanner lokal aktif — filter anomali only<br>
            <span style='color:#00d4ff;'>▸</span> [CONCIERGE] Chat widget aktif di semua halaman<br>
            <span style='color:#ffab00;'>▸</span> [AUDITOR] Sinkronisasi mutasi bank — jadwal 06:00 WIB<br>
            <span style='color:#00e676;'>✓</span> [WHISPERBOT] WhatsApp gateway — Connected<br>
            <span style='color:#00d4ff;'>▸</span> [ORACLE] Predictive model last update: hari ini 02:00 WIB<br>
            <span style='color:#ffd700;'>▸</span> [COLLECTOR] Auto-billing H-7 check — Aktif<br>
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
        for i, loc in enumerate(cam_locations):
            with cam_cols[i % 2]:
                now_str = datetime.datetime.now().strftime("%H:%M:%S")
                alert_show = i == 0
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

        st.divider()

        # YOLO integration info
        st.markdown("""
        <div style='background:#101c2e;border:1px solid #1e3352;border-radius:10px;padding:16px 20px;'>
            <div style='font-family:Rajdhani,sans-serif;font-size:15px;font-weight:700;color:#00d4ff;margin-bottom:10px;'>VisualEye AI — YOLO Integration</div>
            <div style='font-size:12px;color:#7a9bbf;line-height:1.8;'>
                Model YOLO fine-tuned untuk deteksi:<br>
                ● <b style='color:#ff3b5c;'>unscanned_item</b> — barang tidak di-scan kasir<br>
                ● <b style='color:#ff3b5c;'>item_concealment</b> — barang disembunyikan<br>
                ● <b style='color:#ffab00;'>cash_swap</b> — penukaran uang mencurigakan<br>
                ● <b style='color:#ffab00;'>void_gesture</b> — gerakan void tidak wajar<br><br>
                Integrasi: <code style='color:#00d4ff;'>process_yolo_cctv_frame()</code> tersedia di kode — hubungkan DVR CCTV via HTTP POST.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Simulate YOLO detection for demo
        if st.button("🤖 Simulasi Deteksi YOLO (Demo)", key="btn_yolo_demo"):
            demo_frame = {"camera_id": "cam_01", "timestamp": str(datetime.datetime.now())}
            result = process_yolo_cctv_frame(demo_frame)
            st.json(result)

    # ── TAB 3: FRAUD SCANNER ──────────────────────────────────────────
    with war_tabs[3]:
        st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#e8f4ff;margin-bottom:4px;'>🚨 Fraud Intelligence Scanner — The Liaison</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:13px;color:#7a9bbf;margin-bottom:16px;'>Agent #4 Liaison: Filter lokal anomali sebelum dikirim ke API — hemat biaya hingga 80%.</div>", unsafe_allow_html=True)

        df_trx = fetch_pos_data()
        hasil  = scan_fraud_lokal(df_trx)

        fs1,fs2,fs3 = st.columns(3)
        fs1.metric("VOID / Cancel",  len(hasil["void"]),       delta="Tidak Wajar" if hasil["void"].shape[0] else "Aman")
        fs2.metric("Duplikat Kasir", len(hasil["fraud"]),      delta="Terdeteksi"  if hasil["fraud"].shape[0] else "Aman")
        fs3.metric("Selisih Saldo",  len(hasil["suspicious"]), delta="Anomali"     if hasil["suspicious"].shape[0] else "Aman")

        # AI Fraud Alarm: compare POS vs simulated YOLO
        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background:#ff3b5c11;border:1px solid #ff3b5c33;border-left:3px solid #ff3b5c;border-radius:8px;padding:12px 16px;margin-bottom:16px;'>
            <div style='font-family:Rajdhani,sans-serif;font-size:14px;font-weight:700;color:#ff3b5c;margin-bottom:4px;'>🤖 AI Fraud Alarm Engine</div>
            <div style='font-size:12px;color:#7a9bbf;'>Komparasi data kasir POS dengan deteksi YOLO CCTV. Mismatch = alarm otomatis ke Owner.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⚡ Jalankan AI Fraud Alarm Check", key="btn_ai_alarm"):
            yolo_results = [process_yolo_cctv_frame({"camera_id": f"cam_0{i+1}", "timestamp": str(datetime.datetime.now())}) for i in range(2)]
            alarms = check_ai_fraud_alarm(df_trx, yolo_results)
            if alarms:
                st.error(f"⚠️ {len(alarms)} alarm fraud terdeteksi!")
                for alarm in alarms:
                    wa_alarm = trigger_alarm(alarm["reason"], alarm["kasir"], alarm["cabang"], alarm["jumlah"])
                    st.markdown(f"""
                    <div style='background:#ff3b5c11;border:1px solid #ff3b5c33;border-radius:8px;padding:12px 16px;margin-bottom:8px;'>
                        <b style='color:#ff3b5c;'>⚠ ALARM</b><br>
                        Kasir: {alarm['kasir']} · Cabang: {alarm['cabang']} · Jumlah: Rp {alarm['jumlah']:,.0f}<br>
                        Alasan: {alarm['reason']}
                    </div>
                    """, unsafe_allow_html=True)
                    st.link_button(f"📲 Kirim Alert ke Owner — {alarm['cabang']}", wa_alarm, key=f"alarm_{alarm['kasir']}")
            else:
                st.success("✅ Tidak ada mismatch kasir vs CCTV.")

        tv,tf,ts = st.tabs(["VOID","Duplikat","Selisih"])
        with tv:
            if not hasil["void"].empty:
                st.error("Transaksi VOID mencurigakan ditemukan!")
                st.dataframe(hasil["void"][["ID_Transaksi","Cabang","Kasir","Jumlah","Waktu"]], use_container_width=True)
                for cab in hasil["void"]["Cabang"].unique():
                    alarm_link = trigger_alarm("VOID Mencurigakan Berulang", "—", cab, 0)
                    st.link_button(f"Alert Owner — {cab}", alarm_link, key=f"voidalert_{cab}")
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
                ref_badge = ""
                if klien.get("Ref"):
                    ref_badge = f"<span style='background:#ffd70011;color:#ffd700;border:1px solid #ffd70044;border-radius:20px;font-size:10px;padding:2px 8px;font-family:JetBrains Mono,monospace;margin-left:8px;'>🔗 Ref: {klien['Ref']}</span>"

                st.markdown(f"""
                <div class='client-card-pending'>
                    <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;'>
                        <div>
                            <div style='font-family:Rajdhani,sans-serif;font-size:17px;font-weight:700;color:#e8f4ff;'>{klien.get("Nama Klien","—")} — {klien.get("Nama Usaha","—")}</div>
                            <div style='font-family:JetBrains Mono,monospace;font-size:10px;color:#00d4ff;margin-bottom:4px;'>{cid} · {pkg} · {hb}/bln {ref_badge}</div>
                            <div style='font-size:12px;color:#7a9bbf;'>WA: {klien.get("WhatsApp","—")} · Daftar: {klien.get("Tanggal","—")}</div>
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
                    db_idx = next((j for j,k in enumerate(st.session_state.db_umum) if k.get("Client_ID")==cid), None)
                    if db_idx is not None:
                        if st.button("✅ Aktivasi Akun", key=f"aktiv_{cid}_{i}", type="primary", use_container_width=True):
                            st.session_state.db_umum[db_idx]["Status"] = "Aktif"
                            # Update referral status if applicable
                            for r in st.session_state.db_referrals:
                                if r.get("new_client") == klien.get("Nama Klien") and r.get("status") == "Menunggu Konfirmasi":
                                    r["status"] = "Terbayar"
                            st.rerun()
                with pc3:
                    akses_txt = urllib.parse.quote(
                        f"Halo {klien.get('Nama Klien','Klien')},\n\n"
                        f"✅ Akun V-Guard Anda telah AKTIF!\n\n"
                        f"🔑 Client ID: {cid}\n"
                        f"🔗 Dashboard: {BASE_APP_URL}\n"
                        f"📦 Paket: {pkg}\n\n"
                        f"Selamat menggunakan V-Guard AI!\n— Tim V-Guard AI"
                    )
                    st.link_button("📲 Kirim Akses Klien", f"https://wa.me/{wa_tgt}?text={akses_txt}", use_container_width=True, key=f"access_{cid}_{i}")
                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # ── TAB 5: AKTIVASI KLIEN ─────────────────────────────────────────
    with war_tabs[5]:
        st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#e8f4ff;margin-bottom:4px;'>👥 Manajemen Klien Aktif</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:13px;color:#7a9bbf;margin-bottom:16px;'>Kelola status, kirim invoice, dan akses dashboard klien.</div>", unsafe_allow_html=True)

        with st.expander("➕ Tambah Klien Manual"):
            ac1,ac2 = st.columns(2)
            with ac1:
                new_nama   = st.text_input("Nama Klien", key="new_nama")
                new_usaha  = st.text_input("Nama Usaha", key="new_usaha")
                new_wa     = st.text_input("WhatsApp", key="new_wa")
            with ac2:
                new_produk = st.selectbox("Produk", ["V-LITE","V-PRO","V-ADVANCE","V-ELITE","V-ULTRA"], key="new_produk")
                new_status = st.selectbox("Status Awal", ["Menunggu Pembayaran","Aktif"], key="new_status")
                new_due    = st.date_input("Jatuh Tempo Invoice (untuk H-7 reminder)", key="new_due",
                                           value=datetime.date.today() + datetime.timedelta(days=30))
            if st.button("Tambahkan Klien", type="primary", key="btn_add_client"):
                if new_nama and new_wa:
                    cid_new = buat_client_id(new_nama, new_wa)
                    st.session_state.db_umum.append({
                        "Client_ID": cid_new, "Nama Klien": new_nama,
                        "Nama Usaha": new_usaha, "WhatsApp": new_wa,
                        "Produk": new_produk, "Status": new_status,
                        "Tanggal": str(datetime.date.today()),
                        "invoice_due_date": str(new_due),
                        "Source": "Admin Manual",
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
                    akses_txt = urllib.parse.quote(f"Halo {klien['Nama Klien']},\n\n✅ Akun V-Guard Anda AKTIF!\n\n🔑 Client ID: {cid}\n🔗 Portal: {BASE_APP_URL}\n📦 Paket: {klien['Produk']}\n\n— Tim V-Guard AI")
                    st.link_button("🔑 Kirim Akses", f"https://wa.me/{wa_tgt}?text={akses_txt}", use_container_width=True, key=f"akses_{i}")
                with ac4:
                    ref_link2 = buat_referral_link(cid)
                    ref_txt = urllib.parse.quote(f"Link referral Anda: {ref_link2}\nKomisi 10% dari setiap klien baru yang berhasil!")
                    st.link_button("🔗 Referral", f"https://wa.me/{wa_tgt}?text={ref_txt}", use_container_width=True, key=f"ref_{i}")
                st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

    # ── TAB 6: REFERRAL DASHBOARD ─────────────────────────────────────
    with war_tabs[6]:
        st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#e8f4ff;margin-bottom:4px;'>🔗 Referral Dashboard</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:13px;color:#7a9bbf;margin-bottom:20px;'>Monitor daftar referral masuk, status penjualan, dan kalkulasi komisi 10% yang harus dibayarkan.</div>", unsafe_allow_html=True)

        db_refs = st.session_state.db_referrals

        # Summary metrics
        total_refs   = len(db_refs)
        total_kom_r  = sum(r.get("komisi_10pct",0) for r in db_refs)
        kom_pending  = sum(r.get("komisi_10pct",0) for r in db_refs if r.get("status")=="Menunggu Konfirmasi")
        kom_terbayar = sum(r.get("komisi_10pct",0) for r in db_refs if r.get("status")=="Terbayar")

        rm1,rm2,rm3,rm4 = st.columns(4)
        rm1.metric("Total Referral", str(total_refs))
        rm2.metric("Total Komisi", f"Rp {total_kom_r:,.0f}")
        rm3.metric("Komisi Pending", f"Rp {kom_pending:,.0f}")
        rm4.metric("Komisi Terbayar", f"Rp {kom_terbayar:,.0f}")

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # Add demo referral
        with st.expander("➕ Input Referral Manual (untuk testing)"):
            mr1,mr2 = st.columns(2)
            with mr1:
                demo_ref_cid   = st.text_input("Ref Client ID (pemberi referral)", placeholder="VG-XXXXXX", key="demo_ref_cid")
                demo_new_nama  = st.text_input("Nama Klien Baru", key="demo_ref_nama")
                demo_new_usaha = st.text_input("Nama Usaha Baru", key="demo_ref_usaha")
            with mr2:
                demo_paket     = st.selectbox("Paket", ["V-LITE","V-PRO","V-ADVANCE","V-ELITE"], key="demo_ref_paket")
                setup_map      = {"V-LITE":250_000,"V-PRO":750_000,"V-ADVANCE":3_500_000,"V-ELITE":10_000_000}
                demo_setup     = setup_map.get(demo_paket, 750_000)
                demo_komisi    = int(demo_setup * KOMISI_RATE)
                st.markdown(f"<div style='padding:12px;background:#ffd70011;border:1px solid #ffd70033;border-radius:8px;margin-top:24px;font-size:13px;color:#ffd700;'>Setup Fee: Rp {demo_setup:,.0f}<br>Komisi 10%: <b>Rp {demo_komisi:,.0f}</b></div>", unsafe_allow_html=True)
            if st.button("Tambah Referral", key="btn_add_ref", type="primary"):
                if demo_ref_cid and demo_new_nama:
                    track_referral(demo_ref_cid, {"Nama Klien": demo_new_nama, "Nama Usaha": demo_new_usaha, "Produk": demo_paket}, demo_setup)
                    st.success("Referral ditambahkan!")
                    st.rerun()

        if not db_refs:
            st.info("Belum ada data referral. Referral akan otomatis tercatat saat klien mendaftar melalui link referral.")
        else:
            st.markdown("<div style='margin-bottom:12px;font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:#e8f4ff;'>Daftar Referral Masuk</div>", unsafe_allow_html=True)
            for i, r in enumerate(db_refs):
                is_paid  = r.get("status") == "Terbayar"
                card_cls = "ref-card ref-card-paid" if is_paid else "ref-card"
                badge_cls= "ref-badge-paid" if is_paid else "ref-badge-pending"
                st.markdown(f"""
                <div class='{card_cls}'>
                    <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;'>
                        <div>
                            <div style='font-size:14px;color:#e8f4ff;font-weight:600;'>{r.get("new_client","—")} — {r.get("new_usaha","—")}</div>
                            <div style='font-size:12px;color:#7a9bbf;margin-top:2px;'>
                                Dari Ref: <b style='color:#00d4ff;font-family:JetBrains Mono,monospace;'>{r.get("ref_cid","—")}</b> ·
                                Paket: {r.get("paket","—")} ·
                                Setup: Rp {r.get("setup_fee",0):,.0f} ·
                                Komisi: <b style='color:#ffd700;'>Rp {r.get("komisi_10pct",0):,.0f}</b>
                            </div>
                            <div style='font-size:11px;color:#4a6a8a;margin-top:2px;'>Tanggal: {r.get("tanggal","—")}</div>
                        </div>
                        <span class='{badge_cls}'>{r.get("status","—")}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                rb1, rb2 = st.columns([2,1])
                with rb1:
                    if not is_paid:
                        if st.button("✅ Tandai Komisi Terbayar", key=f"pay_ref_{i}", use_container_width=True):
                            st.session_state.db_referrals[i]["status"] = "Terbayar"
                            st.rerun()
                    else:
                        st.markdown("<div style='font-size:12px;color:#00e676;padding:8px 0;'>✓ Komisi sudah dibayarkan</div>", unsafe_allow_html=True)
                with rb2:
                    # Find referrer's WA
                    referrer = next((k for k in st.session_state.db_umum if k.get("Client_ID","").upper() == r.get("ref_cid","").upper()), None)
                    if referrer and referrer.get("WhatsApp"):
                        wa_ref = referrer["WhatsApp"]
                        if not wa_ref.startswith("62"): wa_ref = "62" + wa_ref.lstrip("0")
                        komisi_msg = urllib.parse.quote(
                            f"Halo {referrer.get('Nama Klien','')},\n\n"
                            f"🎉 Selamat! Referral Anda berhasil!\n\n"
                            f"Klien: {r.get('new_client','—')}\n"
                            f"Paket: {r.get('paket','—')}\n"
                            f"Komisi 10%: Rp {r.get('komisi_10pct',0):,.0f}\n\n"
                            f"Komisi akan ditransfer ke rekening Anda segera.\n— Tim V-Guard AI"
                        )
                        st.link_button("📲 Notif Komisi", f"https://wa.me/{wa_ref}?text={komisi_msg}", use_container_width=True, key=f"notif_ref_{i}")
                st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

            # Export
            st.divider()
            df_refs = pd.DataFrame(db_refs)
            st.download_button(
                "⬇️ Download Laporan Referral CSV",
                data=df_refs.to_csv(index=False).encode("utf-8"),
                file_name=f"vguard_referrals_{datetime.date.today()}.csv",
                mime="text/csv",
            )

    # ── TAB 7: AUTO-BILLING ───────────────────────────────────────────
    with war_tabs[7]:
        st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#e8f4ff;margin-bottom:4px;'>⏰ Auto-Billing — H-7 & H-1 Reminder</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:13px;color:#7a9bbf;margin-bottom:20px;'>Agent Collector #9 mengingatkan klien otomatis H-7 dan H-1 sebelum jatuh tempo invoice.</div>", unsafe_allow_html=True)

        # Check reminders
        reminders = check_autobilling_reminders(st.session_state.db_umum)

        if reminders:
            st.warning(f"⚠️ {len(reminders)} klien mendekati jatuh tempo invoice!")
            for rem in reminders:
                color = "#ff3b5c" if rem["delta"] == 1 else "#ffab00"
                label = "H-1 🚨 BESOK JATUH TEMPO" if rem["delta"] == 1 else "H-7 Akan jatuh tempo"
                wa_rem = rem["wa"]
                if wa_rem and not wa_rem.startswith("62"): wa_rem = "62" + wa_rem.lstrip("0")
                msg_rem = urllib.parse.quote(
                    f"{'🚨 URGENT — ' if rem['delta']==1 else '⏰ '}PENGINGAT INVOICE V-GUARD AI\n\n"
                    f"Yth. {rem['nama']},\n\n"
                    f"Invoice paket {rem['paket']} Anda akan jatuh tempo pada {rem['due']} "
                    f"({'BESOK!' if rem['delta']==1 else f'dalam {rem[\"delta\"]} hari'}).\n\n"
                    f"Mohon segera lakukan pembayaran agar layanan tidak terputus.\n\n"
                    f"Transfer: BCA 3450074658 a/n Erwin Sinaga\n— Tim V-Guard AI"
                )
                st.markdown(f"""
                <div style='background:#101c2e;border:1px solid {color}44;border-left:3px solid {color};border-radius:8px;padding:14px 18px;margin-bottom:10px;'>
                    <div style='font-family:Rajdhani,sans-serif;font-size:15px;font-weight:700;color:{color};margin-bottom:4px;'>{label}</div>
                    <div style='font-size:13px;color:#e8f4ff;'>{rem['nama']} — {rem['usaha']}</div>
                    <div style='font-size:12px;color:#7a9bbf;'>Paket: {rem['paket']} · Due: {rem['due']} · WA: {rem['wa']}</div>
                </div>
                """, unsafe_allow_html=True)
                if wa_rem:
                    st.link_button(f"📲 Kirim Reminder ke {rem['nama']}", f"https://wa.me/{wa_rem}?text={msg_rem}", key=f"rem_{rem['cid']}")
        else:
            st.success("✅ Tidak ada invoice yang mendekati jatuh tempo saat ini.")

        st.divider()
        st.markdown("""
        <div style='background:#101c2e;border:1px solid #1e3352;border-radius:10px;padding:16px 20px;'>
            <div style='font-family:Rajdhani,sans-serif;font-size:15px;font-weight:700;color:#00d4ff;margin-bottom:10px;'>⚙️ Setup Auto-Billing</div>
            <div style='font-size:12px;color:#7a9bbf;line-height:1.8;'>
                Untuk mengaktifkan pengiriman otomatis tanpa klik manual:<br>
                1. Integrasikan dengan <b style='color:#e8f4ff;'>Fonnte</b> atau <b style='color:#e8f4ff;'>WA Business API</b><br>
                2. Set <code style='color:#00d4ff;'>invoice_due_date</code> saat klien aktif (field sudah ada di form Tambah Klien)<br>
                3. Jadwalkan <code style='color:#00d4ff;'>check_autobilling_reminders()</code> via cron job atau Cloud Scheduler setiap pukul 08:00 WIB<br>
                4. Hubungkan response ke endpoint WA gateway untuk kirim otomatis
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── TAB 8: DATABASE ───────────────────────────────────────────────
    with war_tabs[8]:
        if st.session_state.db_umum:
            df_db = pd.DataFrame(st.session_state.db_umum)
            if "Client_ID" in df_db.columns:
                df_db["Dashboard_Link"] = df_db["Client_ID"].apply(buat_dashboard_link)
                df_db["Referral_Link"]  = df_db["Client_ID"].apply(buat_referral_link)
            st.dataframe(df_db, use_container_width=True, hide_index=True)
            st.download_button(
                "⬇️ Download CSV Klien",
                data=df_db.to_csv(index=False).encode("utf-8"),
                file_name=f"vguard_clients_{datetime.date.today()}.csv",
                mime="text/csv",
            )
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            if st.button("🗑️ Hapus Semua Data (Reset)", key="btn_reset_db"):
                st.session_state.db_umum = []
                st.session_state.db_pengajuan = []
                st.session_state.db_referrals = []
                st.rerun()
        else:
            st.info("Database masih kosong. Klien yang mendaftar akan muncul di sini.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

# =============================================================================
# 21. FOOTER
# =============================================================================
st.markdown(
    "<div style='background:#060b14;border-top:1px solid #1e3352;padding:28px 48px;"
    "display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;'>"
    "<div><span style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#00d4ff;'>V-Guard AI Intelligence</span>"
    "<span style='color:#7a9bbf;font-size:12px;margin-left:12px;'>V-GUARD AI Ecosystem ©2026</span></div>"
    "<div style='font-size:12px;color:#7a9bbf;'>Digitizing Trust · Eliminating Leakage · Protecting Every Rupiah</div></div>",
    unsafe_allow_html=True,
)
