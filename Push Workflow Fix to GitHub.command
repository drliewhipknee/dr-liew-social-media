#!/bin/bash
cd "$(dirname "$0")"
rm -f .git/index.lock .git/HEAD.lock
git add posts_data.py
git commit -m "Remove posts 79 & 80 (Eastwood + Colleagues) — already posted manually"
git push && echo "✅ Done!" || echo "❌ Failed"
read -n 1
