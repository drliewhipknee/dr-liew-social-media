#!/bin/bash
# Test: generate one complete LinkedIn image via kie.ai GPT Image-2 (background + text in one call)
# Output is cropped to exact LinkedIn dimensions: 1200 x 627 px
# Cost: ~$0.05 per image (2K resolution via kie.ai)

SCRIPT_DIR="/Users/cwl/Desktop/Claude Missions/Dr Liew Social Media/Automation Scripts"
cd "$SCRIPT_DIR" || exit 1

python3 - << 'PYEOF'
import os, sys, time, json, requests
from pathlib import Path
from PIL import Image, ImageOps
from io import BytesIO

SCRIPT_DIR = "/Users/cwl/Desktop/Claude Missions/Dr Liew Social Media/Automation Scripts"

# ── kie.ai API Key ──────────────────────────────────────────────────────────────
KIE_API_KEY = "961df6a53af50676575fee66b918b68c"

# ── LinkedIn canvas: 1200 x 627 px (ratio ~1.914:1)
# kie.ai 16:9 native output (1.778:1) — minimal centre-crop to reach 1.914:1
# Safe-zone instruction in prompt keeps all text clear of the crop area.
TARGET_W, TARGET_H = 1200, 627

prompt = (
    "Professional LinkedIn social media post graphic for an orthopaedic surgeon's brand. "
    "IMPORTANT LAYOUT: All text and content must stay within the centre 85% of the image height "
    "— keep a clear margin at top and bottom with no text near the edges. "
    "Image is wider than tall (landscape orientation, 16:9). "
    "\n\n"
    "LEFT PANEL (55% of width): Deep navy background (#16233A) at approximately 90% opacity, "
    "creating a clean, dark text zone. Behind the headline text, add an extremely faint "
    "soft-glow bloom in brand light blue (#A2B9D8) — barely visible, just a whisper of "
    "luminescence that adds depth and dimensionality. No orange, no gold, no harsh halo. "
    "\n\n"
    "RIGHT PANEL (45% of width): Background scene — empty modern private hospital atrium, "
    "tall floor-to-ceiling windows with soft natural daylight, polished marble floors, "
    "clean white and steel architecture. No people. The background bleeds naturally into "
    "the navy panel with a soft gradient edge. "
    "\n\n"
    "TEXT ON NAVY PANEL (left-aligned, crisp modern sans-serif): "
    "TOP — small uppercase tracking label in brand light blue (#A2B9D8): 'ORTHOPAEDICS 360' "
    "CENTRE — large bold white headline (max 2 lines, large font): "
    "'Direct Anterior Approach for Total Hip Replacement' "
    "BELOW HEADLINE — medium-weight white body text (1-2 lines): "
    "'Clinical advantages, patient selection, and what to expect from the DAA approach.' "
    "BOTTOM — clearly readable brand light-blue website URL: 'drchienwenliew.com.au' "
    "\n\n"
    "BRAND WORDMARK — bottom-left corner of the navy panel, below the URL, with clear breathing room: "
    "A typographic wordmark in two parts. First, '(DR)' in small, light-weight uppercase sans-serif, "
    "colour: light blue #A2B9D8. Immediately to the right of '(DR)', 'LIEW' in large bold uppercase "
    "sans-serif, colour: white. The word 'LIEW' is significantly larger than '(DR)' — roughly 2.5x "
    "the height. Both sit on the same baseline. Clean, minimal, architectural — no underline, no box, "
    "no icon. Just the two typographic elements side by side. "
    "\n\n"
    "Typography throughout: clean geometric sans-serif (Neue Montreal or similar — structured, Swiss-inspired). "
    "All text must be sharp, legible, and properly kerned — no blurry or distorted letters. "
    "Colour palette: deep navy #16233A, pure white, light blue #A2B9D8. "
    "No clip art, no borders, no gradients that look cheap. "
    "Luxury private practice aesthetic — the kind of image a top Sydney surgeon would post."
)

headers = {
    "Authorization": f"Bearer {KIE_API_KEY}",
    "Content-Type": "application/json",
}

# ── Step 1: Submit task ─────────────────────────────────────────────────────────
print("Submitting to kie.ai GPT Image-2 (16:9, 2K) ...")
body = {
    "model": "gpt-image-2-text-to-image",
    "input": {
        "prompt": prompt,
        "aspect_ratio": "16:9",
        "resolution": "2K",
    },
}

resp = requests.post(
    "https://api.kie.ai/api/v1/jobs/createTask",
    headers=headers,
    json=body,
    timeout=30,
)

if resp.status_code != 200:
    print(f"ERROR {resp.status_code}: {resp.text[:500]}")
    sys.exit(1)

data = resp.json()
task_id = data.get("data", {}).get("taskId")
if not task_id:
    print(f"ERROR: No taskId in response: {data}")
    sys.exit(1)

print(f"Task submitted. ID: {task_id}")

# ── Step 2: Poll for result ─────────────────────────────────────────────────────
print("Waiting for generation", end="", flush=True)
max_wait = 600   # 10 minutes
interval = 3
elapsed = 0

while elapsed < max_wait:
    time.sleep(interval)
    elapsed += interval
    print(".", end="", flush=True)

    poll = requests.get(
        "https://api.kie.ai/api/v1/jobs/recordInfo",
        headers=headers,
        params={"taskId": task_id},
        timeout=30,
    )

    if poll.status_code != 200:
        print(f"\nPoll error {poll.status_code}: {poll.text[:200]}")
        continue

    poll_data = poll.json().get("data", {})
    state = poll_data.get("state", "")

    if state == "fail":
        print(f"\nTask failed: {poll_data.get('failMsg', 'unknown error')}")
        sys.exit(1)

    if state == "success":
        print("\nGeneration complete!")
        # resultJson is a JSON string — parse it
        result_json_str = poll_data.get("resultJson", "{}")
        try:
            result = json.loads(result_json_str)
        except Exception:
            result = {}

        # Extract image URL — kie.ai returns resultUrls as dict or list
        result_urls = result.get("resultUrls", result.get("imageUrls", {}))
        if isinstance(result_urls, dict):
            img_url = next(iter(result_urls.values()), None)
        elif isinstance(result_urls, list):
            img_url = result_urls[0] if result_urls else None
        else:
            img_url = None

        if not img_url:
            print(f"ERROR: Could not find image URL in result: {result}")
            print(f"Full poll data: {poll_data}")
            sys.exit(1)

        print(f"Image URL: {img_url[:80]}...")
        break
else:
    print(f"\nTimed out after {max_wait}s")
    sys.exit(1)

# ── Step 3: Download image ──────────────────────────────────────────────────────
print("Downloading image ...")
img_resp = requests.get(img_url, timeout=120)
if img_resp.status_code != 200:
    print(f"ERROR downloading image: {img_resp.status_code}")
    sys.exit(1)

raw = Image.open(BytesIO(img_resp.content)).convert("RGB")
print(f"Raw size from kie.ai: {raw.width} x {raw.height}")

# ── Step 4: Crop to LinkedIn canvas (1200 x 627) ────────────────────────────────
# 16:9 at width=1200 → height=675; crop 24px total (12 top, 12 bottom) to get 627
scale = TARGET_W / raw.width
new_h = round(raw.height * scale)
resized = raw.resize((TARGET_W, new_h), Image.LANCZOS)
print(f"After resize: {resized.width} x {resized.height}")

if new_h >= TARGET_H:
    top = (new_h - TARGET_H) // 2
    final = resized.crop((0, top, TARGET_W, top + TARGET_H))
else:
    final = ImageOps.pad(resized, (TARGET_W, TARGET_H), color=(22, 35, 54))

print(f"Final size: {final.width} x {final.height}")

# ── Step 5: Save ────────────────────────────────────────────────────────────────
out_dir = Path(SCRIPT_DIR) / "generated_images"
out_dir.mkdir(exist_ok=True)
out_path = out_dir / "test_linkedin_complete.png"
final.save(str(out_path), "PNG", optimize=True)
print(f"\nSaved to: {out_path}")
print("Open generated_images/test_linkedin_complete.png to review.")
PYEOF

read -p "Press Enter to close..."
