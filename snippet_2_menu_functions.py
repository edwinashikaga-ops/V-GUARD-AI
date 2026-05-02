# =============================================================================
# V-GUARD AI INTELLIGENCE — snippet_2_menu_functions.py
# Menu rendering functions for Visionary CCTV and Treasurer pages.
# Called from app.py page routing (menus 👁️ Visionary CCTV and 💰 Treasurer).
# Requires: logic_vguard (get_squad, get_sample_transaksi), streamlit, pandas
# =============================================================================

import datetime
import random
import urllib.parse

import pandas as pd
import streamlit as st

from logic_vguard import (
    get_squad,
    get_sample_transaksi,
    HARGA_MAP,
    HARGA_NUMERIK,
    WA_NUMBER,
)


# =============================================================================
# MENU — 👁️ VISIONARY CCTV
# Agent #1 — Mata: CCTV Visual Intelligence
# =============================================================================
def menu_visionary():
    squad     = get_squad()
    visionary = squad.agent(1)

    st.markdown("""
    <div style='padding:32px 48px 0;'>
        <div class='page-title'>👁️ Visionary — <span style='color:#00d4ff;'>CCTV Visual Intelligence</span></div>
        <div class='page-subtitle'>Agent #1 · Mata Sistem · Analisis frame CCTV, overlay transaksi real-time, deteksi anomali visual.</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='padding:24px 48px;'>", unsafe_allow_html=True)

    is_active    = visionary.is_active()
    status_color = "#00e676" if is_active else "#ff3b5c"
    status_label = "ACTIVE — Monitoring semua kamera" if is_active else "KILLED — Kamera tidak aktif"

    st.markdown(
        f"<div style='background:#101c2e;border:1px solid #1e3352;border-left:3px solid {status_color};"
        f"border-radius:10px;padding:14px 20px;margin-bottom:20px;display:flex;"
        f"align-items:center;justify-content:space-between;'>"
        f"<div><span style='font-family:JetBrains Mono,monospace;font-size:10px;"
        f"color:{status_color};text-transform:uppercase;letter-spacing:1.5px;'>● {status_label}</span>"
        f"<div style='font-size:12px;color:#7a9bbf;margin-top:4px;'>"
        f"Frame logs: {len(st.session_state.get('vision_logs', []))}</div></div>"
        f"<div style='font-family:Rajdhani,sans-serif;font-size:13px;font-weight:700;color:#7a9bbf;'>"
        f"Engine: YOLO v8 (Stub Mode)</div></div>",
        unsafe_allow_html=True,
    )

    tab_live, tab_batch, tab_logs = st.tabs([
        "📹 Live Monitor",
        "⚡ Batch Analysis",
        "📋 Vision Logs",
    ])

    # ── TAB 1: Live Monitor ──────────────────────────────────────────────────
    with tab_live:
        CAMERAS = [
            {"id": "cam_01", "label": "Outlet Sudirman — Kasir 1",    "alert": True},
            {"id": "cam_02", "label": "Outlet Sudirman — Kasir 2",    "alert": False},
            {"id": "cam_03", "label": "Resto Central — Kasir Utama",  "alert": False},
            {"id": "cam_04", "label": "Cabang Tangerang — Pintu Masuk","alert": False},
        ]
        cols = st.columns(2)
        for i, cam in enumerate(CAMERAS):
            with cols[i % 2]:
                now_str    = datetime.datetime.now().strftime("%H:%M:%S")
                alert_html = (
                    "<div style='position:absolute;top:8px;right:8px;font-family:JetBrains Mono,"
                    "monospace;font-size:10px;color:#ff3b5c;background:#00000088;padding:4px 8px;"
                    "border-radius:4px;animation:vgPulse 1s infinite;'>⚠ VOID DETECTED</div>"
                    if cam["alert"] else
                    "<div style='position:absolute;top:8px;right:8px;font-family:JetBrains Mono,"
                    "monospace;font-size:10px;color:#00e676;background:#00000088;padding:4px 8px;"
                    "border-radius:4px;'>✓ NORMAL</div>"
                )
                border = "2px solid #ff3b5c" if cam["alert"] else "2px solid #1e3352"
                st.markdown(
                    f"<div style='background:#000;border:{border};border-radius:8px;"
                    f"aspect-ratio:16/9;display:flex;align-items:center;justify-content:center;"
                    f"position:relative;overflow:hidden;margin-bottom:12px;'>"
                    f"<div style='text-align:center;'>"
                    f"<div style='font-size:32px;margin-bottom:6px;'>📹</div>"
                    f"<div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#1e3352;'>"
                    f"{cam['label']}</div>"
                    f"<div style='font-size:10px;color:#7a9bbf;margin-top:4px;'>"
                    f"Feed tersedia setelah hardware terpasang</div></div>"
                    f"<div style='position:absolute;top:8px;left:8px;font-family:JetBrains Mono,"
                    f"monospace;font-size:10px;color:#00e676;background:#00000088;padding:4px 8px;"
                    f"border-radius:4px;'>● REC {now_str} · {cam['id']}</div>"
                    f"{alert_html}</div>",
                    unsafe_allow_html=True,
                )

        col_scan, col_src = st.columns([1, 2])
        with col_scan:
            if st.button("🤖 Scan Satu Frame (Demo)", type="primary",
                         key="vis_scan_live", use_container_width=True):
                frame = {"camera_id": "cam_01", "timestamp": str(datetime.datetime.now())}
                result = visionary.run(frame)
                st.session_state["_vis_last"] = result
        result = st.session_state.get("_vis_last")
        if result and result.get("status") == "OK":
            alert = result.get("alert", False)
            if alert:
                st.error(f"⚠️ ALERT: {result.get('alert_reason','Anomali visual terdeteksi')} — {result.get('camera_id','—')}")
            else:
                st.success("✅ Frame bersih — tidak ada anomali visual.")
            with st.expander("Detail deteksi (raw)"):
                st.json({k: v for k, v in result.items() if k not in ("overlay_text",)})

    # ── TAB 2: Batch Analysis ────────────────────────────────────────────────
    with tab_batch:
        st.markdown(
            "<div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;"
            "color:#e8f4ff;margin-bottom:6px;'>⚡ Batch Frame + POS Cross-check</div>"
            "<div style='font-size:13px;color:#7a9bbf;margin-bottom:14px;'>"
            "Kirim semua frame kamera bersamaan dan cocokkan dengan data POS aktif.</div>",
            unsafe_allow_html=True,
        )
        n_frames = st.slider("Jumlah frame simulasi", 1, 8, 4, key="vis_n_frames")
        if st.button("▶️ Jalankan Batch Analysis", type="primary",
                     key="vis_batch_run", use_container_width=True):
            pos_df = get_sample_transaksi()
            frames = [
                {"camera_id": f"cam_0{i+1}", "timestamp": str(datetime.datetime.now())}
                for i in range(n_frames)
            ]
            with st.spinner("Visionary memproses frame..."):
                results = visionary.process_batch(frames, pos_df)
            st.session_state["_vis_batch"] = results

        batch = st.session_state.get("_vis_batch")
        if batch:
            alerts = [r for r in batch if r.get("alert")]
            b1, b2, b3 = st.columns(3)
            b1.metric("Frame Diproses", len(batch))
            b2.metric("Alert Terdeteksi", len(alerts),
                      delta="⚠ Anomali" if alerts else None, delta_color="inverse")
            b3.metric("Bersih", len(batch) - len(alerts))
            for r in batch:
                color = "#ff3b5c" if r.get("alert") else "#00e676"
                label = f"⚠ {r.get('alert_reason','ALERT')}" if r.get("alert") else "✓ NORMAL"
                st.markdown(
                    f"<div style='background:#101c2e;border:1px solid #1e3352;"
                    f"border-left:3px solid {color};border-radius:8px;padding:10px 16px;"
                    f"margin-bottom:8px;display:flex;justify-content:space-between;'>"
                    f"<div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#7a9bbf;'>"
                    f"{r.get('camera_id','—')} · {r.get('timestamp','')[:19]}</div>"
                    f"<div style='font-size:12px;color:{color};'>{label}</div></div>",
                    unsafe_allow_html=True,
                )
            if alerts:
                for r in alerts:
                    cabang = r.get("camera_id","cam")
                    alarm_txt = urllib.parse.quote(
                        f"🚨 V-GUARD VISIONARY ALERT\n\n📹 Kamera: {cabang}\n"
                        f"⚠️ Alasan: {r.get('alert_reason','Anomali visual')}\n"
                        f"🕐 {r.get('timestamp','')[:19]}\n\n"
                        f"Segera cek rekaman!\n— AgentVisionary V-Guard"
                    )
                    st.link_button(
                        f"📲 Kirim Alert — {cabang}",
                        f"https://wa.me/{WA_NUMBER}?text={alarm_txt}",
                        key=f"vis_alert_{cabang}",
                    )

    # ── TAB 3: Vision Logs ───────────────────────────────────────────────────
    with tab_logs:
        logs = st.session_state.get("vision_logs", [])
        if not logs:
            st.info("Belum ada frame yang diproses. Jalankan Live Monitor atau Batch Analysis.")
        else:
            st.markdown(
                f"<div style='font-size:13px;color:#7a9bbf;margin-bottom:10px;'>"
                f"Total frame logged: <b style='color:#00d4ff;'>{len(logs)}</b></div>",
                unsafe_allow_html=True,
            )
            for entry in reversed(logs[-20:]):
                color = "#ff3b5c" if entry.get("alert") else "#00e676"
                label = f"⚠ {entry.get('alert_reason','ALERT')}" if entry.get("alert") else "✓ NORMAL"
                ts    = str(entry.get("timestamp",""))[:19]
                st.markdown(
                    f"<div style='background:#101c2e;border:1px solid #1e3352;"
                    f"border-left:3px solid {color};border-radius:8px;padding:10px 16px;"
                    f"margin-bottom:6px;display:flex;justify-content:space-between;'>"
                    f"<div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#7a9bbf;'>"
                    f"{entry.get('camera_id','—')} · {ts}</div>"
                    f"<div style='font-size:12px;color:{color};'>{label}</div></div>",
                    unsafe_allow_html=True,
                )

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)


# =============================================================================
# MENU — 💰 TREASURER
# Agent #10 — Kantong: Profit & Expense Calculator
# =============================================================================
def menu_treasurer():
    squad     = get_squad()
    treasurer = squad.agent(10)

    st.markdown("""
    <div style='padding:32px 48px 0;'>
        <div class='page-title'>💰 Treasurer — <span style='color:#00d4ff;'>Profit & Expense Calculator</span></div>
        <div class='page-subtitle'>Agent #10 · Kantong Sistem · MRR, gross margin, proyeksi profit, dan breakdown pengeluaran bulanan.</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='padding:24px 48px;'>", unsafe_allow_html=True)

    is_active    = treasurer.is_active()
    status_color = "#00e676" if is_active else "#ff3b5c"
    status_label = "ACTIVE — Kalkulasi keuangan berjalan" if is_active else "KILLED — Kalkulasi tidak aktif"

    st.markdown(
        f"<div style='background:#101c2e;border:1px solid #1e3352;border-left:3px solid {status_color};"
        f"border-radius:10px;padding:14px 20px;margin-bottom:20px;display:flex;"
        f"align-items:center;justify-content:space-between;'>"
        f"<div><span style='font-family:JetBrains Mono,monospace;font-size:10px;"
        f"color:{status_color};text-transform:uppercase;letter-spacing:1.5px;'>● {status_label}</span>"
        f"<div style='font-size:12px;color:#7a9bbf;margin-top:4px;'>"
        f"Ledger entries: {len(st.session_state.get('treasurer_ledger', []))}</div></div>"
        f"<div style='font-family:Rajdhani,sans-serif;font-size:13px;font-weight:700;color:#7a9bbf;'>"
        f"Tax Rate: 11% · COGS Rate: 22%</div></div>",
        unsafe_allow_html=True,
    )

    tab_ledger, tab_roi, tab_proj = st.tabs([
        "📊 Ledger Bulanan",
        "🧮 ROI Kalkulator Klien",
        "📈 Proyeksi Profit",
    ])

    db_klien = st.session_state.get("db_umum", [])

    # ── TAB 1: Ledger Bulanan ────────────────────────────────────────────────
    with tab_ledger:
        months_ahead = st.slider("Proyeksi ke depan (bulan)", 1, 12, 6, key="tr_months")

        col_extra, col_run = st.columns([2, 1])
        with col_extra:
            extra_marketing = st.number_input(
                "Pengeluaran Tambahan — Marketing (Rp)",
                min_value=0, value=0, step=500_000, key="tr_extra_mkt",
            )
            extra_ops = st.number_input(
                "Pengeluaran Tambahan — Operasional (Rp)",
                min_value=0, value=0, step=500_000, key="tr_extra_ops",
            )
        with col_run:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            run_ledger = st.button(
                "⚡ Hitung Ledger Sekarang", type="primary",
                key="tr_run", use_container_width=True,
            )

        if run_ledger:
            if not is_active:
                st.error("Agent Treasurer sedang di-kill. Restart dari panel Admin > AI Agents.")
            else:
                extra = {}
                if extra_marketing: extra["Marketing Tambahan"] = extra_marketing
                if extra_ops:       extra["Operasional Tambahan"] = extra_ops
                with st.spinner("Agent Treasurer menghitung..."):
                    result = treasurer.run(db_klien, extra, months_ahead)
                st.session_state["tr_last_ledger"] = result

        result = st.session_state.get("tr_last_ledger")
        if result and result.get("status") == "OK":
            ledger = result["ledger"]
            fixed  = result.get("fixed_breakdown", {})

            # KPI row
            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("MRR",           f"Rp {ledger['mrr']:,.0f}")
            k2.metric("ARR",           f"Rp {ledger['arr']:,.0f}")
            k3.metric("Gross Margin",  f"{ledger['gross_margin_pct']}%")
            k4.metric("Net Profit",    f"Rp {ledger['net_profit']:,.0f}",
                      delta="Untung" if ledger['net_profit'] > 0 else "Rugi",
                      delta_color="normal" if ledger['net_profit'] > 0 else "inverse")
            k5.metric("Klien Aktif",   str(ledger["klien_aktif"]))

            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

            col_inc, col_exp = st.columns(2)
            with col_inc:
                st.markdown(
                    "<div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;"
                    "padding:20px;'><div style='font-family:Rajdhani,sans-serif;font-size:16px;"
                    "font-weight:700;color:#00e676;margin-bottom:14px;'>💵 Revenue</div>"
                    f"<div style='font-size:13px;color:#9ab8d4;margin-bottom:8px;'>"
                    f"MRR (Langganan): <b style='color:#e8f4ff;'>Rp {ledger['mrr']:,.0f}</b></div>"
                    f"<div style='font-size:13px;color:#9ab8d4;margin-bottom:8px;'>"
                    f"Total Revenue: <b style='color:#00d4ff;'>Rp {ledger['total_revenue']:,.0f}</b></div>"
                    f"<div style='font-size:13px;color:#9ab8d4;'>"
                    f"Gross Profit: <b style='color:#00e676;'>Rp {ledger['gross_profit']:,.0f}</b></div></div>",
                    unsafe_allow_html=True,
                )
            with col_exp:
                fixed_rows = "".join(
                    f"<div style='font-size:12px;color:#9ab8d4;margin-bottom:6px;"
                    f"display:flex;justify-content:space-between;'>"
                    f"<span>{name}</span><span style='color:#e8f4ff;'>Rp {val:,.0f}</span></div>"
                    for name, val in fixed.items()
                )
                st.markdown(
                    "<div style='background:#101c2e;border:1px solid #1e3352;border-radius:12px;"
                    "padding:20px;'><div style='font-family:Rajdhani,sans-serif;font-size:16px;"
                    "font-weight:700;color:#ff3b5c;margin-bottom:14px;'>💸 Pengeluaran</div>"
                    + fixed_rows +
                    f"<div style='border-top:1px solid #1e3352;margin-top:10px;padding-top:10px;"
                    f"font-size:13px;color:#9ab8d4;display:flex;justify-content:space-between;'>"
                    f"<b>Total Pengeluaran</b>"
                    f"<b style='color:#ff3b5c;'>Rp {ledger['total_expense']:,.0f}</b></div></div>",
                    unsafe_allow_html=True,
                )

            # Net after tax
            st.markdown(
                f"<div style='background:linear-gradient(135deg,#00e67611,#00d4ff11);"
                f"border:1px solid #00e67633;border-radius:10px;padding:20px;"
                f"text-align:center;margin-top:16px;'>"
                f"<div style='font-size:13px;color:#7a9bbf;'>Net Profit Setelah Pajak 11%</div>"
                f"<div style='font-family:Rajdhani,sans-serif;font-size:48px;font-weight:700;"
                f"color:{'#00e676' if ledger['net_after_tax'] >= 0 else '#ff3b5c'};'>"
                f"Rp {ledger['net_after_tax']:,.0f}</div>"
                f"<div style='font-size:12px;color:#7a9bbf;'>Pajak: Rp {ledger['tax_11pct']:,.0f}</div></div>",
                unsafe_allow_html=True,
            )
        elif not result:
            st.info("Klik 'Hitung Ledger Sekarang' untuk memulai kalkulasi.")

    # ── TAB 2: ROI Kalkulator Klien ──────────────────────────────────────────
    with tab_roi:
        st.markdown(
            "<div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;"
            "color:#e8f4ff;margin-bottom:14px;'>🧮 Simulasi ROI per Klien</div>",
            unsafe_allow_html=True,
        )
        rc1, rc2 = st.columns(2)
        with rc1:
            omzet_val = st.number_input(
                "Omzet Bulanan Klien (Rp)",
                min_value=0, value=50_000_000, step=5_000_000, key="tr_omzet",
            )
            paket_val = st.selectbox(
                "Paket V-Guard", ["V-LITE","V-PRO","V-ADVANCE","V-ELITE"],
                index=1, key="tr_paket",
            )
        with rc2:
            bocor_pct = st.slider("Estimasi Kebocoran (%)", 1, 20, 5, key="tr_bocor")
            st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
            calc_roi = st.button("🧮 Hitung ROI", type="primary",
                                 key="tr_roi_btn", use_container_width=True)

        if calc_roi:
            if not is_active:
                st.error("Agent Treasurer sedang di-kill.")
            else:
                roi = treasurer.roi_klien(omzet_val, paket_val, bocor_pct)
                hb, _ = HARGA_MAP.get(paket_val, ("—","—"))
                st.markdown(
                    "<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:16px;'>"
                    f"<div style='background:#101c2e;border:1px solid #ff3b5c33;border-radius:8px;"
                    f"padding:16px;text-align:center;'><div style='font-size:11px;color:#7a9bbf;'>Kebocoran/Bln</div>"
                    f"<div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#ff3b5c;'>"
                    f"Rp {roi['kebocoran_rp']:,.0f}</div></div>"
                    f"<div style='background:#101c2e;border:1px solid #00e67633;border-radius:8px;"
                    f"padding:16px;text-align:center;'><div style='font-size:11px;color:#7a9bbf;'>Diselamatkan 88%</div>"
                    f"<div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#00e676;'>"
                    f"Rp {roi['diselamatkan']:,.0f}</div></div>"
                    f"<div style='background:#101c2e;border:1px solid #00d4ff33;border-radius:8px;"
                    f"padding:16px;text-align:center;'><div style='font-size:11px;color:#7a9bbf;'>Net Saving</div>"
                    f"<div style='font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#00d4ff;'>"
                    f"Rp {roi['net_saving']:,.0f}</div></div></div>"
                    f"<div style='background:linear-gradient(135deg,#00e67611,#00d4ff11);"
                    f"border:1px solid #00e67633;border-radius:10px;padding:20px;text-align:center;margin-top:14px;'>"
                    f"<div style='font-size:12px;color:#7a9bbf;'>ROI Bulanan · Payback {roi['payback_days']:.0f} hari</div>"
                    f"<div style='font-family:Rajdhani,sans-serif;font-size:52px;font-weight:700;"
                    f"background:linear-gradient(135deg,#00e676,#00d4ff);-webkit-background-clip:text;"
                    f"-webkit-text-fill-color:transparent;'>{roi['roi_pct']:.0f}%</div>"
                    f"<div style='font-size:12px;color:#7a9bbf;'>Paket {paket_val} — {hb}/bln</div></div>",
                    unsafe_allow_html=True,
                )

    # ── TAB 3: Proyeksi Profit ───────────────────────────────────────────────
    with tab_proj:
        result = st.session_state.get("tr_last_ledger")
        if not result or result.get("status") != "OK":
            st.info("Jalankan Ledger Bulanan terlebih dahulu untuk melihat proyeksi.")
        else:
            projection = result.get("projection", [])
            if not projection:
                st.info("Tidak ada data proyeksi. Coba jalankan ulang Ledger.")
            else:
                st.markdown(
                    "<div style='font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;"
                    "color:#e8f4ff;margin-bottom:14px;'>📈 Proyeksi MRR & Net Profit</div>",
                    unsafe_allow_html=True,
                )
                for p in projection:
                    net_color = "#00e676" if p["net_profit"] >= 0 else "#ff3b5c"
                    pct_color = "#00d4ff"
                    bar_width = min(100, max(5, int(p["mrr"] / 10_000_000 * 100)))
                    st.markdown(
                        f"<div style='background:#101c2e;border:1px solid #1e3352;border-radius:8px;"
                        f"padding:14px 18px;margin-bottom:8px;'>"
                        f"<div style='display:flex;justify-content:space-between;align-items:center;"
                        f"margin-bottom:8px;'>"
                        f"<div style='font-family:Rajdhani,sans-serif;font-size:15px;font-weight:700;"
                        f"color:#e8f4ff;'>{p['month']}</div>"
                        f"<div style='display:flex;gap:20px;'>"
                        f"<div style='text-align:right;'><div style='font-size:10px;color:#7a9bbf;'>MRR</div>"
                        f"<div style='font-family:Rajdhani,sans-serif;font-size:14px;font-weight:700;"
                        f"color:#00d4ff;'>Rp {p['mrr']:,.0f}</div></div>"
                        f"<div style='text-align:right;'><div style='font-size:10px;color:#7a9bbf;'>Net Profit</div>"
                        f"<div style='font-family:Rajdhani,sans-serif;font-size:14px;font-weight:700;"
                        f"color:{net_color};'>Rp {p['net_profit']:,.0f}</div></div>"
                        f"<div style='text-align:right;'><div style='font-size:10px;color:#7a9bbf;'>Growth</div>"
                        f"<div style='font-family:Rajdhani,sans-serif;font-size:14px;font-weight:700;"
                        f"color:{pct_color};'>+{p['growth_pct']}%</div></div>"
                        f"</div></div>"
                        f"<div style='background:#1e3352;border-radius:4px;height:6px;'>"
                        f"<div style='background:linear-gradient(90deg,#0091ff,#00d4ff);border-radius:4px;"
                        f"height:6px;width:{bar_width}%;'></div></div></div>",
                        unsafe_allow_html=True,
                    )

                proj_df = pd.DataFrame(projection)
                st.download_button(
                    "⬇️ Download Proyeksi CSV",
                    data=proj_df.to_csv(index=False).encode("utf-8"),
                    file_name=f"vguard_proyeksi_{datetime.date.today()}.csv",
                    mime="text/csv",
                    key="tr_download_proj",
                )

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)
