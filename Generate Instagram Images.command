#!/bin/bash
cd "$(dirname "$0")"
echo "=== Generating all 20 Instagram images (forced regeneration) ==="
python3 generate_images_kie.py --from-date 2026-05-05 --to-date 2026-07-10 --force
echo ""
echo "=== Done! Now pushing to GitHub ==="
bash "Push Images to GitHub.command"
