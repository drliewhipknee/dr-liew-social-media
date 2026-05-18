#!/bin/bash
# ══════════════════════════════════════════════════════
#  Dr Liew — Sync Everything to GitHub
# ══════════════════════════════════════════════════════
#  Runs all steps in the correct order so posts_data,
#  images, and GitHub are always in sync:
#
#  STEP 1 — Regenerate posts_data.py files from Excel
#            (captions, hashtags, topics, website links)
#  STEP 2 — Generate any pending images via Kie.ai
#            (already-generated images are skipped)
#  STEP 3 — Push images + updated Python files to GitHub
#
#  Safe to run anytime. Already-done images are skipped.
#  Double-click to run.
# ══════════════════════════════════════════════════════
cd "$(dirname "$0")"

echo ""
echo "══════════════════════════════════════════════"
echo "  Dr Liew — Sync Everything to GitHub"
echo "══════════════════════════════════════════════"
echo ""
echo "  This runs 3 steps in sequence:"
echo "  1. Regenerate post data files from Excel"
echo "  2. Generate pending images via Kie.ai"
echo "  3. Push everything to GitHub"
echo ""
echo "  Already-generated images are skipped."
echo "  (New images may take several minutes each)"
echo ""
read -p "  Press Enter to start, or Ctrl+C to cancel... "
echo ""

# ── Install dependencies quietly ─────────────────────
pip install requests openpyxl --break-system-packages -q

# ── STEP 1: Regenerate post data files ───────────────
echo ""
echo "──────────────────────────────────────────────"
echo "  STEP 1 of 3 — Regenerating post data files"
echo "  (posts_data.py / posts_data2.py from Excel)"
echo "──────────────────────────────────────────────"
echo ""

python3 excel_to_posts.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌  Step 1 failed. Check the error above."
    echo "    posts_data.py may not have been updated."
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

echo ""
echo "  ✅  Post data files regenerated."

# ── STEP 2: Generate pending images ──────────────────
echo ""
echo "──────────────────────────────────────────────"
echo "  STEP 2 of 3 — Generating pending images"
echo "  (Kie.ai GPT Image 2 — skips existing images)"
echo "──────────────────────────────────────────────"
echo ""

# Count how many images still need generating
PENDING=$(python3 -c "
import json, openpyxl
from pathlib import Path
from datetime import datetime

XLSX = Path('posts_schedule.xlsx')
OUT  = Path('generated_images')
ACTIVE_FROM = 79

ASPECT = {'instagram':'1:1','linkedin':'16:9','facebook':'1:1'}

try:
    wb = openpyxl.load_workbook(XLSX)
    ws = wb['Posts Schedule']
    pending = 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        pid = row[0]
        if pid is None: continue
        try: pid = int(pid)
        except: continue
        if pid < ACTIVE_FROM: continue
        dt = row[1]
        d_str = dt.strftime('%Y-%m-%d') if isinstance(dt, datetime) else str(dt or '').strip()
        platform = str(row[3] or '').strip().lower()
        fmt      = str(row[4] or '').strip().lower()
        kie_desc = str(row[12] or '').strip()
        if not kie_desc: continue
        is_carousel = 'carousel' in fmt or 'infographic' in fmt
        if is_carousel:
            segments = [s.strip() for s in kie_desc.split('|') if s.strip()]
            for i, _ in enumerate(segments):
                suf = f'slide{[2,4,6,8][i%4]}'
                if not (OUT / f'{d_str}-{platform}-{suf}.jpg').exists():
                    pending += 1
            if not (OUT / f'{d_str}-{platform}-slide1.jpg').exists():
                pending += 1
        else:
            if not (OUT / f'{d_str}-{platform}.jpg').exists():
                pending += 1
    print(pending)
except Exception as e:
    print(0)
" 2>/dev/null)

echo "  Images pending: $PENDING"
echo ""

if [ "$PENDING" -gt 0 ]; then
    echo "  Generating $PENDING image(s) — please wait..."
    echo "  (~30–90 seconds per image)"
    echo ""
    python3 generate_images_kie.py
    if [ $? -ne 0 ]; then
        echo ""
        echo "⚠️   Image generation had errors — continuing to push."
        echo "    Check the output above for details."
    fi
else
    echo "  ✅  All images already generated — nothing to do."
fi

# ── STEP 3: Push to GitHub ────────────────────────────
echo ""
echo "──────────────────────────────────────────────"
echo "  STEP 3 of 3 — Pushing to GitHub"
echo "──────────────────────────────────────────────"
echo ""

python3 push_images.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌  Push failed. Check git credentials and connection."
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

# ── Done ─────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════"
echo "  ✅  All done — everything is in sync!"
echo ""
echo "  What was updated:"
echo "  • posts_data.py / posts_data2.py — rebuilt from Excel"
echo "  • generated_images/ → images/ — synced"
echo "  • GitHub — pushed and live"
echo ""
echo "  Instagram & LinkedIn will post automatically"
echo "  on their next scheduled time."
echo "══════════════════════════════════════════════"
echo ""
read -p "Press Enter to close..."
