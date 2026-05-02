# =============================================================================
# V-GUARD AI INTELLIGENCE — logic_vguard.py
# Elite AI Squad v3.1 — 10 Agent Brain Layer (REVISED)
# Sync target: app.py v3.0 (Professional SaaS Edition)
#
# AGENT ROSTER (sesuai V-Guard Elite AI Squad Workflow):
#  1. AgentVisionary    → Mata          (CCTV / Visual Intelligence)
#  2. AgentConcierge    → Telinga       (CS / Onboarding)
#  3. AgentGrowthHacker → Mulut         (Marketing / Branding)
#  4. AgentLiaison      → Tangan        (SAP / Moka / POS Integration)
#  5. AgentAnalyst      → Otak Audit    (Financial Forensic)
#  6. AgentStockmaster  → Gudang        (Inventory & OCR Invoice)
#  7. AgentWatchdog     → Otak Bisnis   (Fraud Detector)
#  8. AgentSentinel     → Imun Fisik    (Server Monitor)
#  9. AgentLegalist     → Imun Hukum    (Compliance / NDA)
# 10. AgentTreasurer    → Kantong       (Profit / Expense Calculator)
#
# Architecture: Local-First Filter (Liaison → Watchdog) → Cloud API
# Hemat 80% API cost vs full-cloud scanning.
# =============================================================================

import datetime
import random
import uuid
import re
import urllib.parse
import pandas as pd
import streamlit as st

# =============================================================================
# CONSTANTS — shared dengan app.py
# =============================================================================
WA_NUMBER    = "6282122190885"
BASE_APP_URL = "https://v-guard-ai.streamlit.app"
KOMISI_RATE  = 0.10

HARGA_NUMERIK = {
    "V-LITE":    150000,
    "V-PRO":     450000,
    "V-ADVANCE": 1_200000,
    "V-ELITE":   3500000,
    "V-ULTRA":   0,
}

SETUP_FEE = {
    "V-LITE":    250_000,
    "V-PRO":     750_000,
    "V-ADVANCE": 3_500_000,
    "V-ELITE":   10_000_000,
    "V-ULTRA":   0,
}

HARGA_MAP = {
    "V-LITE":    ("Rp 150.000",         "Rp 250.000"),
    "V-PRO":     ("Rp 450.000",         "Rp 750.000"),
    "V-ADVANCE": ("Rp 1.200.000",       "Rp 3.500.000"),
    "V-ELITE":   ("Mulai Rp 3.500.000", "Rp 10.000.000"),
    "V-ULTRA":   ("Custom",             "Konsultasi"),
}

# =============================================================================
# SESSION STATE INITIALIZER
# =============================================================================
VGUARD_STATE_DEFAULTS = {
    "warroom_db":         [],
    "vision_logs":        [],
    "audit_logs":         [],
    "inventory_db":       {"Premium Coffee": 100, "V-Guard Device": 50},
    "last_heartbeat":     None,
    "total_loss":         0.0,
    "agent_heartbeats":   {},
    "concierge_leads":    [],
    "stockmaster_alerts": [],
    "collector_queue":    [],
    "growth_campaigns":   [],
    "compliance_flags":   [],
    "server_health":      {},
    "treasurer_ledger":   [],
    "watchdog_alerts":    [],
}


def init_vguard_core():
    """
    Inisialisasi seluruh session state yang dibutuhkan 10 Agent.
    Panggil sekali di bagian atas app.py sebelum page routing.
    """
    for key, default in VGUARD_STATE_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = (
                default.copy() if isinstance(default, dict)
                else list(default)  if isinstance(default, list)
                else default
            )
    if st.session_state.get("last_heartbeat") is None:
        st.session_state["last_heartbeat"] = datetime.datetime.now()


# =============================================================================
# DATA BRIDGE — Pintu masuk data POS ke warroom_db
# =============================================================================
def process_data_bridge(
    client_id:   str,
    trans_type:  str,
    amount:      float,
    item_name:   str,
    timestamp:   datetime.datetime,
    kasir:       str = "—",
    cabang:      str = "—",
    saldo_fisik: float = None,
) -> dict:
    """
    Pintu masuk transaksi dari POS ke sistem V-Guard.
    Setiap entry melewati fungsi ini sebelum diproses agent.
    """
    entry = {
        "id":           "TRX-" + str(uuid.uuid4())[:6].upper(),
        "client_id":    client_id,
        "type":         trans_type,
        "amount":       float(amount),
        "item":         item_name,
        "kasir":        kasir,
        "cabang":       cabang,
        "timestamp":    timestamp,
        "saldo_fisik":  saldo_fisik if saldo_fisik is not None else float(amount),
        "saldo_sistem": float(amount),
        "flagged":      False,
        "flag_reason":  "",
    }
    if trans_type == "SALE" and item_name in st.session_state.get("inventory_db", {}):
        st.session_state["inventory_db"][item_name] = max(
            0, st.session_state["inventory_db"][item_name] - 1
        )
    if trans_type in ("VOID", "REFUND", "CANCEL"):
        st.session_state["total_loss"] = (
            st.session_state.get("total_loss", 0.0) + float(amount)
        )
        entry["flagged"]    = True
        entry["flag_reason"]= f"{trans_type} — antrian Watchdog scan"

    st.session_state.setdefault("warroom_db", []).append(entry)
    st.session_state["last_heartbeat"] = datetime.datetime.now()
    return entry


# =============================================================================
# BASE AGENT CLASS
# =============================================================================
class VGuardAgent:
    """Base class semua 10 Elite AI Agent."""

    def __init__(self, agent_id: int, name: str, organ: str,
                 role: str, icon: str, desc: str):
        self.id    = agent_id
        self.name  = name
        self.organ = organ
        self.role  = role
        self.icon  = icon
        self.desc  = desc
        self._log: list = []

    def run(self, *args, **kwargs):
        raise NotImplementedError(f"Agent {self.name}.run() belum diimplementasikan.")

    def get_status(self) -> dict:
        ks = st.session_state.get("agent_kill_switch", {}).get(self.id, False)
        return {
            "id":        self.id,
            "name":      self.name,
            "organ":     self.organ,
            "role":      self.role,
            "icon":      self.icon,
            "desc":      self.desc,
            "active":    not ks,
            "status":    "KILLED" if ks else "ACTIVE",
            "log_count": len(self._log),
            "last_run":  self._log[-1]["ts"] if self._log else "—",
        }

    def log_event(self, event: str, data: dict = None):
        entry = {
            "ts":    datetime.datetime.now().strftime("%H:%M:%S"),
            "agent": self.name,
            "event": event,
            "data":  data or {},
        }
        self._log.append(entry)
        st.session_state.setdefault("agent_logs", []).append(entry)
        return entry

    def is_active(self) -> bool:
        return not st.session_state.get("agent_kill_switch", {}).get(self.id, False)


# =============================================================================
# AGENT 1 — VISIONARY: Mata — CCTV / Visual Intelligence
# =============================================================================
class AgentVisionary(VGuardAgent):
    """
    MATA sistem V-Guard.
    Mengawasi feed CCTV, mendeteksi anomali visual (barang tidak di-scan,
    gesture void, penukaran uang mencurigakan), dan me-render overlay
    transaksi real-time di atas feed kamera.

    Production: ganti stub dengan ultralytics YOLO inference.
    """

    def __init__(self):
        super().__init__(
            1, "Visionary", "Mata",
            "CCTV Visual Intelligence",
            "👁️",
            "Mengawasi feed CCTV, deteksi anomali visual, render overlay transaksi real-time."
        )

    def run(self, frame_data: dict = None, pos_trx: dict = None) -> dict:
        if not self.is_active():
            return {"status": "KILLED", "alert": False}

        camera_id = (frame_data or {}).get("camera_id", "cam_01")
        timestamp = (frame_data or {}).get("timestamp", str(datetime.datetime.now()))

        detections = [{
            "label":      "person",
            "confidence": round(random.uniform(0.88, 0.99), 2),
            "bbox":       [random.randint(50,200), random.randint(30,100),
                           random.randint(200,400), random.randint(300,500)],
        }]

        alert        = False
        alert_reason = ""
        if pos_trx and pos_trx.get("Status") == "VOID":
            alert        = random.random() < 0.30
            alert_reason = "CUSTOMER_ABSENT_VOID" if alert else ""

        overlay = {
            "camera_id":    camera_id,
            "timestamp":    timestamp,
            "detections":   detections,
            "alert":        alert,
            "alert_reason": alert_reason,
            "overlay_text": self._build_overlay(pos_trx),
        }
        st.session_state.setdefault("vision_logs", []).append(overlay)
        self.log_event("Frame processed", {"cam": camera_id, "alert": alert})
        return {"status": "OK", **overlay}

    def process_batch(self, frames: list, pos_df: pd.DataFrame = None) -> list:
        results = []
        for i, frame in enumerate(frames):
            pos_trx = None
            if pos_df is not None and not pos_df.empty and i < len(pos_df):
                pos_trx = pos_df.iloc[i].to_dict()
            results.append(self.run(frame, pos_trx))
        return results

    def _build_overlay(self, pos_trx: dict = None) -> str:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        if pos_trx:
            return (
                f"[V-GUARD VISIONARY] {now} | "
                f"KASIR: {pos_trx.get('Kasir','—')} | "
                f"AMOUNT: Rp {float(pos_trx.get('Jumlah',0)):,.0f} | "
                f"STATUS: {pos_trx.get('Status','—')}"
            )
        return f"[V-GUARD VISIONARY] {now} | Monitoring Active"


# =============================================================================
# AGENT 2 — CONCIERGE: Telinga — CS / Onboarding
# =============================================================================
class AgentConcierge(VGuardAgent):
    """
    TELINGA sistem V-Guard.
    Mendengarkan pesan calon klien, mendeteksi kebutuhan,
    memberi skor lead, merekomendasikan paket terbaik,
    dan menangani onboarding klien baru pasca aktivasi.
    """

    KEYWORD_MATRIX = {
        "V-LITE":    ["warung","1 kasir","lapak","kios","usaha kecil","baru buka","coba","murah"],
        "V-PRO":     ["cafe","kafe","resto","cctv","pantau","monitor","audit bank","ocr","2 kasir","3 kasir"],
        "V-ADVANCE": ["cabang","multi cabang","stok","minimarket","franchise","banyak kasir","alarm"],
        "V-ELITE":   ["fraud","curang","kecurangan","void","forensik","korporasi","enterprise","server"],
        "V-ULTRA":   ["white label","rebranding","lisensi","reseller","custom platform","holding"],
    }

    def __init__(self):
        super().__init__(
            2, "Concierge", "Telinga",
            "CS & Onboarding Intelligence",
            "🤝",
            "Lead scoring, rekomendasi paket, onboarding klien baru pasca aktivasi."
        )

    def run(self, user_message: str, session_history: list = None) -> dict:
        if not self.is_active():
            return {"status": "KILLED", "package": None, "score": 0}

        text   = user_message.lower()
        scores = {}
        for pkg, keywords in self.KEYWORD_MATRIX.items():
            hit = sum(2 for kw in keywords if kw in text)
            if session_history:
                full = " ".join(m.get("content","") for m in session_history).lower()
                hit += sum(1 for kw in keywords if kw in full)
            if hit:
                scores[pkg] = hit

        best_pkg   = max(scores, key=scores.get) if scores else None
        lead_score = min(100, sum(scores.values()) * 10) if scores else 0
        intents    = self._detect_intent(text)

        result = {
            "package":    best_pkg,
            "lead_score": lead_score,
            "intent":     intents,
            "all_scores": scores,
            "qualify":    lead_score >= 20,
        }

        if result["qualify"] and best_pkg:
            st.session_state.setdefault("concierge_leads", []).append({
                "ts":      datetime.datetime.now().strftime("%H:%M:%S"),
                "message": user_message[:80],
                "package": best_pkg,
                "score":   lead_score,
                "intent":  intents,
            })

        self.log_event("Lead scored", {"pkg": best_pkg, "score": lead_score})
        return {"status": "OK", **result}

    def onboard_client(self, klien: dict) -> dict:
        pkg = klien.get("Produk","V-LITE")
        steps = {
            "V-LITE":    ["Aktifkan akun","Setup dashboard","Setup WA alert","Test transaksi"],
            "V-PRO":     ["Aktifkan akun","Hubungkan POS","Setup OCR","Konfig bank audit","Test alert"],
            "V-ADVANCE": ["Aktifkan akun","Install per cabang","Hubungkan CCTV","Briefing staf"],
            "V-ELITE":   ["Onboarding call","Server provisioning","CCTV integration","UAT","Go-live"],
            "V-ULTRA":   ["Executive briefing","White-label setup","Squad config","Soft launch"],
        }
        return {
            "client_id": klien.get("Client_ID","—"),
            "nama":      klien.get("Nama Klien","—"),
            "paket":     pkg,
            "checklist": steps.get(pkg, steps["V-LITE"]),
            "generated": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        }

    def _detect_intent(self, text: str) -> list:
        intents = []
        if any(k in text for k in ["harga","berapa","biaya","tarif"]):      intents.append("PRICE_INQUIRY")
        if any(k in text for k in ["demo","coba","gratis"]):                intents.append("DEMO_REQUEST")
        if any(k in text for k in ["daftar","order","beli","mulai"]):       intents.append("PURCHASE_INTENT")
        if any(k in text for k in ["fraud","curang","void","kecurangan"]):  intents.append("PAIN_POINT_FRAUD")
        if any(k in text for k in ["roi","hemat","bocor","omzet","rugi"]):  intents.append("ROI_CALCULATOR")
        return intents


# =============================================================================
# AGENT 3 — GROWTHHACKER: Mulut — Marketing / Branding
# =============================================================================
class AgentGrowthHacker(VGuardAgent):
    """
    MULUT sistem V-Guard.
    Mengatur seluruh komunikasi keluar: content marketing, referral campaign,
    A/B test copywriting, dan analisis traffic channel (WA/IG/TikTok/LinkedIn).
    Generate materi promo otomatis berdasarkan paket yang paling sering di-lead.
    """

    PAIN_HOOKS = {
        "V-LITE":    "Warung Anda aman? Cek kebocoran kasir GRATIS 7 hari! 🏪",
        "V-PRO":     "CCTV saja tidak cukup — V-Guard baca transaksi kasir real-time. 📹",
        "V-ADVANCE": "Multi-cabang tanpa AI pengawas = kebocoran tak terlihat. 🔍",
        "V-ELITE":   "Kasir curang tidak bisa sembunyi dari Deep Learning AI V-Guard. 🛡️",
        "V-ULTRA":   "Bangun platform keamanan bisnis sendiri dengan white-label V-Guard. 👑",
    }

    def __init__(self):
        super().__init__(
            3, "GrowthHacker", "Mulut",
            "Marketing & Branding Automation",
            "📣",
            "Content marketing, referral campaign, A/B test copy, WA blast otomatis."
        )

    def run(self, leads: list = None, target_pkg: str = "V-PRO",
            channel: str = "whatsapp") -> dict:
        if not self.is_active():
            return {"status": "KILLED"}

        leads      = leads or st.session_state.get("concierge_leads", [])
        conversion = self._calc_conversion(leads, target_pkg)
        content    = self._generate_brief(target_pkg, channel)

        campaign = {
            "ts":           datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
            "target_pkg":   target_pkg,
            "channel":      channel,
            "total_leads":  len(leads),
            "conversion":   conversion,
            "pain_hook":    self.PAIN_HOOKS.get(target_pkg,""),
            "content_brief":content,
            "wa_blast":     self.generate_wa_blast(target_pkg),
        }
        st.session_state.setdefault("growth_campaigns", []).append(campaign)
        self.log_event("Campaign generated", {"pkg": target_pkg, "channel": channel})
        return {"status": "OK", "campaign": campaign}

    def generate_wa_blast(self, target_pkg: str, custom_hook: str = "") -> str:
        hb, _ = HARGA_MAP.get(target_pkg, ("Custom","—"))
        hook   = custom_hook or self.PAIN_HOOKS.get(target_pkg,"")
        msg = (
            f"💡 *PROMO V-GUARD AI*\n\n{hook}\n\n"
            f"✅ Paket {target_pkg} mulai {hb}/bln\n"
            f"✅ Deteksi fraud kasir otomatis 24/7\n"
            f"✅ Laporan real-time ke WhatsApp Owner\n\n"
            f"🎯 *Demo GRATIS 30 menit — tanpa komitmen*\n"
            f"👉 https://wa.me/{WA_NUMBER}?text=Halo+Pak+Erwin%2C+saya+ingin+Demo\n\n"
            f"— Tim V-Guard AI 🛡️"
        )
        return f"https://wa.me/?text={urllib.parse.quote(msg)}"

    def _calc_conversion(self, leads: list, pkg: str) -> dict:
        total   = len(leads)
        matched = sum(1 for l in leads if l.get("package") == pkg)
        rate    = round(matched / total * 100, 1) if total > 0 else 0.0
        return {"total": total, "matched": matched, "rate_pct": rate}

    def _generate_brief(self, pkg: str, channel: str) -> dict:
        briefs = {
            "whatsapp":  f"WA Blast: Pain point fraud + ROI kalkulator + CTA demo {pkg}.",
            "instagram": f"Carousel 5 slide: 'Tanda Kasirmu Curang' → solusi {pkg}.",
            "tiktok":    f"Video 30 dtk: Owner panik lihat VOID → V-Guard deteksi < 5 detik.",
            "linkedin":  f"Artikel B2B: ROI keamanan bisnis + studi kasus {pkg} enterprise.",
            "youtube":   f"Demo walkthrough 10 menit: setup V-Guard {pkg} dari nol.",
        }
        return {"channel": channel, "brief": briefs.get(channel, f"Content {pkg} via {channel}.")}


# =============================================================================
# AGENT 4 — LIAISON: Tangan — SAP / Moka / POS Integration + Local Filter
# =============================================================================
class AgentLiaison(VGuardAgent):
    """
    TANGAN sistem V-Guard.
    Menghubungkan V-Guard ke seluruh sistem POS eksternal klien:
    Moka, SAP, iReap, Majoo, Olsera, Pawoon, dan Custom API.

    SEKALIGUS menjadi Local Filter pertama — hanya anomali yang naik ke cloud.
    Target: hemat 80% API cost vs full-cloud scanning.

    6 Filter Rules:
      R1 — VOID flag langsung
      R2 — VOID rate > 20% per kasir
      R3 — Duplikat transaksi < 5 menit
      R4 — Selisih saldo fisik vs sistem
      R5 — Jam transaksi tidak wajar (< 07:00 / > 23:00)
      R6 — Rapid VOID > 2 kali dalam 10 menit
    """

    VOID_RATE_THRESHOLD   = 0.20
    DUPLICATE_WINDOW_MIN  = 5
    SALDO_TOLERANCE_RP    = 0
    RAPID_VOID_WINDOW_MIN = 10
    UNUSUAL_HOUR_START    = 23
    UNUSUAL_HOUR_END      = 7
    SUPPORTED_CONNECTORS  = ["moka","sap","ireap","majoo","olsera","pawoon","custom_api"]

    def __init__(self):
        super().__init__(
            4, "Liaison", "Tangan",
            "POS / SAP / Moka Integration + Local Fraud Filter",
            "🔗",
            "Integrasi POS eksternal + filter lokal 6 rules sebelum kirim ke Cloud AI."
        )

    def run(self, df: pd.DataFrame) -> dict:
        if not self.is_active():
            return {"status": "KILLED", "anomalies": pd.DataFrame(), "clean": pd.DataFrame()}

        if df is None or df.empty:
            return {"status": "OK", "anomalies": pd.DataFrame(), "clean": pd.DataFrame(), "stats": {}}

        df = df.copy()
        df["_flag"]   = False
        df["_reason"] = ""

        # R1 — VOID langsung flag
        void_mask = df["Status"] == "VOID" if "Status" in df.columns else pd.Series(False, index=df.index)
        df.loc[void_mask, "_flag"]   = True
        df.loc[void_mask, "_reason"] = df.loc[void_mask, "_reason"] + "VOID | "

        # R2 — VOID rate > 20% per kasir
        if "Kasir" in df.columns and void_mask.any():
            kasir_total = df.groupby("Kasir").size()
            kasir_void  = df[void_mask].groupby("Kasir").size()
            for kasir, voids in kasir_void.items():
                total = kasir_total.get(kasir, 1)
                if voids / total > self.VOID_RATE_THRESHOLD:
                    mask = df["Kasir"] == kasir
                    df.loc[mask, "_flag"]   = True
                    df.loc[mask, "_reason"] = df.loc[mask, "_reason"] + f"HIGH_VOID_RATE_{voids/total:.0%} | "

        # R3 — Duplikat < 5 menit
        if all(c in df.columns for c in ["Kasir","Jumlah","Waktu"]):
            df_s = df.sort_values(["Kasir","Jumlah","Waktu"])
            df_s["_gap"] = (
                df_s.groupby(["Kasir","Jumlah"])["Waktu"]
                .diff().dt.total_seconds().div(60)
            )
            dup_idx = df_s[df_s["_gap"] < self.DUPLICATE_WINDOW_MIN].index
            df.loc[dup_idx, "_flag"]   = True
            df.loc[dup_idx, "_reason"] = df.loc[dup_idx, "_reason"] + "DUPLICATE_<5MIN | "

        # R4 — Selisih saldo fisik vs sistem
        if "Saldo_Fisik" in df.columns and "Saldo_Sistem" in df.columns:
            mismatch = (df["Saldo_Sistem"] - df["Saldo_Fisik"]).abs() > self.SALDO_TOLERANCE_RP
            df.loc[mismatch, "_flag"]   = True
            df.loc[mismatch, "_reason"] = df.loc[mismatch, "_reason"] + "SALDO_MISMATCH | "

        # R5 — Jam tidak wajar
        if "Waktu" in df.columns:
            hours   = pd.to_datetime(df["Waktu"]).dt.hour
            unusual = (hours >= self.UNUSUAL_HOUR_START) | (hours < self.UNUSUAL_HOUR_END)
            df.loc[unusual, "_flag"]   = True
            df.loc[unusual, "_reason"] = df.loc[unusual, "_reason"] + "UNUSUAL_HOUR | "

        # R6 — Rapid VOID
        if all(c in df.columns for c in ["Kasir","Waktu","Status"]):
            void_df2 = df[void_mask].sort_values(["Kasir","Waktu"]).copy()
            if not void_df2.empty:
                void_df2["_prev"] = void_df2.groupby("Kasir")["Waktu"].shift(1)
                void_df2["_vgap"] = (
                    (void_df2["Waktu"] - void_df2["_prev"])
                    .dt.total_seconds().div(60)
                )
                rapid = void_df2[void_df2["_vgap"] < self.RAPID_VOID_WINDOW_MIN]
                if not rapid.empty and "ID_Transaksi" in df.columns:
                    rapid_ids = rapid.get("ID_Transaksi", pd.Series(dtype=str))
                    mask      = df["ID_Transaksi"].isin(rapid_ids)
                    df.loc[mask, "_flag"]   = True
                    df.loc[mask, "_reason"] = df.loc[mask, "_reason"] + "RAPID_VOID | "

        anomalies = df[df["_flag"] == True].copy()
        clean     = df[df["_flag"] == False].copy()

        stats = {
            "total":          len(df),
            "anomalies":      len(anomalies),
            "clean":          len(clean),
            "filter_rate":    f"{len(clean)/len(df)*100:.1f}%" if len(df) > 0 else "0%",
            "api_cost_saved": len(clean),
        }
        self.log_event("POS filter complete", stats)
        return {
            "status":      "OK",
            "anomalies":   anomalies,
            "clean":       clean,
            "stats":       stats,
            "api_payload": anomalies,
        }

    def connect_pos(self, connector: str, api_url: str = "", api_key: str = "") -> dict:
        if connector not in self.SUPPORTED_CONNECTORS:
            return {"status": "ERROR", "msg": f"Connector '{connector}' tidak didukung."}
        return {
            "status":    "OK",
            "connector": connector,
            "endpoint":  api_url or f"http://localhost:8080/api/{connector}/transactions",
            "connected": True,
            "note":      "TODO production: replace stub dengan requests.get(api_url, ...)",
        }


# =============================================================================
# AGENT 5 — ANALYST: Otak Audit — Financial Forensic
# =============================================================================
class AgentAnalyst(VGuardAgent):
    """
    OTAK AUDIT sistem V-Guard.
    Rekonsiliasi kasir vs bank, analisis tren selisih keuangan,
    identifikasi pola anomali finansial jangka panjang,
    dan produksi laporan audit PDF-ready.
    """

    MATCH_TOLERANCE_RP = 1_000

    def __init__(self):
        super().__init__(
            5, "Analyst", "Otak Audit",
            "Financial Forensic & Bank Reconciliation",
            "🏦",
            "Rekonsiliasi kasir vs bank, forensik keuangan, laporan audit otomatis."
        )

    def run(self, kasir_df: pd.DataFrame, bank_df: pd.DataFrame = None) -> dict:
        if not self.is_active():
            return {"status": "KILLED", "matched": [], "unmatched": [], "discrepancy": 0}

        if bank_df is None or bank_df.empty:
            bank_df = self._generate_demo_bank(kasir_df)

        matched, unmatched = [], []
        discrepancy_total  = 0.0

        if kasir_df is None or kasir_df.empty:
            return {"status": "OK", "matched": [], "unmatched": [], "discrepancy": 0}

        for _, trx in kasir_df.iterrows():
            if trx.get("Status") == "VOID":
                continue
            amount = float(trx.get("Jumlah", 0))
            found  = False
            for _, btrx in bank_df.iterrows():
                bank_amt = float(btrx.get("amount", 0))
                if abs(bank_amt - amount) <= self.MATCH_TOLERANCE_RP:
                    matched.append({
                        "trx_id":       trx.get("ID_Transaksi","—"),
                        "kasir_amount": amount,
                        "bank_amount":  bank_amt,
                        "selisih":      bank_amt - amount,
                        "status":       "MATCH",
                    })
                    found = True
                    break
            if not found:
                unmatched.append({
                    "trx_id":       trx.get("ID_Transaksi","—"),
                    "kasir_amount": amount,
                    "bank_amount":  0,
                    "selisih":      -amount,
                    "status":       "TIDAK_ADA_DI_BANK",
                })
                discrepancy_total += amount

        total_trx  = len(matched) + len(unmatched)
        match_rate = f"{len(matched)/total_trx*100:.1f}%" if total_trx > 0 else "0%"

        audit_report = {
            "ts":           datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
            "matched":      len(matched),
            "unmatched":    len(unmatched),
            "discrepancy":  discrepancy_total,
            "match_rate":   match_rate,
            "verdict":      "CLEAR" if discrepancy_total == 0 else "FLAGGED",
            "risk_score":   min(100, int(discrepancy_total / 10_000)),
        }
        st.session_state.setdefault("audit_logs", []).append(audit_report)
        self.log_event("Audit complete", {"discrepancy": discrepancy_total})

        return {
            "status":       "OK",
            "matched":      matched,
            "unmatched":    unmatched,
            "discrepancy":  discrepancy_total,
            "audit_report": audit_report,
            "bank_df":      bank_df,
        }

    def generate_audit_summary(self, result: dict) -> str:
        r = result.get("audit_report", {})
        return (
            f"📊 LAPORAN AUDIT V-GUARD AI\n"
            f"Tanggal   : {r.get('ts','—')}\n"
            f"Match Rate: {r.get('match_rate','—')}\n"
            f"Selisih   : Rp {r.get('discrepancy',0):,.0f}\n"
            f"Verdict   : {r.get('verdict','—')}\n"
            f"Risk Score: {r.get('risk_score',0)}/100\n"
            f"— AgentAnalyst V-Guard AI"
        )

    def _generate_demo_bank(self, kasir_df: pd.DataFrame) -> pd.DataFrame:
        now  = datetime.datetime.now()
        rows = []
        for _, row in (kasir_df.iterrows() if kasir_df is not None else []):
            if row.get("Status") != "VOID":
                amount = float(row.get("Jumlah", 0))
                noise  = random.choice([0,0,0,-500,500,-1000]) if random.random() > 0.85 else 0
                rows.append({
                    "date":        now - datetime.timedelta(minutes=random.randint(1,60)),
                    "description": f"TRANSFER/EDC — {row.get('Kasir','—')}",
                    "amount":      amount + noise,
                    "type":        "CREDIT",
                })
        return pd.DataFrame(rows)


# =============================================================================
# AGENT 6 — STOCKMASTER: Gudang — Inventory & OCR Invoice
# =============================================================================
class AgentStockmaster(VGuardAgent):
    """
    GUDANG sistem V-Guard.
    Update stok real-time via drag & drop invoice supplier (OCR),
    pantau level stok, dan kirim reorder alert saat stok kritis.
    """

    REORDER_THRESHOLD = 10
    CRITICAL_STOCK    = 3

    def __init__(self):
        super().__init__(
            6, "Stockmaster", "Gudang",
            "Inventory Intelligence & OCR Invoice",
            "📦",
            "Update stok real-time via OCR invoice supplier, reorder alert otomatis."
        )

    def run(self, action: str = "check", item_name: str = None,
            quantity: int = 0, invoice_text: str = None) -> dict:
        if not self.is_active():
            return {"status": "KILLED"}

        inventory = st.session_state.get("inventory_db", {})
        if action == "check":       return self._check_inventory(inventory)
        elif action == "update":    return self._update_stock(inventory, item_name, quantity)
        elif action == "ocr_parse": return self._parse_invoice_ocr(invoice_text, inventory)
        elif action == "reorder_check":
            return {"status": "OK", "reorders": self._check_reorder(inventory)}
        return {"status": "ERROR", "msg": f"Unknown action: {action}"}

    def _check_inventory(self, inventory: dict) -> dict:
        alerts = []
        for item, qty in inventory.items():
            if qty <= self.CRITICAL_STOCK:
                alerts.append({"item": item, "qty": qty, "level": "CRITICAL"})
            elif qty <= self.REORDER_THRESHOLD:
                alerts.append({"item": item, "qty": qty, "level": "LOW"})
        st.session_state.setdefault("stockmaster_alerts", []).extend(alerts)
        self.log_event("Inventory checked", {"alerts": len(alerts)})
        return {
            "status":    "OK",
            "inventory": inventory,
            "alerts":    alerts,
            "total_sku": len(inventory),
            "critical":  sum(1 for a in alerts if a["level"] == "CRITICAL"),
            "low_stock": sum(1 for a in alerts if a["level"] == "LOW"),
        }

    def _update_stock(self, inventory: dict, item: str, qty: int) -> dict:
        if not item:
            return {"status": "ERROR", "msg": "Item name required"}
        old = inventory.get(item, 0)
        inventory[item] = max(0, old + qty)
        st.session_state["inventory_db"] = inventory
        self.log_event("Stock updated", {"item": item, "old": old, "new": inventory[item]})
        return {"status": "OK", "item": item, "old_qty": old, "new_qty": inventory[item]}

    def _parse_invoice_ocr(self, text: str, inventory: dict) -> dict:
        if not text:
            return {"status": "ERROR", "msg": "No OCR text provided"}
        pattern = r"([A-Za-z0-9\s\-]+?)\s+(\d+)\s*(?:pcs|unit|box|lusin|kg|gr|ltr)?"
        matches = re.findall(pattern, text, re.IGNORECASE)
        parsed  = []
        for m in matches:
            item_name, qty = m[0].strip(), int(m[1])
            if qty > 0 and len(item_name) > 2:
                old = inventory.get(item_name, 0)
                inventory[item_name] = old + qty
                parsed.append({"item": item_name, "qty_added": qty, "new_total": old + qty})
        st.session_state["inventory_db"] = inventory
        self.log_event("OCR parsed", {"items": len(parsed)})
        return {"status": "OK", "parsed_items": parsed, "updated_inventory": inventory}

    def _check_reorder(self, inventory: dict) -> list:
        return [
            {"item": item, "qty": qty, "suggested_order": max(50, (20 - qty) * 2)}
            for item, qty in inventory.items() if qty <= self.REORDER_THRESHOLD
        ]


# =============================================================================
# AGENT 7 — WATCHDOG: Otak Bisnis — Fraud Detector
# =============================================================================
class AgentWatchdog(VGuardAgent):
    """
    OTAK BISNIS sistem V-Guard.
    Menerima anomaly payload dari Liaison, menganalisis pola fraud
    lintas kasir/cabang/waktu, memberi risk score, dan memutuskan
    apakah perlu eskalasi ke Owner dan/atau cloud AI.

    Eskalasi ke Gemini HANYA jika risk >= HIGH → hemat cost maksimal.
    """

    RISK_THRESHOLDS = {
        "LOW":      (0, 30),
        "MEDIUM":   (31, 60),
        "HIGH":     (61, 85),
        "CRITICAL": (86, 100),
    }

    def __init__(self):
        super().__init__(
            7, "Watchdog", "Otak Bisnis",
            "Fraud Pattern Detector & Risk Scoring",
            "🐕",
            "Analisis pola fraud, risk scoring, keputusan eskalasi ke cloud AI."
        )

    def run(self, anomalies_df: pd.DataFrame, ai_model=None) -> dict:
        if not self.is_active():
            return {"status": "KILLED", "alerts": [], "risk": "UNKNOWN"}

        if anomalies_df is None or (isinstance(anomalies_df, pd.DataFrame) and anomalies_df.empty):
            self.log_event("No anomalies")
            return {"status": "OK", "alerts": [], "risk": "LOW", "risk_score": 0}

        patterns   = self._detect_patterns(anomalies_df)
        risk_score = (
            len(patterns.get("repeat_kasir",[])) * 15
            + len(patterns.get("high_amount_void",[])) * 20
            + patterns.get("rapid_void_count",0) * 10
            + patterns.get("saldo_mismatch_count",0) * 12
        )
        risk_score = min(100, risk_score)

        risk_level = "LOW"
        for level, (lo, hi) in self.RISK_THRESHOLDS.items():
            if lo <= risk_score <= hi:
                risk_level = level

        alerts = []
        for _, row in anomalies_df.iterrows():
            reason = str(row.get("_reason","")).strip().rstrip("|").strip()
            if reason:
                alerts.append({
                    "kasir":  row.get("Kasir","—"),
                    "cabang": row.get("Cabang","—"),
                    "jumlah": float(row.get("Jumlah",0)),
                    "reason": reason,
                    "risk":   risk_level,
                })

        # Cloud AI — hanya saat HIGH atau CRITICAL
        ai_analysis = None
        cloud_used  = False
        if risk_level in ("HIGH","CRITICAL") and ai_model:
            try:
                prompt = (
                    "Analisis pola fraud berikut (sudah difilter lokal oleh Liaison):\n\n"
                    + anomalies_df.to_string(index=False)
                    + "\n\nBerikan: 1) Pola kecurangan utama, "
                    "2) Kasir paling berisiko, 3) Rekomendasi taktis Owner. "
                    "Format ringkas, bahasa Indonesia, actionable."
                )
                resp = ai_model.generate_content(prompt)
                if resp.text:
                    ai_analysis = resp.text.strip()
                    st.session_state["api_cost_total"] = (
                        st.session_state.get("api_cost_total", 0.0) + 150
                    )
                    cloud_used = True
            except Exception:
                pass

        result = {
            "status":      "OK",
            "alerts":      alerts,
            "risk":        risk_level,
            "risk_score":  risk_score,
            "patterns":    patterns,
            "ai_analysis": ai_analysis,
            "cloud_used":  cloud_used,
            "escalated":   risk_level in ("HIGH","CRITICAL"),
        }
        st.session_state.setdefault("watchdog_alerts", []).extend(alerts)
        self.log_event("Watchdog scan done", {"risk": risk_level, "score": risk_score})
        return result

    def _detect_patterns(self, df: pd.DataFrame) -> dict:
        patterns = {
            "repeat_kasir":         [],
            "high_amount_void":     [],
            "rapid_void_count":     0,
            "saldo_mismatch_count": 0,
        }
        if "Kasir" in df.columns:
            kasir_counts = df.groupby("Kasir").size()
            patterns["repeat_kasir"] = [
                {"kasir": k, "count": int(v)}
                for k, v in kasir_counts.items() if v >= 2
            ]
        if "Jumlah" in df.columns and "Status" in df.columns:
            high_void = df[(df["Status"]=="VOID") & (df["Jumlah"] >= 100_000)]
            patterns["high_amount_void"] = (
                high_void[["Kasir","Jumlah"]].to_dict("records") if not high_void.empty else []
            )
        if "_reason" in df.columns:
            patterns["rapid_void_count"]      = int(df["_reason"].str.contains("RAPID_VOID").sum())
            patterns["saldo_mismatch_count"]  = int(df["_reason"].str.contains("SALDO_MISMATCH").sum())
        return patterns


# =============================================================================
# AGENT 8 — SENTINEL: Sistem Imun Fisik — Server Monitor
# =============================================================================
class AgentSentinel(VGuardAgent):
    """
    SISTEM IMUN FISIK sistem V-Guard.
    Memantau kesehatan infrastruktur: uptime, CPU, memory, disk,
    latency API, dan status koneksi database secara real-time.
    Jika ada degradasi → trigger alert ke Admin.

    Production: ganti stub dengan psutil + requests health check.
    """

    THRESHOLDS = {
        "cpu_pct":    80.0,
        "mem_pct":    85.0,
        "disk_pct":   90.0,
        "latency_ms": 2000,
        "uptime_pct": 99.0,
    }

    def __init__(self):
        super().__init__(
            8, "Sentinel", "Sistem Imun Fisik",
            "Server & Infrastructure Monitor",
            "🖥️",
            "Monitor uptime, CPU/memory, API latency, dan infrastruktur 24/7."
        )

    def run(self, force_check: bool = False) -> dict:
        if not self.is_active():
            return {"status": "KILLED"}

        metrics = self._collect_metrics()
        health  = self._evaluate_health(metrics)

        st.session_state["server_health"] = {
            "last_check": datetime.datetime.now().strftime("%H:%M:%S"),
            "metrics":    metrics,
            "health":     health,
        }
        self.log_event("Health check done", {"overall": health["overall"]})
        return {"status": "OK", "metrics": metrics, "health": health}

    def get_status_badge(self) -> str:
        health  = st.session_state.get("server_health", {}).get("health", {})
        overall = health.get("overall","UNKNOWN")
        return {"HEALTHY":"🟢 HEALTHY","WARNING":"🟡 WARNING",
                "CRITICAL":"🔴 CRITICAL","UNKNOWN":"⚪ UNKNOWN"}.get(overall,"⚪ UNKNOWN")

    def _collect_metrics(self) -> dict:
        # Stub — production: psutil.cpu_percent(), psutil.virtual_memory().percent, dll.
        return {
            "cpu_pct":    round(random.uniform(15, 65), 1),
            "mem_pct":    round(random.uniform(30, 75), 1),
            "disk_pct":   round(random.uniform(20, 55), 1),
            "latency_ms": random.randint(80, 400),
            "uptime_pct": round(random.uniform(99.5, 99.99), 3),
            "db_status":  "CONNECTED",
            "api_status": "ONLINE",
            "timestamp":  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _evaluate_health(self, metrics: dict) -> dict:
        issues = []
        for metric, threshold in self.THRESHOLDS.items():
            val = metrics.get(metric, 0)
            if metric == "uptime_pct":
                if val < threshold: issues.append(f"UPTIME LOW: {val}%")
            elif val > threshold:
                issues.append(f"{metric.upper()} HIGH: {val}")
        overall = "CRITICAL" if len(issues) > 2 else "WARNING" if issues else "HEALTHY"
        return {"overall": overall, "issues": issues, "score": max(0, 100 - len(issues)*20)}


# =============================================================================
# AGENT 9 — LEGALIST: Sistem Imun Hukum — Compliance / NDA
# =============================================================================
class AgentLegalist(VGuardAgent):
    """
    SISTEM IMUN HUKUM sistem V-Guard.
    Memastikan operasional comply terhadap UU PDP, NDA klien,
    retensi data audit, SLA monitoring, dan deteksi PII exposure di logs.
    """

    RETENTION_DAYS  = 365
    SLA_UPTIME_PCT  = 99.0
    PII_FIELDS      = ["nama","no_hp","email","alamat","nik"]
    COMPLIANCE_RULES= [
        "UU PDP No.27/2022 — Perlindungan Data Pribadi",
        "SE OJK 21/2017 — Keamanan Sistem Informasi",
        "ISO 27001 — Information Security Management",
        "POJK 11/2022 — Keamanan Siber Fintech",
    ]

    def __init__(self):
        super().__init__(
            9, "Legalist", "Sistem Imun Hukum",
            "Compliance, NDA & Legal Monitoring",
            "⚖️",
            "Monitor kepatuhan regulasi, NDA, SLA, retensi data, dan compliance hukum."
        )

    def run(self, db_klien: list = None, server_metrics: dict = None) -> dict:
        if not self.is_active():
            return {"status": "KILLED", "flags": []}

        flags = []
        flags.extend(self._check_pii_exposure())
        if server_metrics:
            flags.extend(self._check_sla(server_metrics))
        if db_klien:
            flags.extend(self._check_contract_expiry(db_klien))

        st.session_state.setdefault("compliance_flags", []).extend(flags)
        self.log_event("Compliance check done", {"flags": len(flags)})
        return {
            "status":        "OK",
            "flags":         flags,
            "compliant":     len(flags) == 0,
            "rules_checked": self.COMPLIANCE_RULES,
            "risk_level":    "HIGH" if len(flags) > 3 else "MEDIUM" if flags else "CLEAR",
            "report_date":   datetime.datetime.now().strftime("%d/%m/%Y"),
        }

    def generate_nda_text(self, client_name: str, business_name: str, pkg: str) -> str:
        today = datetime.date.today().strftime("%d %B %Y")
        return (
            f"PERJANJIAN KERAHASIAAN (NDA)\n\n"
            f"Antara: PT V-Guard AI Intelligence ('Penyedia')\n"
            f"Dan   : {client_name} / {business_name} ('Klien')\n"
            f"Paket : {pkg}\n"
            f"Tanggal: {today}\n\n"
            f"1. Penyedia menjaga kerahasiaan data bisnis Klien.\n"
            f"2. Data transaksi Klien tidak dibagikan ke pihak ketiga.\n"
            f"3. Data audit disimpan maksimal {self.RETENTION_DAYS} hari.\n"
            f"4. SLA uptime minimum {self.SLA_UPTIME_PCT}% per bulan.\n"
            f"5. Pelanggaran SLA → kompensasi sesuai kontrak.\n\n"
            f"Berlaku sejak penandatanganan.\n— V-Guard AI Intelligence ©2026"
        )

    def _check_pii_exposure(self) -> list:
        flags = []
        logs  = st.session_state.get("agent_logs", [])
        for log in logs[-50:]:
            data_str = str(log.get("data","")).lower()
            exposed  = [f for f in self.PII_FIELDS if f in data_str]
            if exposed:
                flags.append({
                    "rule":     "PII_IN_LOG",
                    "severity": "MEDIUM",
                    "detail":   f"PII fields '{', '.join(exposed)}' terdeteksi di agent log.",
                })
                break
        return flags

    def _check_sla(self, metrics: dict) -> list:
        flags = []
        uptime = metrics.get("uptime_pct", 100)
        if uptime < self.SLA_UPTIME_PCT:
            flags.append({
                "rule":     "SLA_BREACH",
                "severity": "HIGH",
                "detail":   f"Uptime {uptime}% < SLA {self.SLA_UPTIME_PCT}% — potensi penalti.",
            })
        return flags

    def _check_contract_expiry(self, db_klien: list) -> list:
        flags = []
        today = datetime.date.today()
        for k in db_klien:
            due_str = k.get("invoice_due_date","")
            if not due_str:
                continue
            try:
                due   = datetime.date.fromisoformat(due_str)
                delta = (due - today).days
                if delta < 0 and k.get("Status") == "Aktif":
                    flags.append({
                        "rule":     "CONTRACT_OVERDUE",
                        "severity": "HIGH",
                        "detail":   f"Klien {k.get('Nama Klien','—')} overdue {abs(delta)} hari.",
                    })
            except Exception:
                pass
        return flags


# =============================================================================
# AGENT 10 — TREASURER: Kantong — Profit / Expense Calculator
# =============================================================================
class AgentTreasurer(VGuardAgent):
    """
    KANTONG sistem V-Guard.
    Menghitung dan memproyeksikan seluruh arus keuangan:
    MRR, ARR, gross margin, COGS, komisi referral,
    proyeksi profit, dan breakdown pengeluaran per bulan.
    """

    FIXED_COSTS = {
        "Gaji Tim":          5_000_000,
        "Server & Cloud":    1_200_000,
        "Tools & SaaS":        500_000,
        "Marketing Budget":  2_000_000,
        "Admin & Legal":       300_000,
    }
    COGS_RATE = 0.22
    TAX_RATE  = 0.11

    def __init__(self):
        super().__init__(
            10, "Treasurer", "Kantong",
            "Profit & Expense Calculator",
            "💰",
            "Hitung MRR, gross margin, proyeksi profit, dan breakdown pengeluaran bulanan."
        )

    def run(self, db_klien: list, extra_expenses: dict = None,
            months_ahead: int = 6) -> dict:
        if not self.is_active():
            return {"status": "KILLED"}

        aktif         = [k for k in db_klien if k.get("Status") == "Aktif"]
        mrr           = sum(HARGA_NUMERIK.get(k.get("Produk","V-LITE"),0) for k in aktif)
        total_revenue = mrr

        total_fixed   = sum(self.FIXED_COSTS.values())
        extra         = sum((extra_expenses or {}).values())
        cogs          = total_revenue * self.COGS_RATE
        komisi_total  = sum(
            r.get("komisi_10pct",0)
            for r in st.session_state.get("db_referrals",[])
            if r.get("status") == "Terbayar"
        )
        total_expense = total_fixed + extra + cogs + komisi_total

        gross_profit  = total_revenue - cogs
        gross_margin  = round(gross_profit / total_revenue * 100, 1) if total_revenue > 0 else 0
        net_profit    = total_revenue - total_expense
        tax           = max(0, net_profit * self.TAX_RATE)
        net_after_tax = net_profit - tax

        projection = self._project(mrr, months_ahead)

        ledger_entry = {
            "period":           datetime.date.today().strftime("%B %Y"),
            "mrr":              mrr,
            "total_revenue":    total_revenue,
            "cogs":             int(cogs),
            "fixed_costs":      total_fixed,
            "komisi_expense":   komisi_total,
            "total_expense":    int(total_expense),
            "gross_profit":     int(gross_profit),
            "gross_margin_pct": gross_margin,
            "net_profit":       int(net_profit),
            "tax_11pct":        int(tax),
            "net_after_tax":    int(net_after_tax),
            "arr":              mrr * 12,
            "klien_aktif":      len(aktif),
        }
        st.session_state.setdefault("treasurer_ledger",[]).append(ledger_entry)
        self.log_event("Ledger calculated", {"mrr": mrr, "net": int(net_profit)})

        return {
            "status":          "OK",
            "ledger":          ledger_entry,
            "fixed_breakdown": self.FIXED_COSTS,
            "projection":      projection,
        }

    def roi_klien(self, omzet: float, pkg: str, kebocoran_pct: float = 5.0) -> dict:
        biaya        = HARGA_NUMERIK.get(pkg, 450_000)
        bocor        = omzet * (kebocoran_pct / 100)
        diselamatkan = bocor * 0.88
        net_save     = diselamatkan - biaya
        roi          = round(net_save / biaya * 100, 0) if biaya > 0 else 0
        payback      = round(biaya / diselamatkan * 30, 0) if diselamatkan > 0 else 0
        return {
            "omzet":        omzet,
            "kebocoran_rp": bocor,
            "diselamatkan": diselamatkan,
            "biaya_paket":  biaya,
            "net_saving":   net_save,
            "roi_pct":      roi,
            "payback_days": payback,
        }

    def _project(self, mrr_current: float, months: int) -> list:
        projection, mrr = [], mrr_current
        for i in range(1, months + 1):
            growth = random.uniform(0.15, 0.40)
            mrr   *= (1 + growth)
            net    = mrr - mrr * self.COGS_RATE - sum(self.FIXED_COSTS.values())
            projection.append({
                "month":      (datetime.date.today() + datetime.timedelta(days=30*i)).strftime("%b %Y"),
                "mrr":        int(mrr),
                "net_profit": int(net),
                "growth_pct": round(growth * 100, 1),
            })
        return projection


# =============================================================================
# ELITE AI SQUAD — ORCHESTRATOR
# =============================================================================
class EliteAISquad:
    """
    Orchestrator pusat 10 Elite AI Agent V-Guard.

    Agent ID → Class Mapping:
      1  → AgentVisionary    (Mata — CCTV)
      2  → AgentConcierge    (Telinga — CS)
      3  → AgentGrowthHacker (Mulut — Marketing)
      4  → AgentLiaison      (Tangan — POS/Filter)
      5  → AgentAnalyst      (Otak Audit — Bank)
      6  → AgentStockmaster  (Gudang — Inventory)
      7  → AgentWatchdog     (Otak Bisnis — Fraud)
      8  → AgentSentinel     (Imun Fisik — Server)
      9  → AgentLegalist     (Imun Hukum — Compliance)
      10 → AgentTreasurer    (Kantong — Finance)
    """

    def __init__(self):
        self.agents = {
            1:  AgentVisionary(),
            2:  AgentConcierge(),
            3:  AgentGrowthHacker(),
            4:  AgentLiaison(),
            5:  AgentAnalyst(),
            6:  AgentStockmaster(),
            7:  AgentWatchdog(),
            8:  AgentSentinel(),
            9:  AgentLegalist(),
            10: AgentTreasurer(),
        }
        self._boot_time = datetime.datetime.now()

    def agent(self, agent_id: int) -> VGuardAgent:
        return self.agents.get(agent_id)

    def kill(self, agent_id: int):
        st.session_state.setdefault("agent_kill_switch",{})[agent_id] = True

    def restart(self, agent_id: int):
        st.session_state.setdefault("agent_kill_switch",{})[agent_id] = False

    def get_all_status(self) -> list:
        return [
            {**agent.get_status(),
             "uptime": str(datetime.datetime.now() - self._boot_time).split(".")[0]}
            for _, agent in self.agents.items()
        ]

    def health_report(self) -> dict:
        statuses = self.get_all_status()
        return {
            "total_agents":  10,
            "active":        sum(1 for s in statuses if s["status"] == "ACTIVE"),
            "killed":        sum(1 for s in statuses if s["status"] == "KILLED"),
            "uptime":        str(datetime.datetime.now() - self._boot_time).split(".")[0],
            "last_heartbeat":st.session_state.get("last_heartbeat","—"),
        }

    def run_fraud_pipeline(self, pos_df: pd.DataFrame,
                           cctv_frames: list = None, ai_model=None) -> dict:
        """
        Full fraud detection pipeline:
        Liaison (#4) → Visionary (#1) → Watchdog (#7) → WA alarm

        Hanya anomali yang naik ke Watchdog.
        Watchdog eskalasi ke cloud AI hanya jika risk >= HIGH.
        → Hemat 80%+ API cost.
        """
        # Step 1: Liaison — filter lokal 6 rules
        liaison_result = self.agents[4].run(pos_df)
        anomalies      = liaison_result.get("anomalies", pd.DataFrame())

        # Step 2: Visionary — CCTV cross-check
        yolo_results = []
        if cctv_frames:
            yolo_results = self.agents[1].process_batch(cctv_frames, anomalies)

        # Step 3: Watchdog — risk score + cloud decision
        watchdog_result = self.agents[7].run(anomalies, ai_model)

        # Step 4: Build WA alarm links
        wa_links = []
        for alert in watchdog_result.get("alerts",[]):
            link = self._build_alarm_link(
                alert.get("kasir","—"), alert.get("cabang","—"),
                alert.get("jumlah",0),  alert.get("reason","FRAUD")
            )
            wa_links.append({"alert": alert, "wa_link": link})

        return {
            "liaison":   liaison_result,
            "yolo":      yolo_results,
            "watchdog":  watchdog_result,
            "wa_links":  wa_links,
            "api_saved": liaison_result.get("stats",{}).get("clean",0),
        }

    def run_daily_ops(self, db_klien: list) -> dict:
        """
        Operasi harian terjadwal:
        Legalist (#9) + Sentinel (#8) + Treasurer (#10) + GrowthHacker (#3)
        """
        sentinel  = self.agents[8].run()
        legalist  = self.agents[9].run(db_klien, sentinel.get("metrics",{}))
        treasurer = self.agents[10].run(db_klien)
        growth    = self.agents[3].run(leads=st.session_state.get("concierge_leads",[]))
        return {
            "sentinel":  sentinel,
            "legalist":  legalist,
            "treasurer": treasurer,
            "growth":    growth,
            "run_at":    datetime.datetime.now().strftime("%H:%M:%S"),
        }

    def _build_alarm_link(self, kasir: str, cabang: str,
                          amount: float, reason: str) -> str:
        msg = (
            f"🚨 *ALERT V-GUARD AI*\n\n"
            f"📍 Cabang: {cabang}\n👤 Kasir: {kasir}\n"
            f"💰 Jumlah: Rp {amount:,.0f}\n⚠️ Alasan: {reason}\n"
            f"🕐 Waktu: {datetime.datetime.now().strftime('%H:%M:%S WIB')}\n\n"
            f"Segera cek rekaman CCTV!\n— AgentWatchdog V-Guard"
        )
        return f"https://wa.me/{WA_NUMBER}?text={urllib.parse.quote(msg)}"


# =============================================================================
# SINGLETON
# =============================================================================
_squad_instance: EliteAISquad = None


def get_squad() -> EliteAISquad:
    """
    Get atau buat singleton EliteAISquad.
    Ini yang dipanggil di app.py:
      from logic_vguard import get_squad
      squad = get_squad()
    """
    global _squad_instance
    if _squad_instance is None:
        _squad_instance = EliteAISquad()
    return _squad_instance


def get_squad_status() -> list:
    return get_squad().get_all_status()


def run_fraud_scan(pos_df: pd.DataFrame, ai_model=None) -> dict:
    return get_squad().run_fraud_pipeline(pos_df, ai_model=ai_model)


def score_lead(user_message: str, history: list = None) -> dict:
    return get_squad().agent(2).run(user_message, history)


def check_inventory() -> dict:
    return get_squad().agent(6).run(action="check")


# =============================================================================
# LEGACY WRAPPERS — 100% backward compatible dengan app.py
# Tidak perlu ubah satu baris pun di app.py
# =============================================================================

def get_sample_transaksi() -> pd.DataFrame:
    now = datetime.datetime.now()
    return pd.DataFrame({
        "ID_Transaksi": ["TRX-001","TRX-002","TRX-003","TRX-004",
                          "TRX-005","TRX-006","TRX-007","TRX-008"],
        "Cabang":       ["Outlet Sudirman","Outlet Sudirman","Resto Central",
                         "Cabang Tangerang","Outlet Sudirman","Resto Central",
                         "Cabang Tangerang","Outlet Sudirman"],
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
        "Status":       ["VOID","NORMAL","NORMAL","NORMAL",
                         "VOID","NORMAL","NORMAL","NORMAL"],
        "Saldo_Fisik":  [0,150000,480000,200000,0,300000,45000,75000],
        "Saldo_Sistem": [150000,150000,500000,200000,150000,300000,50000,75000],
    })


def fetch_pos_data(api_url: str = "http://localhost:8080/api/transactions",
                   api_key: str = "") -> pd.DataFrame:
    return get_sample_transaksi()


def scan_fraud_lokal(df: pd.DataFrame) -> dict:
    """Legacy wrapper → AgentLiaison. app.py tidak perlu diubah."""
    result    = get_squad().agent(4).run(df)
    anomalies = result.get("anomalies", pd.DataFrame())

    void_df = df[df["Status"]=="VOID"].copy() if "Status" in df.columns else pd.DataFrame()

    if not anomalies.empty and all(c in anomalies.columns for c in ["Kasir","Jumlah","Waktu"]):
        df_s = anomalies.sort_values(["Kasir","Jumlah","Waktu"]).copy()
        df_s["selisih_menit"] = (
            df_s.groupby(["Kasir","Jumlah"])["Waktu"]
            .diff().dt.total_seconds().div(60)
        )
        fraud_df = df_s[df_s["selisih_menit"] < 5].copy()
    else:
        fraud_df = pd.DataFrame()

    if "Saldo_Fisik" in df.columns and "Saldo_Sistem" in df.columns:
        df2 = df.copy()
        df2["selisih_saldo"] = df2["Saldo_Sistem"] - df2["Saldo_Fisik"]
        sus_df = df2[df2["selisih_saldo"] != 0].copy()
    else:
        sus_df = pd.DataFrame()

    return {"void": void_df, "fraud": fraud_df, "suspicious": sus_df}


def trigger_alarm(reason: str, kasir: str, cabang: str,
                  amount: float, wa_owner: str = WA_NUMBER) -> str:
    """Legacy wrapper — dipakai di app.py."""
    return get_squad()._build_alarm_link(kasir, cabang, amount, reason)


def check_ai_fraud_alarm(pos_df: pd.DataFrame, yolo_results: list) -> list:
    """Legacy wrapper — dipakai di app.py."""
    void_rows = pos_df[pos_df["Status"]=="VOID"] if "Status" in pos_df.columns else pos_df
    alarms = []
    for _, row in void_rows.iterrows():
        for yolo in yolo_results:
            if yolo.get("alert"):
                alarms.append({
                    "kasir":     row.get("Kasir","—"),
                    "cabang":    row.get("Cabang","—"),
                    "jumlah":    float(row.get("Jumlah",0)),
                    "reason":    "VOID + CCTV: " + yolo.get("alert_reason",""),
                    "camera_id": yolo.get("camera_id","—"),
                })
    return alarms


def check_autobilling_reminders(db_klien: list) -> list:
    """Legacy wrapper — dipakai di app.py."""
    today     = datetime.date.today()
    reminders = []
    for k in db_klien:
        due_str = k.get("invoice_due_date","")
        if not due_str:
            continue
        try:
            due   = datetime.date.fromisoformat(due_str)
            delta = (due - today).days
            if delta in (7, 3, 1):
                wa = k.get("WhatsApp","")
                if wa and not wa.startswith("62"):
                    wa = "62" + wa.lstrip("0")
                urgency = "CRITICAL" if delta <= 1 else "WARNING" if delta <= 3 else "NORMAL"
                due_info = "BESOK!" if delta == 1 else f"dalam {delta} hari"
                msg = (
                    f"{'🚨 URGENT — ' if delta <= 1 else '⏰ '}PENGINGAT INVOICE V-GUARD AI\n\n"
                    f"Yth. {k.get('Nama Klien','')},\n\n"
                    f"Invoice paket {k.get('Produk','')} jatuh tempo {due_str} ({due_info}).\n\n"
                    f"Transfer: BCA 3450074658 a/n Erwin Sinaga\n— Tim V-Guard AI"
                )
                reminders.append({
                    "nama":    k.get("Nama Klien","—"),
                    "usaha":   k.get("Nama Usaha","—"),
                    "wa":      k.get("WhatsApp",""),
                    "paket":   k.get("Produk","V-LITE"),
                    "due":     due_str,
                    "delta":   delta,
                    "cid":     k.get("Client_ID","—"),
                    "urgency": urgency,
                    "wa_link": f"https://wa.me/{wa}?text={urllib.parse.quote(msg)}" if wa else "",
                })
        except Exception:
            continue
    return reminders


def track_referral(ref_cid: str, new_client_data: dict, setup_amount: float):
    """Legacy wrapper — dipakai di app.py."""
    commission = int(setup_amount * KOMISI_RATE)
    st.session_state.setdefault("db_referrals",[]).append({
        "ref_cid":      ref_cid,
        "new_client":   new_client_data.get("Nama Klien","—"),
        "new_usaha":    new_client_data.get("Nama Usaha","—"),
        "paket":        new_client_data.get("Produk","V-LITE"),
        "setup_fee":    setup_amount,
        "komisi_10pct": commission,
        "status":       "Menunggu Konfirmasi",
        "tanggal":      str(datetime.date.today()),
    })


def process_yolo_cctv_frame(frame_data: dict) -> dict:
    """Legacy wrapper — dipakai di app.py."""
    return get_squad().agent(1).run(frame_data)
# ... (Kode AgentVisionary, AgentLiaison, dll yang sudah ada)

