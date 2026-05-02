# =============================================================================
# V-GUARD AI INTELLIGENCE — snippet_1_ai_agents.py
# AI Agent roster metadata for display in the War Room Admin panel.
# Mirrors the 10 Elite AI Squad defined in logic_vguard.py.
# =============================================================================

ai_agents = [
    {
        "id":   1,
        "name": "Visionary",
        "role": "CCTV Visual Intelligence",
        "icon": "👁️",
        "desc": "Mengawasi feed CCTV, deteksi anomali visual, render overlay transaksi real-time di atas feed kamera.",
    },
    {
        "id":   2,
        "name": "Concierge",
        "role": "CS & Onboarding Intelligence",
        "icon": "🤝",
        "desc": "Lead scoring, deteksi kebutuhan klien, rekomendasi paket terbaik, dan onboarding pasca aktivasi.",
    },
    {
        "id":   3,
        "name": "GrowthHacker",
        "role": "Marketing & Branding Automation",
        "icon": "📣",
        "desc": "Content marketing, referral campaign, A/B test copywriting, dan WA blast otomatis per paket.",
    },
    {
        "id":   4,
        "name": "Liaison",
        "role": "POS / SAP / Moka Integration + Local Filter",
        "icon": "🔗",
        "desc": "Integrasi POS eksternal (Moka, SAP, iReap, Majoo, Olsera, Pawoon) + filter lokal 6 rules sebelum kirim ke Cloud AI.",
    },
    {
        "id":   5,
        "name": "Analyst",
        "role": "Financial Forensic & Bank Reconciliation",
        "icon": "🏦",
        "desc": "Rekonsiliasi kasir vs mutasi bank, forensik keuangan, identifikasi selisih, dan laporan audit otomatis.",
    },
    {
        "id":   6,
        "name": "Stockmaster",
        "role": "Inventory Intelligence & OCR Invoice",
        "icon": "📦",
        "desc": "Update stok real-time via OCR invoice supplier drag & drop, pantau level stok, reorder alert otomatis.",
    },
    {
        "id":   7,
        "name": "Watchdog",
        "role": "Fraud Pattern Detector & Risk Scoring",
        "icon": "🐕",
        "desc": "Analisis pola fraud lintas kasir/cabang/waktu, risk scoring, keputusan eskalasi ke Cloud AI hanya jika HIGH/CRITICAL.",
    },
    {
        "id":   8,
        "name": "Sentinel",
        "role": "Server & Infrastructure Monitor",
        "icon": "🖥️",
        "desc": "Monitor uptime, CPU/memory/disk, API latency, dan status koneksi infrastruktur 24/7.",
    },
    {
        "id":   9,
        "name": "Legalist",
        "role": "Compliance, NDA & Legal Monitoring",
        "icon": "⚖️",
        "desc": "Monitor kepatuhan UU PDP, NDA klien, retensi data audit, SLA monitoring, dan deteksi PII exposure di logs.",
    },
    {
        "id":   10,
        "name": "Treasurer",
        "role": "Profit & Expense Calculator",
        "icon": "💰",
        "desc": "Hitung MRR, ARR, gross margin, COGS, komisi referral, proyeksi profit, dan breakdown pengeluaran bulanan.",
    },
]

# Alias — app.py imports as AI_AGENTS in some references
AI_AGENTS = ai_agents
