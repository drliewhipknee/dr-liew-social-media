#!/bin/bash
# Double-click this file to push approved images to GitHub.
# Run this AFTER reviewing the images in the generated_images folder.

SCRIPT_DIR="/Users/cwl/Desktop/Claude Missions/Dr Liew Social Media/Automation Scripts"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Dr Liew — Push Images to GitHub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$SCRIPT_DIR" || { echo "❌  Could not find Automation Scripts folder at:"; echo "    $SCRIPT_DIR"; echo ""; read -p "Press Enter to close..."; exit 1; }

# Count images ready to push
IMAGE_COUNT=$(find generated_images -name "*.jpg" -o -name "*.png" 2>/dev/null | grep -v _progress | wc -l | tr -d ' ')

echo "📁  Folder: $SCRIPT_DIR"
echo "🖼️   Images ready: $IMAGE_COUNT"
echo ""

if [ "$IMAGE_COUNT" -eq 0 ]; then
    echo "❌  No images found in generated_images/"
    echo "    Run 'Generate AI Backgrounds.command' first."
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

echo "⚠️   About to push $IMAGE_COUNT images to GitHub."
echo "    This will make them live in the scheduling system."
echo ""
read -p "   Are you happy with the images? Press Enter to push, or Ctrl+C to cancel... "

echo ""
echo "🚀  Pushing to GitHub..."
echo ""

python3 push_images.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Press Enter to close..."
