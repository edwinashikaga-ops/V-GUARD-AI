#!/bin/bash
# ============================================================
# V-Guard AI — Fix Build Error & Push
# Jalankan dari folder repo: C:\Users\Asus\vguard-ui
# ============================================================

set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   V-Guard AI — Fix Build Script         ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# 1. Pastikan kita di folder repo yang benar
echo "▶ [1/4] Cek direktori..."
pwd
git status --short

# 2. Update vercel.json dengan konfigurasi yang benar
echo "▶ [2/4] Update vercel.json..."
cat > vercel.json << 'VERCELJSON'
{
  "version": 2,
  "installCommand": "npm install -g pnpm && pnpm install",
  "buildCommand": "pnpm run build",
  "outputDirectory": "dist/public",
  "framework": null,
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/$1"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
VERCELJSON

echo "vercel.json updated ✅"

# 3. Commit
echo "▶ [3/4] Git commit..."
git add vercel.json
git commit -m "fix: vercel.json — fix build command, outputDir dist/public, install pnpm"

# 4. Push ke KEDUA branch (master dan main) agar Vercel detect
echo "▶ [4/4] Push ke master dan main..."
git push origin master

# Buat branch main dari master dan push juga
git checkout -b main 2>/dev/null || git checkout main
git merge master --no-edit
git push origin main

git checkout master

echo ""
echo "✅ Selesai! Push ke master dan main berhasil."
echo "   Vercel akan otomatis build dari branch main."
echo "   Pantau: https://vercel.com/vguard-ais-projects/v-guard-ai/deployments"
echo ""
