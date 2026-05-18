#!/bin/bash
# Pushes only the Facebook and LinkedIn thumbnails that are already in images/
# Use this when images have been manually placed in images/ and just need committing.

SCRIPT_DIR="/Users/cwl/Desktop/Claude Missions/Dr Liew Social Media/Automation Scripts"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Dr Liew — Push Facebook & LinkedIn Images"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$SCRIPT_DIR" || {
    echo "❌  Could not find folder at:"
    echo "    $SCRIPT_DIR"
    read -p "Press Enter to close..."
    exit 1
}

# Remove stale git lock if present
if [ -f ".git/index.lock" ]; then
    echo "⚠️   Removing stale .git/index.lock..."
    rm -f ".git/index.lock"
fi

FB_COUNT=$(ls images/*facebook*.jpg 2>/dev/null | wc -l | tr -d ' ')
LI_COUNT=$(ls images/*linkedin*.jpg 2>/dev/null | wc -l | tr -d ' ')
echo "🖼️   Facebook images: $FB_COUNT"
echo "🖼️   LinkedIn images: $LI_COUNT"
echo ""

read -p "Press Enter to commit and push, or Ctrl+C to cancel... "
echo ""

git add images/*facebook*.jpg images/*linkedin*.jpg
git commit -m "Regenerate Facebook and LinkedIn thumbnails"
git push origin main

echo ""
if [ $? -eq 0 ]; then
    echo "✅  Done! Images are live on GitHub."
else
    echo "❌  Push failed. Check that you have internet and GitHub access."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Press Enter to close..."
