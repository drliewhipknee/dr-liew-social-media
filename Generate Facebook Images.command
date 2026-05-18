#!/bin/bash
cd "$(dirname "$0")"
echo "=================================================="
echo "  Generating 21 Facebook images via Kie.ai"
echo "  (includes Dr Liew headshot in bottom-right)"
echo "  Date range: 2026-05-08 → 2026-09-22"
echo "=================================================="
echo ""
python3 generate_images_kie.py \
    --platform facebook \
    --from-date 2026-05-08 \
    --to-date 2026-09-22 \
    --force
echo ""
echo "=================================================="
echo "  Facebook images done! Review in generated_images/"
echo "  Then push to GitHub when ready."
echo "=================================================="
echo ""
read -p "Push to GitHub now? (y/n): " choice
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    bash "Push Images to GitHub.command"
fi
