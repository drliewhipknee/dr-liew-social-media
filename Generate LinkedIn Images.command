#!/bin/bash
cd "$(dirname "$0")"
echo "=================================================="
echo "  Generating LinkedIn images via Kie.ai"
echo "  (80 posts total, 16:9 format)"
echo "  Date range: 2026-04-30 → 2027-01-30"
echo "=================================================="
echo ""
echo "  Regenerating ALL images with new brand descriptions."
echo ""
python3 generate_images_kie.py \
    --platform linkedin \
    --from-date 2026-04-30 \
    --to-date 2027-01-30 \
    --force
echo ""
echo "=================================================="
echo "  LinkedIn images done! Review in generated_images/"
echo "  Then push to GitHub when ready."
echo "=================================================="
echo ""
read -p "Push to GitHub now? (y/n): " choice
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    bash "Push Images to GitHub.command"
fi
