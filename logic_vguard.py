import streamlit as st
import datetime
import pandas as pd
import uuid

# =============================================================================
# INITIALIZATION (Menyiapkan Database Sementara)
# =============================================================================
def init_vguard_core():
    if "warroom_db" not in st.session_state: st.session_state["warroom_db"] = []
    if "total_loss" not in st.session_state: st.session_state["total_loss"] = 0.0
    if "last_heartbeat" not in st.session_state: st.session_state["last_heartbeat"] = datetime.datetime.now()
    if "audit_logs" not in st.session_state: st.session_state["audit_logs"] = []
    if "client_billing_status" not in st.session_state: st.session_state["client_billing_status"] = "Paid"
    if "kyc_data" not in st.session_state: st.session_state["kyc_data"] = {}

# =============================================================================
# 1. INFRASTRUKTUR DATA & SYNC ENGINE (Agen #4 Liaison, #5 Analyst, #7 Watchdog)
# =============================================================================
def process_data_bridge(client_id, trans_type, amount, timestamp):
    """Menerima data JSON dan update Warroom [cite: 3, 4, 5, 6]"""
    new_entry = {
        "client_id": client_id,
        "type": trans_type,
        "amount": amount,
        "timestamp": timestamp,
        "processed_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.warroom_db.append(new_entry)

    # Sinkronisasi ke Agen #7 jika ada Void/Refund [cite: 5, 63]
    if trans_type in ["VOID", "REFUND"]:
        st.session_state.total_loss += float(amount)
        st.toast(f"📹 [WATCHDOG] Mapping CCTV otomatis untuk timestamp: {timestamp}", icon="🔍")

# =============================================================================
# 2. MANAJEMEN AKTIVASI & KYC (Agen #9 Legalist, #10 Treasurer)
# =============================================================================
def generate_activation_key():
    """Membuat Key unik untuk klien baru [cite: 7, 8]"""
    return f"VG-{str(uuid.uuid4())[:8].upper()}"

def save_kyc_data(name, business, address):
    """Menyimpan data identitas klien di Portal [cite: 9, 10]"""
    st.session_state.kyc_data = {
        "owner": name,
        "business": business,
        "address": address,
        "status": "Verified"
    }
    log_audit_trail("KYC_SUBMISSION", name, "Initial registration and verification")

# =============================================================================
# 7. SAAS BILLING & AUTO-LOCK SYSTEM (Agen #10 Treasurer)
# =============================================================================
def check_access_control():
    """Mengunci dashboard jika pembayaran jatuh tempo [cite: 27, 28, 29, 30]"""
    if st.session_state.client_billing_status == "Unpaid":
        return False # Ini akan memicu overlay 'Akses Ditangguhkan' di app.py
    return True

# =============================================================================
# A. AUDIT TRAIL SNAPSHOT (Bukti Hukum Permanen)
# =============================================================================
def log_audit_trail(action, actor, reason):
    """Mencatat perubahan status krusial (Logika Asli) [cite: 51, 52, 53]"""
    snapshot = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "actor": actor,
        "reason": reason,
        "id": str(uuid.uuid4())[:6]
    }
    st.session_state.audit_logs.append(snapshot)

# =============================================================================
# B. PROACTIVE FAILURE HANDLING (Agen #8 Sentinel)
# =============================================================================
def monitor_heartbeat_status():
    """Cek koneksi kasir, notifikasi jika > 1 jam terputus [cite: 18, 54, 55]"""
    time_diff = (datetime.datetime.now() - st.session_state.last_heartbeat).total_seconds()
    if time_diff > 3600:
        return "CRITICAL (🔴) - Sentinel sending WA Alert..."
    return "ONLINE (🟢)"

# =============================================================================
# C. TIERED REFERRAL SYSTEM (Agen #3 Growth Hacker)
# =============================================================================
def calculate_referral_tier(count):
    """Menentukan tingkat komisi mitra [cite: 57, 58, 59, 60, 61, 62]"""
    if count > 50:
        return "Tier 3 (Gold) 👑 - Bonus +10%"
    elif count > 10:
        return "Tier 2 (Silver) 🥈 - Bonus +5%"
    return "Tier 1 (Bronze) 🥉"
