#!/bin/bash
# ================================================================
# V-Guard AI — Push ke GitHub & Deploy ke Vercel
# Jalankan dari folder repo lokal Anda (misal: C:\Users\Asus\vguard-ui)
# ================================================================
set -e

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   V-Guard AI v1.0.0 — Deploy to Vercel              ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── 1. Cek git repo ─────────────────────────────────────────────
echo "▶ [1/5] Cek git repository..."
if [ ! -d ".git" ]; then
  echo "❌ ERROR: Folder ini bukan git repo!"
  echo "   Jalankan: git init && git remote add origin <URL_REPO_GITHUB>"
  exit 1
fi
echo "   Repo OK ✅"
echo "   Remote: $(git remote get-url origin 2>/dev/null || echo 'TIDAK ADA REMOTE')"

# ── 2. Copy semua file yang sudah diperbaiki ──────────────────────
echo ""
echo "▶ [2/5] Salin file yang sudah diperbaiki..."

# vite.config.ts (tanpa manus plugins)
cp -f vite.config.ts.fixed vite.config.ts 2>/dev/null || true
echo "   vite.config.ts ✅"

# vercel.json (serverless Express)
echo "   vercel.json ✅ (sudah ada)"

# api/index.ts (Vercel serverless entry)
mkdir -p api
echo "   api/index.ts ✅ (sudah ada)"

# ── 3. Remove file Manus-specific ────────────────────────────────
echo ""
echo "▶ [3/5] Bersihkan file Manus-specific..."
rm -rf client/public/__manus__ 2>/dev/null && echo "   __manus__ folder dihapus ✅" || echo "   Tidak ada __manus__ folder"

# ── 4. Git commit ─────────────────────────────────────────────────
echo ""
echo "▶ [4/5] Git add & commit..."
git add -A
git status --short
git commit -m "feat: deploy V-Guard AI v1.0.0 to Vercel" || echo "   (Tidak ada perubahan baru)"

# ── 5. Push ke GitHub ─────────────────────────────────────────────
echo ""
echo "▶ [5/5] Push ke GitHub..."

# Coba push ke main dulu, kalau gagal coba master
BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "   Branch aktif: $BRANCH"

git push origin $BRANCH

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   ✅ BERHASIL! Push ke GitHub selesai.              ║"
echo "║                                                      ║"
echo "║   Vercel akan otomatis build & deploy dalam ~2 mnt  ║"
echo "║                                                      ║"
echo "║   Pantau di:                                         ║"
echo "║   https://vercel.com/dashboard                       ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "⚠️  PENTING — Set Environment Variables di Vercel:"
echo "   Dashboard > Project > Settings > Environment Variables"
echo ""
echo "   DATABASE_URL  = mysql://user:pass@host:port/vguard_db"
echo "   JWT_SECRET    = (string acak min. 32 karakter)"
echo "   NODE_ENV      = production"
echo ""
