import streamlit as st
import datetime
import pandas as pd
import uuid

# =============================================================================
# INITIALIZATION
# =============================================================================
def init_vguard_core():
    if "warroom_db" not in st.session_state: st.session_state["warroom_db"] = []
    if "total_loss" not in st.session_state: st.session_state["total_loss"] = 0.0
    if "last_heartbeat" not in st.session_state: st.session_state["last_heartbeat"] = datetime.datetime.now()
    if "audit_logs" not in st.session_state: st.session_state["audit_logs"] = []
    if "client_billing_status" not in st.session_state: st.session_state["client_billing_status"] = "Paid"

# =============================================================================
# 1. INFRASTRUKTUR DATA & SYNC ENGINE (Agen #4, #5, #7)
# =============================================================================
def process_data_bridge(client_id, trans_type, amount, timestamp):
    new_entry = {
        "client_id": client_id,
        "type": trans_type,
        "amount": amount,
        "timestamp": timestamp,
        "processed_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.warroom_db.append(new_entry)

    if trans_type in ["VOID", "REFUND"]:
        st.session_state.total_loss += float(amount)
        # Agen #7 VisualEye Sync
        st.toast(f"📹 [WATCHDOG] Auto-Mapping CCTV: {timestamp}", icon="🔍")

# =============================================================================
# 7. SAAS BILLING & AUTO-LOCK SYSTEM (Agen #10)
# =============================================================================
def check_access_control():
    """Mengunci dashboard jika pembayaran Unpaid > 3 hari"""
    # Simulasi logika: Jika status Unpaid, kembalikan False untuk blokir UI
    if st.session_state.client_billing_status == "Unpaid":
        return False
    return True

# =============================================================================
# A. AUDIT TRAIL SNAPSHOT (The Legalist & Treasurer)
# =============================================================================
def log_audit_trail(action, actor, reason):
    """Mencatat perubahan status krusial secara permanen (bukti hukum)"""
    snapshot = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "actor": actor,
        "reason": reason,
        "log_id": str(uuid.uuid4())[:8]
    }
    st.session_state.audit_logs.append(snapshot)

# =============================================================================
# B. PROACTIVE FAILURE HANDLING (The Sentinel)
# =============================================================================
def monitor_liaison_connection():
    time_diff = (datetime.datetime.now() - st.session_state.last_heartbeat).total_seconds()
    if time_diff > 3600: # 1 Jam terputus
        return "CRITICAL: Connection Lost (🔴)"
    return "Stable (🟢)"

# =============================================================================
# C. TIERED REFERRAL SYSTEM (The Growth Hacker)
# =============================================================================
def get_referral_tier(client_count):
    if client_count > 50:
        return {"tier": "Gold 👑", "bonus": "10%", "color": "#ffd700"}
    elif client_count > 10:
        return {"tier": "Silver 🥈", "bonus": "5%", "color": "#c0c0c0"}
    else:
        return {"tier": "Bronze 🥉", "bonus": "0%", "color": "#cd7f32"}

# =============================================================================
# HELPERS
# =============================================================================
def get_warroom_summary():
    if not st.session_state.warroom_db:
        return pd.DataFrame()
    return pd.DataFrame(st.session_state.warroom_db)
