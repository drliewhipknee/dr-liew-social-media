#!/bin/bash
# ──────────────────────────────────────────────────────
#  Update Carousel Slide Prompts
#  ─────────────────────────────────────────────────────
#  Writes explicit, art-directed Kie.ai prompts for all
#  16 carousel posts. Each slide has real heading + body
#  text embedded directly in the image prompt — so the
#  AI renders your actual content, not placeholder text.
#
#  After running this, regenerate carousel images:
#    1. Run 'Regenerate Posts from Excel.command'
#    2. Run 'Generate Kie.ai Images.command'
#    3. Run 'Push Images to GitHub.command'
#
#  Or just run 'Sync Everything.command' for all steps.
#
#  Double-click to run.
# ──────────────────────────────────────────────────────
cd "$(dirname "$0")"

echo ""
echo "═══════════════════════════════════════════════════"
echo "  Dr Liew — Update Carousel Slide Prompts"
echo "═══════════════════════════════════════════════════"
echo ""
echo "  This writes explicit slide text into the Kie.ai"
echo "  image prompts for all 16 carousel posts."
echo ""

pip install openpyxl --break-system-packages -q

python3 update_carousel_prompts.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌  Failed. Check the error above."
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

echo ""
echo "  What to do next:"
echo "  • Run 'Sync Everything.command' to regenerate + push"
echo "  • Or use --force flag to regenerate carousel images only:"
echo "    python3 generate_images_kie.py --id 83 --force"
echo ""
read -p "Press Enter to close..."
