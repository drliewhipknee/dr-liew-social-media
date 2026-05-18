#!/bin/bash
SCRIPT_DIR="/Users/cwl/Desktop/Claude Missions/Dr Liew Social Media/Automation Scripts"
cd "$SCRIPT_DIR" || exit 1

python3 - << 'PYEOF'
import sys, time, json, requests
from pathlib import Path
from PIL import Image
from io import BytesIO

KIE_API_KEY = "961df6a53af50676575fee66b918b68c"
TARGET_W, TARGET_H = 1080, 1080

prompt = (
    "Professional Instagram social media post graphic for an orthopaedic surgeon's brand. "
    "Image is square (1:1 aspect ratio). "
    "IMPORTANT LAYOUT: All text and content must stay within the centre 85% of the image — "
    "keep clear margins at all edges with no text near borders. "
    "\n\n"
    "BACKGROUND: warm abstract bokeh lights — golden and amber tones, soft depth of field. "
    "In the background, a softly blurred, anonymous figure of a person sitting on a bed, "
    "gently holding their hip — face not visible, purely atmospheric and human. "
    "The bokeh and warm tones create emotional warmth. "
    "\n\n"
    "BOTTOM PANEL (lower 38% of image): rounded-top semi-transparent deep navy panel #16233A "
    "at approximately 88% opacity, creating a clean dark reading area over the image. "
    "\n\n"
    "TEXT ON BOTTOM PANEL (left-aligned, crisp modern geometric sans-serif, Neue Montreal style): "
    "TOP of panel — small uppercase tracking label in brand light blue (#A2B9D8): 'ORTHOPAEDICS 360' "
    "CENTRE — large bold white headline (1 line, prominent): 'The Moment It Clicked' "
    "BELOW HEADLINE — small-medium white subtitle: 'When patients decide to take their life back' "
    "\n\n"
    "BOTTOM-LEFT of panel — brand wordmark: small light-weight '(DR)' in light blue #A2B9D8, "
    "immediately to its right 'LIEW' in large bold white — same baseline, 'LIEW' roughly 2.5x taller. "
    "BOTTOM-RIGHT of panel — small light blue URL text: 'drchienwenliew.com.au' "
    "\n\n"
    "Typography: clean geometric sans-serif throughout — sharp, legible, well-kerned. "
    "Colours: deep navy #16233A panel, pure white text, light blue #A2B9D8 accents, warm amber/gold bokeh. "
    "Aesthetic: luxury private orthopaedic practice — refined, warm, trustworthy."
)

headers = {"Authorization": f"Bearer {KIE_API_KEY}", "Content-Type": "application/json"}

print("Submitting to kie.ai GPT Image-2 (1:1, 2K) ...")
resp = requests.post(
    "https://api.kie.ai/api/v1/jobs/createTask",
    headers=headers,
    json={"model": "gpt-image-2-text-to-image", "input": {"prompt": prompt, "aspect_ratio": "1:1", "resolution": "2K"}},
    timeout=30,
)
if resp.status_code != 200:
    print(f"ERROR {resp.status_code}: {resp.text[:400]}")
    sys.exit(1)

task_id = resp.json().get("data", {}).get("taskId")
print(f"Task ID: {task_id}")
print("Generating", end="", flush=True)

img_url = None
for _ in range(120):
    time.sleep(5)
    print(".", end="", flush=True)
    poll = requests.get("https://api.kie.ai/api/v1/jobs/recordInfo", headers=headers, params={"taskId": task_id}, timeout=30)
    if poll.status_code != 200:
        continue
    d = poll.json().get("data", {})
    if d.get("state") == "fail":
        print(f"\nFailed: {d.get('failMsg')}")
        sys.exit(1)
    if d.get("state") == "success":
        print("\nDone!")
        result = json.loads(d.get("resultJson", "{}"))
        urls = result.get("resultUrls", result.get("imageUrls", {}))
        img_url = next(iter(urls.values()), None) if isinstance(urls, dict) else (urls[0] if urls else None)
        break

if not img_url:
    print("ERROR: No image URL")
    sys.exit(1)

print("Downloading ...")
raw = Image.open(BytesIO(requests.get(img_url, timeout=120).content)).convert("RGB")
print(f"Raw size: {raw.width} x {raw.height}")

scale = max(TARGET_W / raw.width, TARGET_H / raw.height)
nw, nh = round(raw.width * scale), round(raw.height * scale)
resized = raw.resize((nw, nh), Image.LANCZOS)
left, top = (nw - TARGET_W) // 2, (nh - TARGET_H) // 2
final = resized.crop((left, top, left + TARGET_W, top + TARGET_H))

out = Path("/Users/cwl/Desktop/Claude Missions/Dr Liew Social Media/Automation Scripts/generated_images") / "test_instagram_moment_clicked.png"
out.parent.mkdir(exist_ok=True)
final.save(str(out), "PNG", optimize=True)
print(f"\nSaved to: generated_images/test_instagram_moment_clicked.png")
print(f"Size: {final.width} x {final.height}")
PYEOF

read -p "Press Enter to close..."
