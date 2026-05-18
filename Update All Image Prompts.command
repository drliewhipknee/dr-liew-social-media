#!/bin/bash
# ──────────────────────────────────────────────────────
#  Update All Kie.ai Image Prompts
#  ─────────────────────────────────────────────────────
#  Writes a high-quality, art-directed Kie.ai prompt
#  for every active post (IDs 79+) in posts_schedule.xlsx.
#
#  Platform layouts:
#    Instagram (1:1)  — floating navy panel, photography top
#    LinkedIn  (16:9) — panel left, photography right
#    Facebook  (1:1)  — floating panel, reserved circle
#                       bottom-right for Dr Liew's headshot
#
#  After this completes, run:
#    1. Regenerate Posts from Excel.command
#    2. Generate Kie.ai Images.command
#    3. Push Images to GitHub.command
#
#  Double-click to run.
# ──────────────────────────────────────────────────────
cd "$(dirname "$0")"

echo ""
echo "═══════════════════════════════════════════════════"
echo "  Dr Liew — Update All Kie.ai Image Prompts"
echo "═══════════════════════════════════════════════════"
echo ""

pip install openpyxl --break-system-packages -q

python3 update_all_kie_prompts.py

echo ""
echo "Press any key to close..."
read -n 1
