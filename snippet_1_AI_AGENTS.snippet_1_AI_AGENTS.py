# =============================================================================
# SNIPPET 1 — Ganti seluruh blok AI_AGENTS = [...] di app.py
# Cari:   AI_AGENTS = [
# Sampai: ]
# Ganti dengan blok di bawah ini.
# =============================================================================

AI_AGENTS = [
    {
        "id":   1,
        "name": "Visionary",
        "role": "Mata — CCTV Visual Intelligence",
        "icon": "👁️",
        "desc": "Mengawasi feed CCTV, deteksi anomali visual (barang tidak di-scan, "
                "void gesture, cash swap), dan render overlay transaksi real-time.",
    },
    {
        "id":   2,
        "name": "Concierge",
        "role": "Telinga — CS & Onboarding Intelligence",
        "icon": "🤝",
        "desc": "Lead scoring otomatis, rekomendasi paket terbaik berdasarkan percakapan, "
                "dan checklist onboarding klien baru pasca aktivasi.",
    },
    {
        "id":   3,
        "name": "GrowthHacker",
        "role": "Mulut — Marketing & Branding Automation",
        "icon": "📣",
        "desc": "Generate WA blast, konten promo per paket, A/B test copywriting, "
                "dan analisis konversi lead per channel.",
    },
    {
        "id":   4,
        "name": "Liaison",
        "role": "Tangan — POS / SAP / Moka Integration + Local Filter",
        "icon": "🔗",
        "desc": "Hubungkan Moka, SAP, iReap, Majoo, Olsera, Pawoon & Custom API. "
                "Filter lokal 6-rule — hanya anomali naik ke Cloud AI (hemat 80% cost).",
    },
    {
        "id":   5,
        "name": "Analyst",
        "role": "Otak Audit — Financial Forensic & Bank Reconciliation",
        "icon": "🏦",
        "desc": "Rekonsiliasi kasir vs mutasi bank secara otomatis, identifikasi selisih "
                "finansial jangka panjang, dan produksi laporan audit PDF-ready.",
    },
    {
        "id":   6,
        "name": "Stockmaster",
        "role": "Gudang — Inventory Intelligence & OCR Invoice",
        "icon": "📦",
        "desc": "Update stok real-time via drag & drop invoice supplier (OCR), "
                "pantau level stok kritis, dan kirim reorder alert otomatis.",
    },
    {
        "id":   7,
        "name": "Watchdog",
        "role": "Otak Bisnis — Fraud Pattern Detector & Risk Scoring",
        "icon": "🐕",
        "desc": "Analisis pola fraud lintas kasir/cabang/waktu, risk scoring 0–100, "
                "dan eskalasi ke Cloud AI hanya jika risk >= HIGH.",
    },
    {
        "id":   8,
        "name": "Sentinel",
        "role": "Imun Fisik — Server & Infrastructure Monitor",
        "icon": "🖥️",
        "desc": "Monitor uptime, CPU, memory, disk, API latency, dan status DB 24/7. "
                "Alert Admin jika ada degradasi infrastruktur.",
    },
    {
        "id":   9,
        "name": "Legalist",
        "role": "Imun Hukum — Compliance, NDA & Legal Monitoring",
        "icon": "⚖️",
        "desc": "Pastikan operasional comply UU PDP, NDA klien, retensi data audit, "
                "SLA monitoring, dan deteksi PII exposure di logs.",
    },
    {
        "id":   10,
        "name": "Treasurer",
        "role": "Kantong — Profit & Expense Calculator",
        "icon": "💰",
        "desc": "Hitung MRR, ARR, gross margin, COGS, komisi referral, "
                "proyeksi profit, dan breakdown pengeluaran bulanan.",
    },
]
