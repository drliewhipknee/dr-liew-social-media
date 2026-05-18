#!/bin/bash
# ──────────────────────────────────────────────────────
#  Generate 5 Design Variations — Physiotherapy Post
#  ─────────────────────────────────────────────────────
#  Generates 5 background/style variations for the
#  physiotherapy post so you can compare and choose.
#
#  Output files:
#    generated_images/variation-1.jpg  (Deep Navy Abstract)
#    generated_images/variation-2.jpg  (Warm Lifestyle Outdoor)
#    generated_images/variation-3.jpg  (Luxury Architecture)
#    generated_images/variation-4.jpg  (Rich Amber Bokeh)
#    generated_images/variation-5.jpg  (Wellness Studio)
#
#  Double-click this file in Finder to run it.
# ──────────────────────────────────────────────────────
cd "$(dirname "$0")"

echo ""
echo "═══════════════════════════════════════════════════"
echo "  Generating 5 design variations via Kie.ai..."
echo "  (~5 min total — one API call per variation)"
echo "═══════════════════════════════════════════════════"
echo ""

pip install requests --break-system-packages -q

python3 generate_variations_test.py

echo ""
echo "Press any key to close..."
read -n 1
