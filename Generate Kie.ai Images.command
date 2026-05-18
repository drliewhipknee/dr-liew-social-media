#!/bin/bash
# ──────────────────────────────────────────────────────
#  Generate Kie.ai Images
#  ─────────────────────────────────────────────────────
#  Sends each post's "Kie.ai Image Description" to
#  GPT Image 2 via Kie.ai and saves the finished image
#  to generated_images/.
#
#  Images are saved with the correct filename so poster.py
#  can find them automatically.
#
#  Double-click this file in Finder to run it.
# ──────────────────────────────────────────────────────
cd "$(dirname "$0")"

echo ""
echo "═══════════════════════════════════════════════════"
echo "  Generating images via Kie.ai GPT Image 2..."
echo "═══════════════════════════════════════════════════"
echo ""

pip install requests --break-system-packages -q

python3 generate_images_kie.py "$@"

echo ""
echo "Press any key to close..."
read -n 1
