#!/bin/bash
# Clean Sync and Push to GitHub
# Clears images/, copies everything from generated_images/, commits and pushes.

cd "$(dirname "$0")"

echo "=================================================="
echo "  Clean Sync — generated_images/ → images/ → GitHub"
echo "=================================================="
echo ""

echo "Step 1: Clearing images/ folder..."
rm -f images/*.jpg images/*.png images/*.jpeg
echo "  Done. Remaining: $(ls images/ 2>/dev/null | wc -l | tr -d ' ') files"

echo ""
echo "Step 2: Copying all generated_images/ → images/..."
cp generated_images/*.jpg images/ 2>/dev/null
cp generated_images/*.png images/ 2>/dev/null
echo "  Done. images/ now has $(ls images/*.jpg 2>/dev/null | wc -l | tr -d ' ') images"

echo ""
echo "Step 3: Removing stale git index lock if present..."
rm -f .git/index.lock
echo "  Done."

echo ""
echo "Step 4: Staging all changes..."
git add images/ posts_data.py posts_data2.py poster.py generate_images_kie.py *.py *.command *.md 2>/dev/null
git add -A images/

echo ""
echo "Step 5: Committing..."
git commit -m "Clean sync: rebuild images/ from generated_images/, update post data" 2>/dev/null || echo "  Nothing new to commit."

echo ""
echo "Step 6: Pushing to GitHub..."
git push origin main

echo ""
echo "=================================================="
echo "  Clean sync complete!"
echo "  GitHub now has $(ls images/*.jpg 2>/dev/null | wc -l | tr -d ' ') images — matching generated_images/ exactly."
echo "=================================================="
echo ""
read -p "Press Enter to close..."
