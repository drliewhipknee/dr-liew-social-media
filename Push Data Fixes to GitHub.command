#!/bin/bash
# Push emoji encoding fixes in posts_data.py and posts_data2.py to GitHub
cd "$(dirname "$0")"

echo "══ Push Data Fixes to GitHub ══════════════════"

# Remove stale lock if present
if [ -f ".git/index.lock" ]; then
  echo "Removing stale git lock..."
  rm -f ".git/index.lock"
fi

git add posts_data.py posts_data2.py
git commit -m "Fix emoji encoding in post captions (replace surrogate pairs with proper Unicode)"
git push

echo ""
echo "✅ Done — emoji fixes are now in GitHub."
echo "Press any key to close..."
read -n 1
