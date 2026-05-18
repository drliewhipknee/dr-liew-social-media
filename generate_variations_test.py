#!/usr/bin/env python3
"""
generate_variations_test.py
Generates 5 design variations for the physiotherapy post to compare.
Saves to generated_images/variation-1.jpg through variation-5.jpg
"""

import json, time, sys
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

HEADERS = {
    "Authorization": f"Bearer {KIE_API_KEY}",
    "Content-Type":  "application/json",
}

# ── Shared panel description ───────────────────────────────────────────────────
PANEL = (
    "PANEL DESIGN (lower 40% of image): rounded-top solid deep navy #16233A panel. "
    "Soft diffused luminous white-gold halo glow radiating from behind the curved top edge of the panel upward into the photo above — subtle luxury effect. "
    "All text inside panel, left-aligned with generous left margin, Neue Montreal typeface: "
    "LINE 1 — small uppercase wide-tracked 'ORTHOPAEDICS 360' in light blue #A2B9D8; "
    "LINE 2 — large bold white: 'The Role of Physiotherapy in Long-Term Joint Replacement Success' — render ALL words, wrap across multiple lines, do NOT truncate; "
    "LINE 3 — small regular white: 'Dr Chien-Wen Liew | Orthopaedics 360, Adelaide'. "
    "BOTTOM ROW of panel: left side — small light-weight '(DR)' immediately followed by extra-large bold 'LIEW' in white (logo: DR is noticeably smaller, LIEW dominates); "
    "right side — 'drchienwenliew.com.au' in large bold prominent white, clearly legible."
)

VARIATIONS = [
    {
        "name": "variation-1",
        "label": "Deep Navy Abstract",
        "background": (
            "BACKGROUND (top 60%): rich deep navy-to-midnight-blue gradient, "
            "subtle soft bokeh light circles dissolving into darkness, luxurious and sophisticated, "
            "purely abstract, no people, no clinical elements."
        ),
    },
    {
        "name": "variation-2",
        "label": "Warm Lifestyle Outdoor",
        "background": (
            "BACKGROUND (top 60%): sun-drenched outdoor garden or terrace, golden afternoon light, "
            "lush blurred greenery bokeh, cinematic depth of field. "
            "Anonymous figure — face completely not visible, cropped at shoulders from behind — "
            "in neutral sage clothing doing a gentle knee bend, warm wellness lifestyle atmosphere, no clinical elements."
        ),
    },
    {
        "name": "variation-3",
        "label": "Luxury Architecture",
        "background": (
            "BACKGROUND (top 60%): elegant private hospital or medical centre atrium, "
            "soaring glass and timber architecture, warm ambient light reflecting off polished floors, "
            "no people, premium private healthcare aesthetic, calm and aspirational."
        ),
    },
    {
        "name": "variation-4",
        "label": "Rich Amber Bokeh",
        "background": (
            "BACKGROUND (top 60%): deep rich amber and burnt gold abstract bokeh — "
            "warm glowing light circles dissolving out of focus against a dark background, "
            "luxurious and warm tonal depth, purely atmospheric, no people, no location."
        ),
    },
    {
        "name": "variation-5",
        "label": "Wellness Studio",
        "background": (
            "BACKGROUND (top 60%): bright contemporary rehabilitation or wellness studio, "
            "large floor-to-ceiling windows with soft morning light, clean timber floors, "
            "exercise equipment softly out of focus in the background, no people, "
            "feels active, restorative, and premium."
        ),
    },
]


def create_task(prompt):
    try:
        resp = requests.post(
            f"{KIE_BASE}/jobs/createTask",
            headers=HEADERS,
            json={
                "model": MODEL,
                "callBackUrl": "",
                "input": {"prompt": prompt, "aspect_ratio": "1:1"},
            },
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()
        data = body.get("data") or body
        return data.get("taskId") or data.get("task_id") or data.get("id") or body.get("taskId")
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
                data.get("state") or data.get("status") or data.get("taskStatus") or ""
            ).upper()
            print(f"    status: {state}")
            if state in ("SUCCESS", "COMPLETED", "DONE", "FINISH"):
                result_json_str = data.get("resultJson") or "{}"
                result_json = json.loads(result_json_str) if isinstance(result_json_str, str) else result_json_str
                urls = (
                    result_json.get("resultUrls") or result_json.get("images")
                    or data.get("resultUrls") or data.get("images") or []
                )
                if isinstance(urls, list) and urls:
                    url = urls[0]
                    return url.get("url") if isinstance(url, dict) else url
                return data.get("url") or result_json.get("url")
            elif state in ("FAILED", "ERROR", "CANCELLED"):
                print(f"  ❌  Task failed: {state}")
                return None
        except Exception as e:
            print(f"  ⚠️  Poll error: {e}")
    print(f"  ❌  Timed out after {MAX_WAIT}s")
    return None


def download(url, out_path):
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        out_path.write_bytes(resp.content)
        print(f"  ✅  Saved → {out_path.name}  ({len(resp.content)//1024} KB)")
        return True
    except Exception as e:
        print(f"  ❌  Download failed: {e}")
        return False


def main():
    print()
    print("═" * 55)
    print("  Generating 5 design variations via Kie.ai")
    print("═" * 55)

    results = []

    for i, v in enumerate(VARIATIONS, 1):
        out_path = OUT_DIR / f"{v['name']}.jpg"

        if out_path.exists():
            print(f"\n[{i}/5] {v['label']} — already exists, skipping")
            print(f"       (delete {v['name']}.jpg to regenerate)")
            results.append((v['label'], out_path, True))
            continue

        print(f"\n[{i}/5] {v['label']}")
        prompt = f"Square 1:1 social media image. {v['background']} {PANEL}"
        print(f"  → Submitting task...")

        task_id = create_task(prompt)
        if not task_id:
            results.append((v['label'], None, False))
            continue

        print(f"  → Task ID: {task_id}. Polling...")
        url = poll_task(task_id)
        if not url:
            results.append((v['label'], None, False))
            continue

        ok = download(url, out_path)
        results.append((v['label'], out_path if ok else None, ok))

    print()
    print("═" * 55)
    print("  RESULTS")
    print("═" * 55)
    for label, path, ok in results:
        status = "✅" if ok else "❌"
        fname  = path.name if path else "FAILED"
        print(f"  {status}  {label:30s}  →  {fname}")

    print()
    print("  Images saved to:")
    print(f"  {OUT_DIR}")
    print()
    print("  Next: review, then run 'Push Images to GitHub.command'")
    print("═" * 55)
    print()


if __name__ == "__main__":
    main()
