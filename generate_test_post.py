#!/usr/bin/env python3
"""
generate_test_post.py
Generates a single refined test post image via Kie.ai GPT Image 2.
Saves to generated_images/test-post.jpg

Usage:
    python3 generate_test_post.py
"""

import json, time
from pathlib import Path
import requests

KIE_API_KEY   = "961df6a53af50676575fee66b918b68c"
KIE_BASE      = "https://api.kie.ai/api/v1"
MODEL         = "gpt-image-2-text-to-image"
POLL_INTERVAL = 6
MAX_WAIT      = 240

SCRIPT_DIR = Path(__file__).parent
OUT_DIR    = SCRIPT_DIR / "generated_images"
OUT_DIR.mkdir(exist_ok=True)
OUT_PATH   = OUT_DIR / "test-post.jpg"

HEADERS = {
    "Authorization": f"Bearer {KIE_API_KEY}",
    "Content-Type":  "application/json",
}

# ── The prompt ─────────────────────────────────────────────────────────────────
# World-class luxury social media post design.
# Glow is BEHIND the floating panel, spreading outward from panel edges.
# Logo: small (DR) + large bold LIEW.
# Full title — no truncation.

PROMPT = """
Luxury social media post, 1:1 square format, created by a world-class creative agency
for a premium private orthopaedic surgical practice in Adelaide, Australia.

PHOTOGRAPHY — upper 58% of image:
Moody cinematic scene. A patient is seated on a warm timber bench in a sunlit private
garden. An anonymous healthcare figure — face entirely not visible, cropped at collarbone,
wearing soft sage-toned clothing — gently supports the patient's knee with both hands.
Rich warm amber light streams through bokeh foliage behind them. Depth of field is very
shallow — background dissolves into soft glowing greens and golds. No clinical elements,
no white coats, no hospital setting. Editorial production quality — feels like a campaign
image from a luxury private hospital. Cinematic, warm, intimate, reassuring.

FLOATING PANEL — lower 42% of image:
Deep navy panel, hex #16233A, with gently rounded top-left and top-right corners. The
panel does NOT touch the left, right, or bottom edges of the image — it floats inset with
a small margin on all sides, creating breathing room. A soft diffused radiant glow of deep
indigo-blue light emanates from BEHIND the panel and spreads outward beyond all four panel
edges into the surrounding area — like the panel is gently backlit, hovering above the
photograph. This glow creates beautiful depth and a sense of luxury. Subtle, not neon —
refined and elegant.

TYPOGRAPHY inside panel — Neue Montreal typeface, all text left-aligned, generous
left padding:
LINE 1 — small uppercase, wide letter-spacing, colour #A2B9D8 (soft blue): ORTHOPAEDICS 360
LINE 2 — large bold white, wraps naturally across 3 to 4 lines — render every single word,
no cutting off: The Role of Physiotherapy in Long-Term Joint Replacement Success
LINE 3 — small regular white: Dr Chien-Wen Liew | Orthopaedics 360, Adelaide

BOTTOM ROW of panel, flush to panel bottom with padding:
LEFT SIDE — brand wordmark: the letters (DR) in small light-weight white, immediately
followed by LIEW in significantly larger extra-bold white — the size contrast is
intentional and prominent, matching a luxury wordmark style.
RIGHT SIDE — drchienwenliew.com.au in bold white, medium-large size, clearly legible,
more prominent than body text.

Overall design intention: this image should look like it was designed by a senior art
director for a premium private surgical practice. Sophisticated, warm, beautiful, trustworthy.
The photography draws you in. The panel grounds the content. The glow connects them.
""".strip()


# ── API helpers ────────────────────────────────────────────────────────────────
def create_task():
    try:
        resp = requests.post(
            f"{KIE_BASE}/jobs/createTask",
            headers=HEADERS,
            json={
                "model": MODEL,
                "callBackUrl": "",
                "input": {"prompt": PROMPT, "aspect_ratio": "1:1"},
            },
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()
        data = body.get("data") or body
        return (
            data.get("taskId") or data.get("task_id")
            or data.get("id") or body.get("taskId")
        )
    except Exception as e:
        print(f"  ❌  createTask failed: {e}")
        return None


def poll_task(task_id):
    deadline = time.time() + MAX_WAIT
    while time.time() < deadline:
        time.sleep(POLL_INTERVAL)
        try:
            resp = requests.get(
                f"{KIE_BASE}/jobs/recordInfo",
                headers=HEADERS,
                params={"taskId": task_id},
                timeout=30,
            )
            resp.raise_for_status()
            body = resp.json()
            data = body.get("data") or body
            state = (
                data.get("state") or data.get("status")
                or data.get("taskStatus") or ""
            ).upper()
            print(f"    {state}")
            if state in ("SUCCESS", "COMPLETED", "DONE", "FINISH"):
                result_raw = data.get("resultJson") or "{}"
                result = json.loads(result_raw) if isinstance(result_raw, str) else result_raw
                urls = (
                    result.get("resultUrls") or result.get("images")
                    or data.get("resultUrls") or data.get("images") or []
                )
                if isinstance(urls, list) and urls:
                    u = urls[0]
                    return u.get("url") if isinstance(u, dict) else u
                return data.get("url") or result.get("url")
            elif state in ("FAILED", "ERROR", "CANCELLED"):
                print(f"  ❌  Task {state}")
                return None
        except Exception as e:
            print(f"  ⚠️  Poll error: {e}")
    print("  ❌  Timed out")
    return None


def download(url):
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        OUT_PATH.write_bytes(resp.content)
        print(f"  ✅  Saved → {OUT_PATH.name}  ({len(resp.content)//1024} KB)")
        return True
    except Exception as e:
        print(f"  ❌  Download failed: {e}")
        return False


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print()
    print("═" * 55)
    print("  Dr Liew — Test Post Generator")
    print("  Topic: The Role of Physiotherapy in")
    print("         Long-Term Joint Replacement Success")
    print("═" * 55)
    print()
    print("  Design features:")
    print("  • Cinematic warm outdoor lifestyle photography")
    print("  • Floating navy panel with glow BEHIND it")
    print("  • Neue Montreal typeface")
    print("  • Small (DR) + large LIEW logo")
    print("  • Full title — no truncation")
    print("  • Prominent website URL")
    print()
    print("  Submitting to Kie.ai...")
    task_id = create_task()
    if not task_id:
        print("  ❌  Could not create task. Check API key / connection.")
        return

    print(f"  Task ID: {task_id}")
    print("  Polling for result...")
    url = poll_task(task_id)
    if not url:
        print("  ❌  Did not receive image URL.")
        return

    download(url)
    print()
    print("═" * 55)
    print(f"  Image saved to:")
    print(f"  {OUT_PATH}")
    print("═" * 55)
    print()


if __name__ == "__main__":
    main()
