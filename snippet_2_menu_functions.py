# =============================================================================
# SNIPPET 2 — Ganti dua fungsi berikut di app.py:
#   def menu_visionary():   (sekitar baris 200–310 di versi Anda)
#   def menu_treasurer():   (sekitar baris 310–460 di versi Anda)
#
# Fungsi menu_liaison() TIDAK berubah — biarkan apa adanya.
#
# Dependensi yang harus sudah ada di app.py:
#   from logic_vguard import get_squad, check_autobilling_reminders
#   import pandas as pd, datetime, urllib.parse, streamlit as st
# =============================================================================


# ---------------------------------------------------------------------------
# AGENT #1 — VISIONARY (Mata — CCTV Visual Intelligence)
# ---------------------------------------------------------------------------
def menu_visionary():
    """
    UI untuk AgentVisionary (#1).
    Data bersumber dari:
      - visionary._log         → log internal agent
      - st.session_state["vision_logs"] → akumulasi hasil scan lintas session
    """
    squad     = get_squad()
    visionary = squad.agent(1)           # AgentVisionary

    # ── Header ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='padding:32px 48px 0;'>
        <div class='page-title'>
            👁️ AgentVisionary —
            <span style='color:#00d4ff;'>CCTV Visual Intelligence</span>
        </div>
        <div class='page-subtitle'>
            Agent #1 · Mata Sistem · Deteksi anomali visual kasir &amp;
            overlay transaksi real-time di atas feed CCTV.
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Status bar ──────────────────────────────────────────────────────────
    is_active    = visionary.is_active()
    status_color = "#00e676" if is_active else "#ff3b5c"
    status_label = (
        "ACTIVE — Mengawasi feed CCTV" if is_active
        else "KILLED — Tidak aktif · Restart dari Admin > AI Agents"
    )
    st.markdown(
        f"<div style='background:#101c2e;border:1px solid #1e3352;"
        f"border-left:3px solid {status_color};"
        f"border-radius:10px;padding:14px 20px;margin:16px 48px 0;"
        f"display:flex;align-items:center;justify-content:space-between;'>"
        f"<div>"
        f"  <span style='font-family:JetBrains Mono,monospace;font-size:10px;"
        f"  color:{status_color};text-transform:uppercase;letter-spacing:1.5px;'>"
        f"  ● {status_label}</span>"
        f"  <div style='font-size:12px;color:#7a9bbf;margin-top:4px;'>"
        f"  Model: YOLOv8-Custom · "
        f"  Labels: unscanned_item, void_gesture, cash_swap, item_concealment"
        f"  </div>"
        f"</div>"
        f"<div style='font-family:Rajdhani,sans-serif;font-size:13px;"
        f"font-weight:700;color:#7a9bbf;'>"
        f"  Agent log: {len(visionary._log)} entries"
        f"</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='padding:24px 48px;'>", unsafe_allow_html=True)

    # ── Kontrol ─────────────────────────────────────────────────────────────
    col_run, col_reset, col_filt = st.columns([1, 1, 2])
    with col_run:
        run_scan = st.button(
            "▶ Jalankan Batch Scan (Demo)",
            type="primary", key="vis_run", use_container_width=True,
        )
    with col_reset:
        clear_log = st.button(
            "🗑 Bersihkan Log",
            key="vis_clear", use_container_width=True,
        )
    with col_filt:
        filter_alert = st.toggle("Tampilkan hanya ALERT", key="vis_filter_alert")

    # ── Hapus log ────────────────────────────────────────────────────────────
    if clear_log:
        visionary._log.clear()
        st.session_state["vision_logs"] = []
        st.rerun()

    # ── Jalankan scan ────────────────────────────────────────────────────────
    if run_scan:
        if not is_active:
            st.error("AgentVisionary sedang di-kill. Restart dari Admin > AI Agents.")
        else:
            pos_df  = get_sample_transaksi()
            frames  = [
                {
                    "camera_id": f"cam_0{i + 1}",
                    "timestamp": str(datetime.datetime.now()),
                }
                for i in range(4)
            ]
            results = visionary.process_batch(frames, pos_df)
            st.session_state.setdefault("vision_logs", []).extend(results)
            alert_count = sum(1 for r in results if r.get("alert"))
            if alert_count:
                st.error(
                    f"⚠️ {alert_count} frame mengandung ALERT! "
                    f"Cek tabel di bawah dan kirim notifikasi ke Owner."
                )
            else:
                st.success(
                    f"✅ {len(results)} frame diproses — tidak ada anomali visual."
                )

    # ── Metrik ringkasan ─────────────────────────────────────────────────────
    vision_logs  = st.session_state.get("vision_logs", [])
    total_frames = len(vision_logs)
    total_alerts = sum(1 for v in vision_logs if v.get("alert"))
    total_normal = total_frames - total_alerts
    alert_rate   = (
        f"{total_alerts / total_frames * 100:.1f}%" if total_frames > 0 else "—"
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Frame Diproses", str(total_frames))
    m2.metric(
        "Alert Terdeteksi", str(total_alerts),
        delta="Butuh Tindakan" if total_alerts else None,
        delta_color="inverse" if total_alerts else "normal",
    )
    m3.metric("Frame Normal", str(total_normal))
    m4.metric("Alert Rate",   alert_rate)

    # ── Tabel log ────────────────────────────────────────────────────────────
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-family:Rajdhani,sans-serif;font-size:17px;"
        "font-weight:700;color:#e8f4ff;margin-bottom:10px;'>📋 Log Frame CCTV</div>",
        unsafe_allow_html=True,
    )

    if not vision_logs:
        st.info("Belum ada log. Klik 'Jalankan Batch Scan' untuk memulai.")
    else:
        display_logs = (
            [v for v in vision_logs if v.get("alert")]
            if filter_alert else vision_logs
        )
        if not display_logs:
            st.success("Tidak ada frame dengan ALERT dalam log saat ini.")
        else:
            rows = []
            for v in reversed(display_logs[-50:]):
                detect_labels = ", ".join(
                    d.get("label", "—") + f" ({d.get('confidence', 0):.0%})"
                    for d in v.get("detections", [])
                ) or "—"
                overlay_txt = v.get("overlay_text", "—")
                rows.append({
                    "Kamera":    v.get("camera_id", "—"),
                    "Timestamp": str(v.get("timestamp", "—"))[:19],
                    "Deteksi":   detect_labels,
                    "Alert":     "🔴 YA" if v.get("alert") else "🟢 Normal",
                    "Alasan":    v.get("alert_reason", "—") or "—",
                    "Overlay":   (
                        (overlay_txt[:60] + "…")
                        if len(overlay_txt) > 60 else overlay_txt
                    ),
                })
            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
            )

            # ── Tombol WA alert jika ada frame merah ────────────────────────
            if any(r["Alert"] == "🔴 YA" for r in rows):
                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                alert_msg = urllib.parse.quote(
                    f"🚨 V-GUARD VISIONARY ALERT\n\n"
                    f"Total alert  : {total_alerts} frame\n"
                    f"Alert rate   : {alert_rate}\n"
                    f"Waktu        : "
                    f"{datetime.datetime.now().strftime('%H:%M:%S WIB')}\n\n"
                    f"Segera cek rekaman CCTV!\n— AgentVisionary V-Guard"
                )
                st.link_button(
                    "📲 Kirim Semua Alert ke Owner via WhatsApp",
                    "https://wa.me/" + WA_NUMBER + "?text=" + alert_msg,
                )

    # ── Panduan label YOLO ───────────────────────────────────────────────────
    with st.expander("🔍 Panduan Label YOLO & Ambang Batas Deteksi"):
        st.markdown("""
| Label | Deskripsi | Confidence Min |
|---|---|---|
| `unscanned_item` | Barang tidak di-scan kasir | ≥ 0.75 |
| `void_gesture` | Gerakan void tidak wajar | ≥ 0.70 |
| `cash_swap` | Penukaran uang mencurigakan | ≥ 0.80 |
| `item_concealment` | Barang disembunyikan | ≥ 0.72 |
| `person` | Deteksi kehadiran orang (baseline) | ≥ 0.60 |

**Production:** Ganti `process_yolo_cctv_frame()` stub dengan inferensi
`ultralytics.YOLO` asli.  
**Frame rate:** Rekomendasi 1 frame / 2 detik untuk efisiensi biaya.
        """)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# AGENT #10 — TREASURER (Kantong — Profit & Expense Calculator)
# ---------------------------------------------------------------------------
def menu_treasurer():
    """
    UI untuk AgentTreasurer (#10).
    Integrasi tambahan:
      - get_billing_reminders() → check_autobilling_reminders()
        menampilkan klien yang mendekati jatuh tempo invoice.
    """
    squad     = get_squad()
    treasurer = squad.agent(10)          # AgentTreasurer
    db_klien  = st.session_state.get("db_umum", [])

    # ── Header ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='padding:32px 48px 0;'>
        <div class='page-title'>
            💰 AgentTreasurer —
            <span style='color:#00d4ff;'>Profit &amp; Expense</span>
        </div>
        <div class='page-subtitle'>
            Agent #10 · Kantong Sistem · MRR, margin, proyeksi,
            pengingat tagihan, dan komisi referral.
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='padding:24px 48px;'>", unsafe_allow_html=True)

    # ── Kontrol hitung ───────────────────────────────────────────────────────
    col_calc, col_months, _ = st.columns([1, 1, 2])
    with col_calc:
        do_calc = st.button(
            "🔄 Hitung Ledger Sekarang",
            type="primary", key="tr_calc", use_container_width=True,
        )
    with col_months:
        months_proj = st.number_input(
            "Proyeksi (bulan)", min_value=1, max_value=24,
            value=6, step=1, key="tr_months",
        )

    # ── Panel pengeluaran ekstra ─────────────────────────────────────────────
    with st.expander("➕ Tambah Pengeluaran Ekstra Bulan Ini"):
        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            extra_label1 = st.text_input("Label 1", value="Iklan Meta Ads",   key="ex_lbl1")
            extra_val1   = st.number_input(
                "Nominal (Rp)", min_value=0, value=500_000,
                step=100_000, key="ex_val1",
            )
        with ec2:
            extra_label2 = st.text_input("Label 2", value="Domain & SSL",     key="ex_lbl2")
            extra_val2   = st.number_input(
                "Nominal (Rp)", min_value=0, value=150_000,
                step=50_000, key="ex_val2",
            )
        with ec3:
            extra_label3 = st.text_input("Label 3", value="Operasional Lain", key="ex_lbl3")
            extra_val3   = st.number_input(
                "Nominal (Rp)", min_value=0, value=0,
                step=100_000, key="ex_val3",
            )
    extra_expenses = {
        extra_label1: extra_val1,
        extra_label2: extra_val2,
        extra_label3: extra_val3,
    }

    # ── Jalankan kalkulasi ───────────────────────────────────────────────────
    if do_calc or st.session_state.get("tr_last_ledger"):
        if do_calc:
            ledger_result = treasurer.run(db_klien, extra_expenses, int(months_proj))
            st.session_state["tr_last_ledger"] = ledger_result
        else:
            ledger_result = st.session_state["tr_last_ledger"]
    else:
        ledger_result = treasurer.run(db_klien, {}, 6)
        st.session_state["tr_last_ledger"] = ledger_result

    ledger    = ledger_result.get("ledger", {})
    fixed_bkd = ledger_result.get("fixed_breakdown", {})
    proj      = ledger_result.get("projection", [])

    # ── Metrik utama ─────────────────────────────────────────────────────────
    period_label = ledger.get("period", datetime.date.today().strftime("%B %Y"))
    st.markdown(
        f"<div style='font-family:Rajdhani,sans-serif;font-size:17px;"
        f"font-weight:700;color:#e8f4ff;margin:16px 0 12px;'>"
        f"📊 Ringkasan Bulan Ini — {period_label}</div>",
        unsafe_allow_html=True,
    )
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("MRR",          f"Rp {ledger.get('mrr', 0):,.0f}")
    k2.metric("ARR",          f"Rp {ledger.get('arr', 0):,.0f}")
    k3.metric("Gross Margin", f"{ledger.get('gross_margin_pct', 0):.1f}%",
              delta="Target 78%")
    k4.metric("Net Profit",   f"Rp {ledger.get('net_profit', 0):,.0f}")
    k5.metric("Total Biaya",  f"Rp {ledger.get('total_expense', 0):,.0f}")
    k6.metric("Klien Aktif",  str(ledger.get("klien_aktif", 0)))

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1.3], gap="large")

    # ── Kiri: breakdown biaya + tagihan pending ───────────────────────────────
    with col_left:
        st.markdown(
            "<div style='background:#101c2e;border:1px solid #1e3352;"
            "border-radius:12px;padding:20px;'>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='font-family:Rajdhani,sans-serif;font-size:15px;"
            "font-weight:700;color:#00d4ff;margin-bottom:14px;'>"
            "🧾 Breakdown Pengeluaran</div>",
            unsafe_allow_html=True,
        )
        all_costs = {
            **fixed_bkd,
            **{k: v for k, v in extra_expenses.items() if v > 0},
            "COGS (22% Rev)":  int(ledger.get("cogs", 0)),
            "Komisi Referral": int(ledger.get("komisi_expense", 0)),
        }
        total_exp = max(ledger.get("total_expense", 1), 1)
        for label, amount in all_costs.items():
            bar_pct = min(100, int(amount / total_exp * 100))
            st.markdown(
                f"<div style='margin-bottom:10px;'>"
                f"<div style='display:flex;justify-content:space-between;"
                f"margin-bottom:3px;'>"
                f"<span style='font-size:12px;color:#9ab8d4;'>{label}</span>"
                f"<span style='font-size:12px;color:#e8f4ff;font-weight:600;'>"
                f"Rp {amount:,.0f}</span></div>"
                f"<div style='background:#1e3352;border-radius:4px;height:5px;'>"
                f"<div style='background:linear-gradient(90deg,#0091ff,#00d4ff);"
                f"width:{bar_pct}%;height:5px;border-radius:4px;'></div>"
                f"</div></div>",
                unsafe_allow_html=True,
            )
        st.markdown(
            f"<hr style='border-color:#1e3352;margin:12px 0;'>"
            f"<div style='display:flex;justify-content:space-between;'>"
            f"<span style='font-family:Rajdhani,sans-serif;font-size:15px;"
            f"font-weight:700;color:#e8f4ff;'>Total Biaya</span>"
            f"<span style='font-family:Rajdhani,sans-serif;font-size:15px;"
            f"font-weight:700;color:#ff3b5c;'>"
            f"Rp {ledger.get('total_expense', 0):,.0f}</span></div>"
            f"<div style='display:flex;justify-content:space-between;margin-top:6px;'>"
            f"<span style='font-size:13px;color:#7a9bbf;'>Net After Tax (11%)</span>"
            f"<span style='font-size:13px;font-weight:700;color:#00e676;'>"
            f"Rp {ledger.get('net_after_tax', 0):,.0f}</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Integrasi: Pengingat Tagihan (get_billing_reminders) ─────────────
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-family:Rajdhani,sans-serif;font-size:15px;"
            "font-weight:700;color:#ffab00;margin-bottom:10px;'>"
            "⏰ Pengingat Tagihan Jatuh Tempo</div>",
            unsafe_allow_html=True,
        )
        # check_autobilling_reminders adalah "get_billing_reminders" di sini
        reminders = check_autobilling_reminders(db_klien)
        if reminders:
            for rem in reminders:
                color = "#ff3b5c" if rem["delta"] <= 1 else "#ffab00"
                label = (
                    "🚨 H-1 BESOK JATUH TEMPO"
                    if rem["delta"] <= 1 else f"⏰ H-{rem['delta']} Jatuh Tempo"
                )
                wa_rem = rem.get("wa", "")
                if wa_rem and not wa_rem.startswith("62"):
                    wa_rem = "62" + wa_rem.lstrip("0")
                due_info = "BESOK!" if rem["delta"] == 1 else f"dalam {rem['delta']} hari"
                inv_msg = urllib.parse.quote(
                    f"{'🚨 URGENT — ' if rem['delta'] <= 1 else '⏰ '}"
                    f"PENGINGAT INVOICE V-GUARD AI\n\n"
                    f"Yth. {rem['nama']},\n\n"
                    f"Invoice paket {rem['paket']} Anda jatuh tempo "
                    f"{rem['due']} ({due_info}).\n\n"
                    f"Transfer: BCA 3450074658 a/n Erwin Sinaga\n"
                    f"— Tim V-Guard AI"
                )
                st.markdown(
                    f"<div style='background:#101c2e;border:1px solid {color}33;"
                    f"border-left:3px solid {color};border-radius:8px;"
                    f"padding:12px 14px;margin-bottom:8px;'>"
                    f"<div style='font-size:12px;color:{color};font-family:"
                    f"JetBrains Mono,monospace;margin-bottom:4px;'>{label}</div>"
                    f"<div style='font-size:13px;color:#e8f4ff;font-weight:600;'>"
                    f"{rem['nama']} — {rem['usaha']}</div>"
                    f"<div style='font-size:11px;color:#7a9bbf;'>"
                    f"{rem['paket']} · Due: {rem['due']}</div></div>",
                    unsafe_allow_html=True,
                )
                if wa_rem:
                    st.link_button(
                        f"📲 Kirim Reminder ke {rem['nama']}",
                        f"https://wa.me/{wa_rem}?text={inv_msg}",
                        key=f"tr_rem_{rem['cid']}",
                        use_container_width=True,
                    )
        else:
            st.success("✅ Tidak ada invoice mendekati jatuh tempo.")

        # ── Klien pending (belum bayar) ──────────────────────────────────────
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        pending_klien = [k for k in db_klien if k.get("Status") != "Aktif"]
        if pending_klien:
            st.markdown(
                "<div style='font-family:Rajdhani,sans-serif;font-size:15px;"
                "font-weight:700;color:#ff3b5c;margin-bottom:10px;'>"
                "💳 Tagih Klien Belum Bayar</div>",
                unsafe_allow_html=True,
            )
            for k in pending_klien:
                pkg_k  = k.get("Produk", "V-LITE")
                hb, hs = HARGA_MAP.get(pkg_k, ("—", "—"))
                nama   = k.get("Nama Klien", "—")
                wa_k   = k.get("WhatsApp", "")
                if wa_k and not wa_k.startswith("62"):
                    wa_k = "62" + wa_k.lstrip("0")
                inv_msg2 = urllib.parse.quote(
                    f"INVOICE V-GUARD AI\n\nYth. {nama},\n\n"
                    f"Paket   : {pkg_k}\nBulanan : {hb}\nSetup   : {hs}\n\n"
                    f"Transfer: BCA 3450074658 a/n Erwin Sinaga\n"
                    f"Konfirmasi setelah transfer.\n— Tim V-Guard AI"
                )
                st.markdown(
                    f"<div style='background:#101c2e;border:1px solid #ff3b5c33;"
                    f"border-left:3px solid #ff3b5c;border-radius:8px;"
                    f"padding:12px 14px;margin-bottom:8px;'>"
                    f"<div style='font-size:13px;color:#e8f4ff;font-weight:600;'>"
                    f"{nama}</div>"
                    f"<div style='font-size:11px;color:#7a9bbf;'>"
                    f"{pkg_k} · {hb}/bln</div></div>",
                    unsafe_allow_html=True,
                )
                if wa_k:
                    st.link_button(
                        f"📲 Tagih {nama}",
                        f"https://wa.me/{wa_k}?text={inv_msg2}",
                        key=f"tagih_{k.get('Client_ID', nama)}",
                        use_container_width=True,
                    )
        else:
            st.success("✅ Semua klien berstatus aktif — tidak ada tagihan pending.")

    # ── Kanan: proyeksi + ROI per klien ─────────────────────────────────────
    with col_right:
        if proj:
            st.markdown(
                "<div style='background:#101c2e;border:1px solid #1e3352;"
                "border-radius:12px;padding:20px;'>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<div style='font-family:Rajdhani,sans-serif;font-size:15px;"
                "font-weight:700;color:#00d4ff;margin-bottom:14px;'>"
                "📈 Proyeksi MRR & Net Profit</div>",
                unsafe_allow_html=True,
            )
            df_proj = pd.DataFrame(proj)
            st.dataframe(
                df_proj.rename(columns={
                    "month":      "Bulan",
                    "mrr":        "MRR (Rp)",
                    "net_profit": "Net Profit (Rp)",
                    "growth_pct": "Growth %",
                }),
                use_container_width=True,
                hide_index=True,
            )
            best = max(proj, key=lambda x: x["net_profit"])
            st.markdown(
                f"<div style='background:#00e67611;border:1px solid #00e67633;"
                f"border-radius:8px;padding:10px 14px;margin-top:10px;"
                f"font-size:13px;color:#00e676;'>"
                f"🏆 Proyeksi terbaik: <b>{best['month']}</b> — "
                f"Net Profit Rp {best['net_profit']:,.0f} "
                f"(Growth {best['growth_pct']:.1f}%)</div>",
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # ── ROI per klien aktif ──────────────────────────────────────────────
        st.markdown(
            "<div style='background:#101c2e;border:1px solid #1e3352;"
            "border-radius:12px;padding:20px;'>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='font-family:Rajdhani,sans-serif;font-size:15px;"
            "font-weight:700;color:#ffd700;margin-bottom:14px;'>"
            "🧮 ROI per Klien Aktif</div>",
            unsafe_allow_html=True,
        )
        aktif_klien = [k for k in db_klien if k.get("Status") == "Aktif"]
        if not aktif_klien:
            st.info("Belum ada klien aktif untuk dikalkulasi.")
        else:
            roi_rows = []
            for k in aktif_klien:
                pkg_k  = k.get("Produk", "V-LITE")
                # estimasi omzet = 20× biaya paket (konservatif)
                omzet  = HARGA_NUMERIK.get(pkg_k, 0) * 20
                result = treasurer.roi_klien(omzet, pkg_k)
                roi_rows.append({
                    "Klien":          k.get("Nama Klien", "—"),
                    "Paket":          pkg_k,
                    "Est. Omzet/bln": f"Rp {result['omzet']:,.0f}",
                    "Diselamatkan":   f"Rp {result['diselamatkan']:,.0f}",
                    "ROI":            f"{result['roi_pct']:.0f}%",
                    "Payback":        f"{result['payback_days']:.0f} hari",
                })
            st.dataframe(
                pd.DataFrame(roi_rows),
                use_container_width=True,
                hide_index=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Download ledger ──────────────────────────────────────────────────
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        st.download_button(
            "⬇️ Download Ledger CSV",
            data=pd.DataFrame([ledger]).to_csv(index=False).encode("utf-8"),
            file_name=f"vguard_ledger_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)
