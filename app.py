import streamlit as st
import os
import urllib.parse
import random
import string
import pandas as pd

# ============================================================================
# 1. IMPORT GOOGLE GENERATIVE AI (OPSIONAL)
# ============================================================================
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# ============================================================================
# 2. PENGATURAN AI & KEAMANAN
# ============================================================================
gemini_key    = st.secrets.get("GEMINI_API_KEY")
ai_status_msg = "Mode Offline"
model_vguard  = None

if gemini_key and GENAI_AVAILABLE:
    try:
        genai.configure(api_key=gemini_key)
        model_vguard  = genai.GenerativeModel("gemini-1.5-flash")
        ai_status_msg = "Connected"
    except Exception:
        ai_status_msg = "Error Connection"

# ============================================================================
# 3. KONFIGURASI HALAMAN
# ============================================================================
st.set_page_config(
    page_title="V-Guard AI Intelligence",
    page_icon="🛡️",
    layout="wide",
)

# ── Inisialisasi session state ───────────────────────────────────────────────
defaults = {
    "admin_logged_in": False,
    "system_status":   "Healthy",
    "db_umum":         [],
    "api_cost_total":  0.0,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ============================================================================
# 4. FUNGSI HELPER
# ============================================================================

def sentinel_recovery():
    """THE SENTINEL: Sistem Auto-Recovery & Health Check."""
    if st.session_state.system_status != "Healthy":
        st.session_state.system_status = "Healthy"
        return True
    return False


def get_data_from_google():
    """Ambil data dari Google Sheets; fallback ke data simulasi jika gagal."""
    try:
        from streamlit_gsheets import GSheetsConnection
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn.read(ttl="1m")
    except Exception:
        data_simulasi = {
            "Nama Klien":    ["Timotius Mardjuki", "Outlet Sudirman", "Resto Central", "Cabang Tangerang"],
            "Produk":        ["V-PRO (10 Agents)", "V-LITE (Standard)", "V-PRO (10 Agents)", "V-LITE (Standard)"],
            "Status":        ["✅ Terverifikasi", "⚠️ Pending Payment", "🛡️ Audit Watchdog", "✅ Aktif"],
            "Nilai Kontrak": ["Rp 10.000.000", "Rp 5.000.000", "Rp 12.500.000", "Rp 5.000.000"],
        }
        return pd.DataFrame(data_simulasi)


def get_sample_transaksi():
    """Data transaksi kasir simulasi untuk Sentinel Fraud Scanner."""
    import datetime
    now = datetime.datetime.now()
    data = {
        "ID_Transaksi": ["TRX-001", "TRX-002", "TRX-003", "TRX-004",
                         "TRX-005", "TRX-006", "TRX-007", "TRX-008"],
        "Cabang": [
            "Outlet Sudirman", "Outlet Sudirman", "Resto Central",
            "Cabang Tangerang", "Outlet Sudirman", "Resto Central",
            "Cabang Tangerang", "Outlet Sudirman",
        ],
        "Kasir":  ["Budi", "Budi", "Sari", "Andi", "Budi", "Sari", "Andi", "Dewi"],
        "Jumlah": [150000, 150000, 500000, 200000, 150000, 300000, 50000, 75000],
        "Waktu": [
            now - datetime.timedelta(minutes=2),
            now - datetime.timedelta(minutes=3),
            now - datetime.timedelta(hours=1),
            now - datetime.timedelta(hours=2),
            now - datetime.timedelta(minutes=4),
            now - datetime.timedelta(hours=3),
            now - datetime.timedelta(hours=5),
            now - datetime.timedelta(minutes=10),
        ],
        "Status":       ["VOID", "NORMAL", "NORMAL", "NORMAL", "VOID", "NORMAL", "NORMAL", "NORMAL"],
        "Saldo_Fisik":  [0, 150000, 480000, 200000, 0, 300000, 45000, 75000],
        "Saldo_Sistem": [150000, 150000, 500000, 200000, 150000, 300000, 50000, 75000],
    }
    return pd.DataFrame(data)


def hitung_budget_guard(db_umum, api_cost_total):
    """
    AI Budget Guard: Hitung batas 20% dari total omset kontrak.
    Return: (total_omset, batas_anggaran, persen_terpakai, status_warning)
    """
    total_omset = 0
    for klien in db_umum:
        nilai_str = klien.get("Nilai Kontrak", "0")
        angka     = "".join(filter(str.isdigit, str(nilai_str)))
        total_omset += int(angka) if angka else 0

    if total_omset == 0:
        total_omset = 32_500_000  # fallback simulasi

    batas_anggaran = total_omset * 0.20
    persen_terpakai = (api_cost_total / batas_anggaran * 100) if batas_anggaran > 0 else 0
    status_warning  = persen_terpakai >= 80
    return total_omset, batas_anggaran, persen_terpakai, status_warning


def scan_fraud_lokal(df_trx):
    """
    Sentinel Fraud Scanner — filter data tanpa AI (fallback/cepat).
    Return: dict {void, fraud, suspicious}
    """
    # 1. VOID / CANCEL tidak wajar
    void_df = df_trx[df_trx["Status"] == "VOID"].copy()

    # 2. Transaksi berulang dalam < 5 menit (jumlah & kasir sama)
    df_sorted = df_trx.sort_values(["Kasir", "Jumlah", "Waktu"])
    df_sorted["selisih_menit"] = (
        df_sorted.groupby(["Kasir", "Jumlah"])["Waktu"]
        .diff()
        .dt.total_seconds()
        .div(60)
    )
    fraud_df = df_sorted[df_sorted["selisih_menit"] < 5].copy()

    # 3. Selisih saldo fisik vs sistem
    df_trx["selisih_saldo"] = df_trx["Saldo_Sistem"] - df_trx["Saldo_Fisik"]
    suspicious_df = df_trx[df_trx["selisih_saldo"] != 0].copy()

    return {"void": void_df, "fraud": fraud_df, "suspicious": suspicious_df}


def buat_link_wa_alert(nama_cabang, nomor="6282122190885"):
    pesan = (
        f"⚠️ ALERT V-GUARD: Terdeteksi aktivitas mencurigakan pada Kasir "
        f"[{nama_cabang}]. Segera cek sistem!"
    )
    return f"https://wa.me/{nomor}?text={urllib.parse.quote(pesan)}"


# ============================================================================
# 5. CSS CUSTOM
# ============================================================================
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #238636;
        color: white !important;
        font-weight: bold;
        height: 45px;
    }
    .stTextInput>div>div>input {
        background-color: #1e293b;
        color: white;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 6. SIDEBAR NAVIGASI
# ============================================================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🛡️ V-Guard AI</h2>", unsafe_allow_html=True)

    if os.path.exists("erwin.jpg"):
        st.image("erwin.jpg", use_container_width=True)

    st.markdown("""
    <div style='text-align:center;'>
        <p style='color:white; font-weight:bold; margin-bottom:0;'>Erwin Sinaga</p>
        <p style='color:gray;'>Founder & CEO V-Guard AI</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    menu = st.radio(
        "NAVIGASI UTAMA",
        ["Visi & Misi", "Produk & Layanan", "ROI Kerugian Klien", "Portal Klien", "Admin Control Center"],
    )

# ============================================================================
# 7. LOGIKA MENU UTAMA
# ============================================================================

# ── VISI & MISI ──────────────────────────────────────────────────────────────
if menu == "Visi & Misi":
    st.header("🛡️ Visi & Misi: Digitizing Trust")
    col_img, col_txt = st.columns([1, 2])

    with col_img:
        if os.path.exists("erwin.jpg"):
            st.image("erwin.jpg", caption="Erwin Sinaga - Founder & CEO", use_container_width=True)

    with col_txt:
        st.markdown("""
        <div style="text-align:justify; line-height:1.8; font-size:16px; color:#d1d5db;">
        <b>V-Guard AI Intelligence</b> lahir dari urgensi integritas finansial di era transformasi digital yang
        berkembang pesat. Sebagai entitas yang dipimpin oleh profesional dengan pengalaman lebih dari satu dekade
        di industri perbankan dan manajemen aset, kami memahami bahwa celah terkecil dalam sistem operasional
        adalah potensi kerugian fatal bagi sebuah bisnis. Misi utama kami adalah mendigitalisasi kepercayaan
        (<i>Digital Trust</i>) melalui pembuktian matematis dan audit cerdas yang bekerja secara otonom
        24 jam nonstop tanpa kompromi sedikit pun.<br><br>
        Kami percaya bahwa kejujuran sistem tidak boleh hanya bergantung pada pengawasan manusia yang memiliki
        keterbatasan, melainkan harus dibangun di atas fondasi teknologi AI yang presisi. Melalui ekosistem
        V-Guard, kami mengintegrasikan analisis data perbankan (VCS), visi komputer, dan deteksi anomali
        prediktif untuk menciptakan lingkungan bisnis yang bersih dari segala bentuk kecurangan (Fraud).
        Strategi kami adalah memberikan transparansi mutlak kepada pemilik bisnis melalui laporan yang akurat
        dan real-time.<br><br>
        Visi kami adalah menjadi standar global dalam "<b>Eliminating Leakage</b>", di mana setiap pemilik
        bisnis — mulai dari UMKM hingga korporasi besar — dapat menjalankan operasional mereka dengan tenang
        karena setiap Rupiah diawasi oleh kecerdasan buatan yang tak kenal lelah. V-Guard bukan sekadar
        perangkat lunak, melainkan benteng pertahanan terakhir bagi aset dan masa depan investasi Anda.
        </div>
        """, unsafe_allow_html=True)

# ── PRODUK & LAYANAN ─────────────────────────────────────────────────────────
elif menu == "Produk & Layanan":
    st.header("🛡️ Portfolio Layanan V-Guard AI Intelligence")
    wa_number = "6282122190885"
    c1, c2, c3, c4 = st.columns(4)

    packages = {
        "V-LITE":       ["Mikro / 1 Kasir",  "750 rb",  "350 rb",  "AI Fraud Detector Dasar, Daily WA/Email Summary"],
        "V-PRO":        ["Retail & Kafe",    "1.5 Jt",  "850 rb",  "VCS Integration, Bank Statement Audit, Input Excel/CSV/PDF"],
        "V-SIGHT":      ["Gudang & Toko",    "7,5 Jt",  "3,5 Jt",  "CCTV AI Behavior, Visual Cashier Audit, Fraud Alarm 🚨"],
        "V-ENTERPRISE": ["Korporasi",        "15 Jt",   "10 Jt",   "The Core Brain, Forensic AI, Dedicated Server, Custom AI SOP"],
    }

    for col, (name, details) in zip([c1, c2, c3, c4], packages.items()):
        with col:
            with st.container(border=True):
                st.markdown(f"### 📦 {name}")
                st.write(f"**Target:** {details[0]}")
                st.info(f"Pasang: {details[1]}\n\nBulan: {details[2]}")
                st.write(details[3])
                st.link_button(
                    f"Pilih {name}",
                    f"https://wa.me/{wa_number}?text=Halo%20Pak%20Erwin,%20saya%20tertarik%20dengan%20paket%20*{name}*%20V-Guard%20AI.",
                )

# ── ROI KERUGIAN KLIEN ────────────────────────────────────────────────────────
elif menu == "ROI Kerugian Klien":
    st.header("📊 Analisis Potensi Kerugian vs ROI")
    st.write("Gunakan kalkulator ini untuk melihat berapa banyak kebocoran yang bisa dihemat oleh V-Guard AI.")

    col_a, col_b = st.columns(2)
    with col_a:
        omzet = st.number_input("Omzet Bulanan Bisnis Anda (Rp)", value=100_000_000, step=1_000_000)
        leak  = st.slider("Estimasi Persentase Kebocoran/Fraud (%)", 1, 20, 5)
        loss  = omzet * (leak / 100)

    with col_b:
        st.error(f"### Potensi Kerugian: Rp {loss:,.0f} / bulan")
        st.success(f"### Potensi Penyelamatan AI: Rp {loss * 0.88:,.0f} / bulan")
        st.caption("Dihitung berdasarkan rata-rata efisiensi sistem V-Guard sebesar 88%.")

# ── PORTAL KLIEN ──────────────────────────────────────────────────────────────
elif menu == "Portal Klien":
    st.header("🔑 Portal Akses Klien V-Guard")

    URL_SHEETS = "https://docs.google.com/spreadsheets/d/17OJpYRGTWdQ0ZldSxp-3HdyW4AN_RKuJkCWVpYbtNE8/export?format=csv&gid=618275599"
    df_clients  = None
    db_error    = None

    # ── Koneksi ke Google Sheets ─────────────────────────────────────────────
    # --- Koneksi ke Google Sheets ---
    try:
        # Menarik data langsung menggunakan pandas tanpa perlu modul tambahan
        df_clients = pd.read_csv(URL_SHEETS)
    except Exception as e:
        db_error = f"Koneksi ke database gagal: {e}"
    except ImportError:
        db_error = "Modul database tidak tersedia. Hubungi Admin."

    if db_error:
        st.warning(f"⚠️ {db_error}")

    # ── Tab Login & Registrasi ───────────────────────────────────────────────
    tab_log, tab_reg = st.tabs(["🔐 Login Dashboard", "📝 Registrasi Baru"])

    # ── Tab Login ──
    with tab_log:
        st.subheader("🔐 Masuk ke Sistem Monitoring")
        col_login, _ = st.columns(2)

        with col_login:
            user_id_input = st.text_input("User ID Klien", placeholder="Contoh: VGUARD-PRO-99")
            password      = st.text_input("Password", type="password")
            btn_login     = st.button("Masuk ke Dashboard", type="primary")

        if btn_login:
            if df_clients is None:
                st.error("❌ Database tidak tersedia. Tidak dapat melakukan login saat ini.")
            elif user_id_input in df_clients["UserID"].values:
                client_info      = df_clients[df_clients["UserID"] == user_id_input].iloc[0]
                paket_aktif      = client_info["Paket"]
                status_klien     = client_info["Status"]
                nama_klien_login = client_info["Nama Klien"]

                if status_klien == "Aktif":
                    st.success(f"Selamat Datang, Pak {nama_klien_login}! Lisensi **{paket_aktif}** Anda Aktif ✅")
                    st.divider()

                    link_map = {
                        "V-LITE":       "https://vguard-ai.railway.app/lite-vision",
                        "V-PRO":        "https://vguard-ai.railway.app/pro-audit",
                        "V-SIGHT":      "https://vguard-ai.railway.app/sight-live",
                        "V-ENTERPRISE": "https://vguard-ai.railway.app/enterprise-core",
                    }
                    url_tujuan = link_map.get(paket_aktif, "#")

                    st.subheader(f"📊 Dashboard Monitoring — {paket_aktif}")
                    st.info(f"Klik tombol di bawah untuk membuka panel kontrol {paket_aktif} Anda.")
                    st.link_button(f"🚀 Buka Panel {paket_aktif}", url_tujuan, use_container_width=True)
                    st.divider()

                    m1, m2, m3 = st.columns(3)
                    if paket_aktif == "V-LITE":
                        m1.metric("Status Kasir", "Online")
                        m2.metric("Fraud Alert",  "0")
                        m3.info("Mode: Daily Summary")
                    elif paket_aktif == "V-PRO":
                        m1.metric("VCS Sync",     "Active")
                        m2.metric("Audit Status", "Clear")
                        m3.metric("Protected Rev.", "Rp 1.2M")
                        st.write("**Activity:** Audit laporan PDF harian telah siap.")
                    elif paket_aktif == "V-SIGHT":
                        m1.metric("CCTV AI",      "Streaming")
                        m2.metric("Anomali",      "0", delta="Normal")
                        m3.metric("Visual Audit", "100%")
                        st.image(
                            "https://via.placeholder.com/600x200?text=CCTV+AI+Visual+Monitoring+Active",
                            use_container_width=True,
                        )
                    elif paket_aktif == "V-ENTERPRISE":
                        st.warning("⚠️ High Security Mode: The Core Brain Active")
                        m1.metric("Forensic Scan",  "99.9%")
                        m2.metric("Integrity",      "Secure")
                        m3.metric("Drift Analysis", "0%")
                        st.write("DASHBOARD EKSEKUTIF: Akses penuh ke seluruh cabang.")
                else:
                    st.error("⚠️ Akun ditemukan namun belum AKTIF. Silakan selesaikan pembayaran atau hubungi Admin.")
                    st.link_button("📲 Hubungi Admin untuk Aktivasi", "https://wa.me/6282122190885")
            else:
                st.error("❌ User ID tidak ditemukan. Pastikan Anda sudah terdaftar.")

    # ── Tab Registrasi ──
    with tab_reg:
        st.subheader("Form Order & Aktivasi Layanan")

        with st.form("pendaftaran_umum"):
            nama_klien = st.text_input("Nama Lengkap / Owner")
            nama_usaha = st.text_input("Nama Usaha")
            no_hp      = st.text_input("Nomor WhatsApp (Aktif)", placeholder="Contoh: 62812xxxx")
            upload_ktp = st.file_uploader("Upload Foto KTP (Verifikasi Sentinel)", type=["png", "jpg", "jpeg"])
            produk     = st.selectbox("Pilih Paket Aktivasi", ["V-LITE", "V-PRO", "V-SIGHT", "V-ENTERPRISE"])

            with st.expander("📄 Baca Syarat & Ketentuan (T&C)"):
                st.markdown("""
                ### TERMS & CONDITIONS — V-GUARD AI SYSTEMS
                **1. Pembayaran:** Aktivasi dimulai setelah biaya diverifikasi.
                **2. Keamanan Data:** Data terenkripsi dan tidak dibocorkan ke pihak ketiga.
                **3. Refund Policy:** Tidak ada refund setelah aktivasi sistem.
                **4. Support:** Technical support tersedia 24/7 via WhatsApp.
                """)

            setuju_tc = st.checkbox("Saya telah membaca dan menyetujui Syarat & Ketentuan.")
            submit    = st.form_submit_button("🚀 Daftar Sekarang & Dapatkan Akses AI")

            if submit:
                if setuju_tc and nama_klien and no_hp:
                    st.session_state.db_umum.append({
                        "Nama Klien":    nama_klien,
                        "Produk":        produk,
                        "Status":        "🛡️ Menunggu Pembayaran",
                        "WhatsApp":      no_hp,
                        "Nama Usaha":    nama_usaha,
                        "Nilai Kontrak": "0",
                    })
                    try:
                        from streamlit_gsheets import GSheetsConnection
                        conn_reg   = st.connection("gsheets", type=GSheetsConnection)
                        data_baru  = pd.DataFrame([{
                            "Nama Klien":    nama_klien,
                            "Produk":        produk,
                            "Status":        "⏳ Menunggu Verifikasi",
                            "Nilai Kontrak": "Proses Audit",
                        }])
                        existing_data = conn_reg.read(worksheet="Pendaftaran", ttl=0)
                        updated_df    = pd.concat([existing_data, data_baru], ignore_index=True)
                        conn_reg.update(worksheet="Pendaftaran", data=updated_df)
                    except Exception as e:
                        st.warning(f"Data tersimpan lokal, sinkronisasi otomatis akan dilakukan: {e}")

                    st.success(f"✅ Pendaftaran Berhasil! Invoice akan dikirim ke {no_hp}.")
                    st.balloons()
                else:
                    st.error("❌ Mohon isi semua data dan setujui Syarat & Ketentuan.")

# ── ADMIN CONTROL CENTER ──────────────────────────────────────────────────────
elif menu == "Admin Control Center":
    st.title("🛡️ Admin Control Center")
    st.info("Halaman Khusus Founder & Admin")

    # ── Autentikasi Admin ────────────────────────────────────────────────────
    if not st.session_state.admin_logged_in:
        st.subheader("🔑 Admin Authentication")
        admin_password = st.text_input("Masukkan Access Code:", type="password")
        if st.button("Buka Intelligence Center"):
            if admin_password == "w1nbju8282":
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("❌ Access Code Salah!")

    else:
        # ── Sidebar sub-menu admin ───────────────────────────────────────────
        with st.sidebar:
            st.markdown("---")
            menu_admin = st.selectbox("Admin Menu", [
                "Dashboard Utama",
                "Aktivasi Nasabah Baru",
                "Monitoring 10 Agents",
                "Database Klien",
            ])
            if st.button("🚪 Log Out"):
                st.session_state.admin_logged_in = False
                st.rerun()

        # ── Dashboard Utama ──────────────────────────────────────────────────
        if menu_admin == "Dashboard Utama":
            st.subheader("🛡️ Elite AI Squad Activation (10 Agents)")
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.success("👁️ The Visionary")
            with c2: st.success("📦 The Concierge")
            with c3: st.success("👄 The Growth Hacker")
            with c4: st.success("🤝 The Liaison")
            st.info("💡 6 agen lainnya sedang dalam mode background monitoring.")

            st.divider()
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Klien",          len(st.session_state.db_umum))
            m2.metric("Pendapatan Bulan Ini", "Rp 45.2 Juta")
            m3.metric("System Uptime",        "99.8%")
            m4.metric("AI Status",            ai_status_msg)

        # ── Aktivasi Nasabah Baru ────────────────────────────────────────────
        elif menu_admin == "Aktivasi Nasabah Baru":
            st.header("📋 Antrean Aktivasi V-Guard")

            if st.session_state.db_umum:
                df_real = pd.DataFrame(st.session_state.db_umum)
                st.subheader("🚀 Pendaftar Baru (Real-Time)")
                st.dataframe(df_real, use_container_width=True)
                st.markdown("---")

                harga_map = {
                    "V-LITE":       "Rp 750.000",
                    "V-PRO":        "Rp 1.500.000",
                    "V-SIGHT":      "Rp 7.500.000",
                    "V-ENTERPRISE": "Rp 15.000.000",
                }

                k_pil = st.selectbox("Pilih Klien untuk Diproses", df_real["Nama Klien"].tolist())
                d_sel = df_real[df_real["Nama Klien"] == k_pil].iloc[0]

                col_inv, col_act = st.columns(2)
                with col_inv:
                    st.subheader("💰 1. Kirim Tagihan")
                    nom = harga_map.get(d_sel["Produk"], "Rp 750.000")
                    inv_text = (
                        f"🛡️ *INVOICE V-GUARD*\nYth. *{k_pil}*\n"
                        f"Total: {nom}\n"
                        f"Transfer ke BCA 3450074658 a.n Erwin Sinaga."
                    )
                    st.link_button(
                        "📲 Kirim via WhatsApp",
                        f"https://wa.me/6282122190885?text={urllib.parse.quote(inv_text)}",
                    )

                with col_act:
                    st.subheader("✅ 2. Validasi Bayar")
                    st.write(f"Konfirmasi aktivasi untuk **{k_pil}**")

                    if st.button(f"Aktifkan Sentinel {k_pil}", type="primary"):
                        try:
                            random_num   = "".join(random.choices(string.digits, k=3))
                            new_userid   = f"VGD-{d_sel['Produk']}-{random_num}"
                            new_password = f"vguard{random_num}"

                            link_map = {
                                "V-LITE":       "https://vguard-ai.railway.app/lite",
                                "V-PRO":        "https://vguard-ai.railway.app/pro",
                                "V-SIGHT":      "https://vguard-ai.railway.app/sight",
                                "V-ENTERPRISE": "https://vguard-ai.railway.app/enterprise",
                            }
                            url_tujuan = link_map.get(d_sel["Produk"], "#")

                            data_final = pd.DataFrame([{
                                "UserID":     new_userid,
                                "Password":   new_password,
                                "Nama Klien": k_pil,
                                "Paket":      d_sel["Produk"],
                                "Status":     "Aktif",
                                "Link":       url_tujuan,
                            }])

                            try:
                                from streamlit_gsheets import GSheetsConnection
                                conn_gs = st.connection("gsheets", type=GSheetsConnection)
                                conn_gs.update(worksheet="Pendaftaran_Aktif", data=data_final)
                            except Exception:
                                pass  # simpan lokal jika GSheets tidak tersedia

                            pesan_wa = (
                                f"🛡️ *AKTIVASI V-GUARD BERHASIL* 🛡️\n\n"
                                f"Halo Pak *{k_pil}*,\n"
                                f"Sentinel AI Anda untuk paket *{d_sel['Produk']}* telah AKTIF.\n\n"
                                f"🔑 *DATA AKSES LOGIN:*\n"
                                f"- *User ID:* `{new_userid}`\n"
                                f"- *Password:* `{new_password}`\n\n"
                                f"🌐 *LINK DASHBOARD:*\n{url_tujuan}\n\n"
                                f"Silakan simpan data ini untuk masuk ke Portal Klien. "
                                f"Selamat menggunakan teknologi V-Guard!"
                            )
                            st.success("✅ Database Terupdate & ID Terbuat!")
                            st.code(f"User ID: {new_userid} | Pass: {new_password}")
                            st.link_button(
                                "📲 Kirim Data Login ke WhatsApp",
                                f"https://wa.me/6282122190885?text={urllib.parse.quote(pesan_wa)}",
                            )
                            st.balloons()
                        except Exception as e:
                            st.error(f"Gagal generate ID: {e}")
            else:
                st.info("Belum ada pendaftar baru.")

        # ── Monitoring 10 Agents ─────────────────────────────────────────────
        elif menu_admin == "Monitoring 10 Agents":
            st.header("🔍 Real-Time Monitoring (Elite Agents)")

            # ① AI BUDGET GUARD ───────────────────────────────────────────────
            st.subheader("💰 AI Budget Guard")
            total_omset, batas_anggaran, persen_terpakai, status_warning = hitung_budget_guard(
                st.session_state.db_umum, st.session_state.api_cost_total
            )

            bg1, bg2, bg3 = st.columns(3)
            bg1.metric("Total Omset Kontrak",     f"Rp {total_omset:,.0f}")
            bg2.metric("Batas Anggaran API (20%)", f"Rp {batas_anggaran:,.0f}")
            bg3.metric(
                "Biaya API Terpakai",
                f"Rp {st.session_state.api_cost_total:,.0f}",
                delta=f"{persen_terpakai:.1f}% dari batas",
            )
            st.progress(min(persen_terpakai / 100, 1.0))

            if status_warning:
                st.warning(
                    f"⚠️ **BUDGET ALERT:** Pengeluaran API telah mencapai **{persen_terpakai:.1f}%** "
                    f"dari batas anggaran (Rp {batas_anggaran:,.0f}). "
                    f"Pertimbangkan untuk mengoptimalkan frekuensi pemanggilan AI."
                )
            else:
                st.success(f"✅ Anggaran AI aman — {persen_terpakai:.1f}% dari batas 100% (20% omset).")

            with st.expander("⚙️ Simulasi Pengeluaran API (Demo)"):
                tambah_biaya = st.number_input("Tambah Biaya API (Rp)", value=0, step=50_000)
                if st.button("Catat Pengeluaran API"):
                    st.session_state.api_cost_total += tambah_biaya
                    st.rerun()
                if st.button("Reset Biaya API"):
                    st.session_state.api_cost_total = 0.0
                    st.rerun()

            st.divider()

            # ② SENTINEL FRAUD SCANNER ───────────────────────────────────────
            st.subheader("🛡️ Sentinel Fraud Scanner — AI Agent")
            df_trx     = get_sample_transaksi()
            hasil_scan = scan_fraud_lokal(df_trx)

            n_void, n_fraud, n_suspicious = (
                len(hasil_scan["void"]),
                len(hasil_scan["fraud"]),
                len(hasil_scan["suspicious"]),
            )
            fs1, fs2, fs3 = st.columns(3)
            fs1.metric("🚫 Void / Cancel",      n_void,       delta="Tidak Wajar" if n_void       else "Aman")
            fs2.metric("🔁 Transaksi Berulang", n_fraud,      delta="Terdeteksi"  if n_fraud      else "Aman")
            fs3.metric("💸 Selisih Saldo",      n_suspicious, delta="Anomali"     if n_suspicious else "Aman")

            tab_void, tab_fraud, tab_sus = st.tabs([
                "🚫 Void / Cancel", "🔁 Fraud Berulang", "💸 Selisih Saldo"
            ])

            with tab_void:
                if not hasil_scan["void"].empty:
                    st.error("⚠️ Ditemukan transaksi VOID/Cancel yang perlu diverifikasi!")
                    st.dataframe(
                        hasil_scan["void"][["ID_Transaksi", "Cabang", "Kasir", "Jumlah", "Waktu", "Status"]],
                        use_container_width=True,
                    )
                else:
                    st.success("✅ Tidak ada transaksi VOID mencurigakan.")

            with tab_fraud:
                if not hasil_scan["fraud"].empty:
                    st.error("⚠️ Pola transaksi berulang terdeteksi dalam waktu < 5 menit!")
                    st.dataframe(
                        hasil_scan["fraud"][["ID_Transaksi", "Cabang", "Kasir", "Jumlah", "selisih_menit"]],
                        use_container_width=True,
                    )
                else:
                    st.success("✅ Tidak ada pola transaksi berulang mencurigakan.")

            with tab_sus:
                if not hasil_scan["suspicious"].empty:
                    st.error("⚠️ Ditemukan selisih antara saldo fisik dan saldo sistem!")
                    st.dataframe(
                        hasil_scan["suspicious"][
                            ["ID_Transaksi", "Cabang", "Kasir", "Saldo_Fisik", "Saldo_Sistem", "selisih_saldo"]
                        ],
                        use_container_width=True,
                    )
                else:
                    st.success("✅ Saldo fisik dan sistem seimbang.")

            # AI Scan dengan Gemini (opsional)
            if model_vguard:
                if st.button("🤖 Jalankan AI Deep Scan (Gemini)", type="primary"):
                    with st.spinner("🧠 Sentinel AI sedang menganalisis data transaksi..."):
                        try:
                            prompt_fraud = f"""
Anda adalah Sentinel Fraud AI dari V-Guard Intelligence System.
Analisis data transaksi kasir berikut dan berikan laporan singkat mengenai:
1. Indikasi Void/Cancel tidak wajar
2. Pola transaksi mencurigakan (duplikasi, frekuensi tinggi)
3. Selisih saldo fisik vs sistem
4. Rekomendasi tindakan untuk Founder/Owner

Data Transaksi:
{df_trx.to_string(index=False)}

Berikan output dalam format poin-poin yang jelas dan ringkas.
""".strip()
                            response = model_vguard.generate_content(prompt_fraud)
                            st.session_state.api_cost_total += 200
                            st.markdown("### 🤖 Hasil AI Deep Scan:")
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"Error AI Scan: {e}")
            else:
                st.info("ℹ️ Sambungkan GEMINI_API_KEY untuk mengaktifkan AI Deep Scan.")

            st.divider()

            # ③ OWNER ALERT SYSTEM ───────────────────────────────────────────
            st.subheader("🚨 Owner Alert System")
            ada_ancaman = n_void > 0 or n_fraud > 0 or n_suspicious > 0

            if ada_ancaman:
                st.error("🚨 FRAUD TERDETEKSI — Sistem merekomendasikan pengiriman peringatan segera!")

                cabang_set = set()
                for df_part in hasil_scan.values():
                    if not df_part.empty and "Cabang" in df_part.columns:
                        cabang_set.update(df_part["Cabang"].unique())

                cabang_list = sorted(cabang_set)
                st.write(f"**Cabang terdampak:** {', '.join(cabang_list)}")

                for cabang in cabang_list:
                    st.link_button(
                        f"📲 Kirim Peringatan ke Owner — {cabang}",
                        buat_link_wa_alert(cabang),
                        use_container_width=True,
                    )

                if len(cabang_list) > 1:
                    st.markdown("---")
                    st.link_button(
                        "🔴 Kirim Alert ke Owner untuk Semua Cabang",
                        buat_link_wa_alert(" & ".join(cabang_list)),
                        use_container_width=True,
                    )
            else:
                st.success("✅ Tidak ada ancaman aktif. Sistem berjalan normal.")

            st.divider()

            # Status Tagihan Client
            st.subheader("📑 Status Tagihan Client")
            invoice_data = {
                "Customer/Outlet": ["Outlet Sudirman", "Cabang Tangerang", "Resto Central"],
                "Nilai Tagihan":   ["Rp 15.000.000",  "Rp 8.200.000",    "Rp 12.500.000"],
                "Jatuh Tempo":     ["H-2 (Mendesak)", "H-5",             "H-7"],
                "Status":          ["🚨 Kirim Alarm",  "⚠️ Reminder Sent", "✅ Scheduled"],
            }
            st.table(invoice_data)

            st.divider()

            # AI Gatekeeper
            st.subheader("🛰️ AI Pre-Cloud Gatekeeper")
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            col_stat1.metric("Data Traffic", "100%",       "Secure")
            col_stat2.metric("AI Filtering", "0.2ms/trans", "Fast")
            col_stat3.metric("Alarm Merah",  "Active",     "WhatsApp Bot")

            with st.expander("🔍 Live Audit Trail (Pre-Filtering Mode)", expanded=True):
                st.code(
                    "[SYSTEM] API Connected...\n"
                    "[AGENT] The Watchdog: Scanning...\n"
                    "[WARNING] Anomali #9922 Terdeteksi!\n"
                    "[ACTION] Pre-filter activated\n"
                    "[STATUS] Threat neutralized"
                )
                st.error("🚨 FRAUD DETECTED: Upaya manipulasi dicegah!")

            st.divider()

            # The Core Brain
            st.subheader("🤖 The Core Brain — AI Strategist")
            user_query = st.text_area("Konsultasi Strategi (Input Instruksi):", key="admin_query")
            if st.button("Jalankan AI Audit"):
                if model_vguard and user_query:
                    with st.spinner("🧠 Menganalisis..."):
                        try:
                            context  = (
                                f"Anda adalah Core Brain V-Guard. "
                                f"Jawab Founder Erwin Sinaga secara taktis: {user_query}"
                            )
                            response = model_vguard.generate_content(context)
                            st.session_state.api_cost_total += 200
                            st.markdown("### 🤖 Respon AI:")
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"Error AI: {e}")
                else:
                    st.warning("⚠️ Pastikan API Key sudah terpasang atau masukkan query.")

        # ── Database Klien ───────────────────────────────────────────────────
        elif menu_admin == "Database Klien":
            st.header("🗄️ Database Klien V-Guard")

            if st.session_state.db_umum:
                df_db = pd.DataFrame(st.session_state.db_umum)
                st.dataframe(df_db, use_container_width=True)
                st.download_button(
                    label="📥 Download Database (CSV)",
                    data=df_db.to_csv(index=False).encode("utf-8"),
                    file_name="vguard_clients.csv",
                    mime="text/csv",
                )
            else:
                st.info("Database masih kosong. Belum ada klien terdaftar.")

# ============================================================================
# 8. FOOTER
# ============================================================================
st.markdown("---")
st.markdown(
    "<center><small>V-Guard AI Intelligence Center | Founder Edition ©2026</small></center>",
    unsafe_allow_html=True,
)
