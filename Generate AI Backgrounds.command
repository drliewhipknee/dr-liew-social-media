#!/bin/bash
# ──────────────────────────────────────────────────────
#  Generate Post Images via Kie.ai (GPT Image 2)
#  ─────────────────────────────────────────────────────
#  Sends each post's "Kie.ai Image Description" to
#  GPT Image 2 via Kie.ai and saves the complete
#  finished image to generated_images/.
#
#  Already-generated images are skipped automatically
#  (no credits wasted on re-runs).
#
#  After this completes, run:
#    Push Images to GitHub.command
#
#  Double-click this file in Finder to run it.
# ──────────────────────────────────────────────────────

SCRIPT_DIR="/Users/cwl/Desktop/Claude Missions/Dr Liew Social Media/Automation Scripts"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Dr Liew — Kie.ai Image Generator"
echo "  (GPT Image 2)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$SCRIPT_DIR" || {
    echo "❌  Could not find Automation Scripts folder at:"
    echo "    $SCRIPT_DIR"
    echo ""
    read -p "Press Enter to close..."
    exit 1
}

echo "📁  Folder: $SCRIPT_DIR"
echo ""
echo "🎨  Generating images for all pending posts..."
echo "    Already-generated images will be skipped."
echo "    (This takes several minutes — one API call per post)"
echo ""

pip install requests --break-system-packages -q

python3 generate_images_kie.py "$@"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅  Done! Images saved to: generated_images/"
echo "  Next step: run Push Images to GitHub.command"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Press Enter to close..."
