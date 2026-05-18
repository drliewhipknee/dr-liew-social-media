#!/bin/bash
# ──────────────────────────────────────────────────
#  Push Eastwood + Colleagues carousel images & posts_data to GitHub
#  Double-click this file in Finder to run it.
# ──────────────────────────────────────────────────
cd "$(dirname "$0")"

echo ""
echo "═══════════════════════════════════════════"
echo "  Pushing new carousel posts to GitHub"
echo "═══════════════════════════════════════════"
echo ""

# Remove stale git lock if present
LOCK=".git/index.lock"
if [ -f "$LOCK" ]; then
    echo "⚠️  Removing stale git lock file..."
    rm -f "$LOCK"
fi

# Stage our new files
echo "Staging files..."
git add posts_data.py \
    images/2026-04-15-instagram-slide1.jpg \
    images/2026-04-15-instagram-slide2.jpg \
    images/2026-04-15-instagram-slide3.jpg \
    images/2026-04-15-instagram-slide4.jpg \
    images/2026-04-15-instagram-slide5.jpg \
    images/2026-04-15-instagram-slide6.jpg \
    images/2026-04-17-instagram-slide1.jpg \
    images/2026-04-17-instagram-slide2.jpg \
    images/2026-04-17-instagram-slide3.jpg

# Commit
git commit -m "Add Eastwood + Colleagues Instagram carousels (Apr 15 & Apr 17)"

# Push
if git push; then
    echo ""
    echo "✅  All files pushed to GitHub!"
    echo ""
    echo "Now go to GitHub → Actions and run the workflow:"
    echo "  1. Eastwood post   → date: 2026-04-15"
    echo "  2. Colleagues post → date: 2026-04-17"
else
    echo ""
    echo "❌  Push failed. See error above."
fi

echo ""
echo "Press any key to close..."
read -n 1
