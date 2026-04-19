import streamlit as st
import datetime
import pandas as pd
import uuid


# =============================================================================
# INITIALIZATION (Menyiapkan Database Semua Agen)
# =============================================================================
def init_vguard_core():
    # Database Warroom, Vision & Logs
    if "warroom_db" not in st.session_state: st.session_state["warroom_db"] = []
    if "vision_logs" not in st.session_state: st.session_state["vision_logs"] = []
    if "audit_logs" not in st.session_state: st.session_state["audit_logs"] = []
    if "tickets_db" not in st.session_state: st.session_state["tickets_db"] = []
    
    # Database Inventaris (Agen #6 Stockmaster)
    if "inventory_db" not in st.session_state: 
        st.session_state["inventory_db"] = {"Premium Coffee": 100, "V-Guard Device": 50, "CCTV Kit": 30}
    
    # Status Keuangan & Koneksi
    if "total_loss" not in st.session_state: st.session_state["total_loss"] = 0.0
    if "last_heartbeat" not in st.session_state: st.session_state["last_heartbeat"] = datetime.datetime.now()
    if "client_billing_status" not in st.session_state: st.session_state["client_billing_status"] = "Paid"
    if "kyc_data" not in st.session_state: st.session_state["kyc_data"] = {"status": "Unverified"}

# =============================================================================
# AGEN #1: THE VISIONARY (Logika Integrasi YOLO & OCR)
# =============================================================================
def process_vision_ai(plate_number, vehicle_type):
    """Mencatat deteksi kendaraan ke Warroom Vision"""
    entry = {
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "plat": plate_number.upper(),
        "tipe": vehicle_type,
        "status": "Logged"
    }
    st.session_state.vision_logs.append(entry)
    log_audit_trail("VEHICLE_DETECTED", "Visionary_AI", f"Plat: {plate_number}")
    return entry

# =============================================================================
# AGEN #2: THE CONCIERGE (Pusat Bantuan & Onboarding)
# =============================================================================
def render_concierge_ui():
    """Fungsi tampilan untuk dipanggil di app.py"""
    st.header("🛎️ Agen #2: The Concierge")
    if not check_access_control():
        st.error("⚠️ AKSES DITANGGUHKAN - Harap selesaikan administrasi.")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Bantuan & Tiket")
        with st.form("ticket_form"):
            subject = st.text_input("Subjek Masalah")
            msg = st.text_area("Deskripsi Kendala")
            if st.form_submit_button("Kirim Tiket"):
                t_id = f"TIX-{str(uuid.uuid4())[:5].upper()}"
                st.session_state.tickets_db.append({"id": t_id, "sub": subject, "status": "Open"})
                st.success(f"Tiket {t_id} berhasil dikirim!")

# =============================================================================
# AGEN #3: THE GROWTH HACKER (Referral Tiering System)
# =============================================================================
def get_growth_hacker_stats():
    """Menghitung statistik mitra sesuai Poin C Master Prompt"""
    data = [
        {"mitra": "Andi_Ref", "count": 12},
        {"mitra": "Budi_Vguard", "count": 65},
        {"mitra": "Siska_Growth", "count": 5}
    ]
    processed = []
    for m in data:
        tier, bonus = calculate_referral_tier(m["count"])
        processed.append({
            "Mitra": m["mitra"], 
            "Total Klien": m["count"], 
            "Rank": tier, 
            "Komisi": bonus
        })
    return pd.DataFrame(processed)

def calculate_referral_tier(count):
    if count > 50: return "Gold 👑", "10%"
    elif count > 10: return "Silver 🥈", "5%"
    return "Bronze 🥉", "0%"

# =============================================================================
# AGEN #4, #5, #7: DATA BRIDGE, ANALYST & WATCHDOG
# =============================================================================
def process_data_bridge(client_id, trans_type, amount, item_name, timestamp):
    """Integrasi Liaison ke Analyst, Watchdog, dan Stockmaster"""
    new_entry = {
        "client_id": client_id, "type": trans_type, "amount": amount,
        "item": item_name, "timestamp": timestamp,
        "processed_at": datetime.datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.warroom_db.append(new_entry)

    # Sinkronisasi Stok (Agen #6 Stockmaster)
    if trans_type == "SALE" and item_name in st.session_state.inventory_db:
        st.session_state.inventory_db[item_name] -= 1

    # Sinkronisasi CCTV (Agen #7 Watchdog)
    if trans_type in ["VOID", "REFUND"]:
        st.session_state.total_loss += float(amount)
        st.toast(f"📹 [WATCHDOG] Anomali! Sinkronisasi CCTV: {timestamp}", icon="🔍")

# =============================================================================
# AGEN #6: THE STOCKMASTER (Inventory Control)
# =============================================================================
def get_inventory_status():
    return pd.DataFrame(list(st.session_state.inventory_db.items()), columns=['Produk', 'Sisa Stok'])

# =============================================================================
# AGEN #8, #9, #10: SECURITY, LEGAL & BILLING
# =============================================================================
def check_access_control():
    return st.session_state.client_billing_status != "Unpaid"

def log_audit_trail(action, actor, reason):
    st.session_state.audit_logs.append({
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action, "actor": actor, "reason": reason
    })

def monitor_heartbeat_status():
    diff = (datetime.datetime.now() - st.session_state.last_heartbeat).total_seconds()
    if diff > 3600:
        return "CRITICAL (🔴) - Sentinel sending WA Alert..."
    return "ONLINE (🟢)"
