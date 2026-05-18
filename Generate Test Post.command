#!/bin/bash
# ──────────────────────────────────────────────────────
#  Generate Test Post — Refined Design
#  ─────────────────────────────────────────────────────
#  Generates one test image with the refined design:
#  • Cinematic warm outdoor lifestyle photography
#  • Floating navy panel — glow behind the panel
#  • Neue Montreal typeface
#  • Small (DR) + large LIEW logo
#  • Full title, no truncation
#  • Prominent website URL
#
#  Output: generated_images/test-post.jpg
#
#  Double-click to run.
# ──────────────────────────────────────────────────────
cd "$(dirname "$0")"

echo ""
echo "═══════════════════════════════════════════════════"
echo "  Dr Liew — Generate Test Post"
echo "═══════════════════════════════════════════════════"
echo ""

pip install requests --break-system-packages -q

python3 generate_test_post.py

echo ""
echo "Press any key to close..."
read -n 1
