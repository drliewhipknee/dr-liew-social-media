#!/bin/bash
# Test: generate one LinkedIn image with updated prompt via Higgsfield

SCRIPT_DIR="/Users/cwl/Desktop/Claude Missions/Dr Liew Social Media/Automation Scripts"
cd "$SCRIPT_DIR" || exit 1

python3 - << 'PYEOF'
import os, sys, requests
from pathlib import Path

SCRIPT_DIR = "/Users/cwl/Desktop/Claude Missions/Dr Liew Social Media/Automation Scripts"

os.environ["HF_API_KEY"]    = "42ffee2b-b774-4248-98a3-28705136c83b"
os.environ["HF_API_SECRET"] = "97cdfdca71162bbe69da32408b9a366987309a644f227ac80c683e4cf8f42945"

import higgsfield_client

prompt = (
    "Professional medical social media graphic, strict 16:9 widescreen landscape ratio, wider than tall. "
    "Background: Orthopaedic surgeon reviewing 3D hip anatomy on a clinical light table, "
    "figure thoughtful and slightly blurred, warm desk lamp glow, medical journals in soft background, scholarly professional setting. "
    "Semi-transparent deep navy (#16233A) overlay covers the left 55%; right side shows the background naturally. "
    "On the left navy panel, a very subtle, barely-visible soft glow sits gently BEHIND the headline text only — "
    "an extremely faint diffuse luminescence in brand light blue (#A2B9D8), almost imperceptible, "
    "just a whisper of depth and 3D dimensionality behind the text. No orange. No gold. No visible halo. "
    "The glow should be so subtle it enhances the navy without the viewer consciously noticing it. "
    "White left-aligned text on the navy panel: "
    "TOP — small uppercase sans-serif label: 'ORTHOPAEDICS 360'. "
    "CENTRE — large bold headline (2–3 lines): 'Direct Anterior Approach for THA — Clinical Advantages and Patient Selection'. "
    "BELOW HEADLINE — medium-weight subtitle (~20 words): 'The direct anterior approach (DAA) for total hip arthroplasty: clinical rationale and patient selection criteria.'. "
    "BOTTOM — clearly readable medium-weight URL: 'drchienwenliew.com.au'. "
    "Clean modern sans-serif font. Palette: navy #16233A, white, light blue accent #A2B9D8. "
    "No clip art, no borders. Authoritative medical brand aesthetic."
)

print("Submitting to Higgsfield (16:9, 2K)...")
result = higgsfield_client.subscribe(
    "bytedance/seedream/v4/text-to-image",
    arguments={
        "prompt": prompt,
        "resolution": "2K",
        "aspect_ratio": "16:9",
    }
)

# Extract image URL
image_url = None
if isinstance(result, dict):
    images = result.get("images", [])
    if images and isinstance(images[0], dict):
        image_url = images[0].get("url")
    if not image_url:
        image_url = result.get("url")
elif hasattr(result, "url"):
    image_url = result.url
elif isinstance(result, (list, tuple)) and result:
    r = result[0]
    image_url = getattr(r, "url", None) or (r if isinstance(r, str) else None)

if not image_url:
    print("ERROR: No image URL in result:", result)
    sys.exit(1)

print(f"Image URL: {image_url}")

out_path = Path(SCRIPT_DIR) / "generated_images" / "test_linkedin_glow.png"
resp = requests.get(image_url, timeout=60)
resp.raise_for_status()
out_path.write_bytes(resp.content)
print(f"Saved to: {out_path}")
print("Done! Open generated_images/test_linkedin_glow.png to review.")
PYEOF

read -p "Press Enter to close..."
