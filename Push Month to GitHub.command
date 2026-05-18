#!/bin/bash
# ══════════════════════════════════════════════════════
#  Dr Liew — Push One Month of Content to GitHub
# ══════════════════════════════════════════════════════
#  Generates images for a single calendar month only,
#  then pushes everything to GitHub.
#
#  1. You choose the month (e.g. "2026-06" for June)
#  2. Images for that month are generated (skipping any
#     already done)
#  3. Everything is pushed to GitHub — posts go live on
#     their scheduled dates automatically
#
#  Run this each month when you're happy with the posts.
#  Already-generated images from earlier months stay on
#  GitHub — only the new month's images are added.
#
#  Double-click to run.
# ══════════════════════════════════════════════════════
cd "$(dirname "$0")"

echo ""
echo "══════════════════════════════════════════════════════"
echo "  Dr Liew — Push One Month of Content to GitHub"
echo "══════════════════════════════════════════════════════"
echo ""

# ── Ask which month ───────────────────────────────────
# Default = next calendar month
CURRENT_YEAR=$(date +%Y)
CURRENT_MONTH=$(date +%m)

# Calculate next month
if [ "$CURRENT_MONTH" -eq 12 ]; then
    NEXT_MONTH="01"
    NEXT_YEAR=$((CURRENT_YEAR + 1))
else
    NEXT_MONTH=$(printf "%02d" $((10#$CURRENT_MONTH + 1)))
    NEXT_YEAR=$CURRENT_YEAR
fi

DEFAULT_MONTH="${NEXT_YEAR}-${NEXT_MONTH}"

echo "  Which month do you want to generate and push?"
echo "  Format: YYYY-MM  (e.g. 2026-06 for June 2026)"
echo ""
read -p "  Month [$DEFAULT_MONTH]: " INPUT_MONTH
echo ""

# Use default if nothing entered
if [ -z "$INPUT_MONTH" ]; then
    INPUT_MONTH="$DEFAULT_MONTH"
fi

# Validate format
if ! echo "$INPUT_MONTH" | grep -qE "^[0-9]{4}-[0-9]{2}$"; then
    echo "❌  Invalid format. Please use YYYY-MM (e.g. 2026-06)"
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

YEAR="${INPUT_MONTH%-*}"
MONTH="${INPUT_MONTH#*-}"

# Last day of month (handles varying month lengths + leap years)
LAST_DAY=$(python3 -c "
import calendar
print(calendar.monthrange(${YEAR}, ${MONTH#0})[1])
" 2>/dev/null)

if [ -z "$LAST_DAY" ]; then
    LAST_DAY=31
fi

FROM_DATE="${INPUT_MONTH}-01"
TO_DATE="${INPUT_MONTH}-${LAST_DAY}"

# Human-readable month name
MONTH_NAME=$(python3 -c "
from datetime import date
d = date(${YEAR}, ${MONTH#0}, 1)
print(d.strftime('%B %Y'))
" 2>/dev/null || echo "$INPUT_MONTH")

echo "══════════════════════════════════════════════════════"
echo "  Month selected: $MONTH_NAME  ($FROM_DATE → $TO_DATE)"
echo "══════════════════════════════════════════════════════"
echo ""

# ── Install dependencies ──────────────────────────────
pip install requests openpyxl --break-system-packages -q

# ── Count pending images for this month ──────────────
echo "  Checking which images still need generating..."
echo ""

PENDING=$(python3 -c "
import json, openpyxl
from pathlib import Path
from datetime import datetime

XLSX = Path('posts_schedule.xlsx')
OUT  = Path('generated_images')

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
        if pid < 79: continue
        dt = row[1]
        d_str = dt.strftime('%Y-%m-%d') if isinstance(dt, datetime) else str(dt or '').strip()
        if d_str < '${FROM_DATE}' or d_str > '${TO_DATE}': continue
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

echo "  Images pending for $MONTH_NAME: $PENDING"
echo ""

if [ "$PENDING" -gt 0 ]; then
    echo "──────────────────────────────────────────────────────"
    echo "  STEP 1 — Generating $PENDING image(s) for $MONTH_NAME"
    echo "  (~30–90 seconds per image)"
    echo "──────────────────────────────────────────────────────"
    echo ""
    python3 generate_images_kie.py --from-date "$FROM_DATE" --to-date "$TO_DATE"
    if [ $? -ne 0 ]; then
        echo ""
        echo "⚠️   Some images had errors — continuing to push anyway."
        echo "    Check output above. You can re-run this script to retry."
        echo ""
    fi
else
    echo "  ✅  All images for $MONTH_NAME already generated — nothing to generate."
    echo ""
fi

# ── Push to GitHub ────────────────────────────────────
echo "──────────────────────────────────────────────────────"
echo "  STEP 2 — Pushing $MONTH_NAME content to GitHub"
echo "──────────────────────────────────────────────────────"
echo ""

python3 push_images.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌  Push failed. Check git credentials and internet connection."
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

# ── Done ─────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════"
echo "  ✅  $MONTH_NAME is live on GitHub!"
echo ""
echo "  Posts will go live automatically on their scheduled"
echo "  dates via GitHub Actions (Instagram, LinkedIn) and"
echo "  the Claude scheduled task (Facebook)."
echo ""
echo "  Reminder: Run this again around the 26th of the"
echo "  month to push the NEXT month's content on time."
echo "══════════════════════════════════════════════════════"
echo ""
read -p "Press Enter to close..."
