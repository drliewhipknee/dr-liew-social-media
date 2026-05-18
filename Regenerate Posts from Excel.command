#!/bin/bash
# ──────────────────────────────────────────────────────
#  Regenerate Posts from Excel
#  ─────────────────────────────────────────────────────
#  1. Reads posts_schedule.xlsx
#  2. Regenerates posts_data.py and posts_data2.py
#  3. Pushes to GitHub so the automation uses the new text
#
#  Double-click this file in Finder to run it.
# ──────────────────────────────────────────────────────
cd "$(dirname "$0")"

echo ""
echo "═══════════════════════════════════════════════════"
echo "  Regenerating posts from Excel..."
echo "═══════════════════════════════════════════════════"
echo ""

# Step 1: Convert Excel → Python files
python3 excel_to_posts.py
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Conversion failed. Check the error above."
    echo "Press any key to close..."
    read -n 1
    exit 1
fi

echo ""
echo "Pushing to GitHub..."

# Remove stale git locks
rm -f .git/index.lock .git/HEAD.lock

# Stage and commit
git add posts_data.py posts_data2.py
git diff --cached --quiet && echo "No changes to commit." || (
    git commit -m "Update post content from posts_schedule.xlsx"
    git push && echo "" && echo "✅ Changes pushed! The automation will use the updated posts." || echo "❌ Push failed — check your internet connection."
)

echo ""
echo "Press any key to close..."
read -n 1
