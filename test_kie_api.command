#!/bin/bash
# Quick Kie.ai API diagnostic — tests 1:1 and 16:9 prompts
cd "$(dirname "$0")"
python3 - <<'EOF'
import requests, json, time, os
from pathlib import Path

# Load key from .env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if line.strip() and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

API_KEY = os.environ.get("KIE_API_KEY", "")
if not API_KEY:
    print("ERROR: KIE_API_KEY not set in .env file")
    exit(1)
BASE    = "https://api.kie.ai/api/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def test_prompt(label, aspect):
    print(f"\n=== Testing {label} ({aspect}) ===")
    payload = {
        "model": "gpt-image-2-text-to-image",
        "callBackUrl": "",
        "input": {
            "prompt": "A clean white desk with a single pen. Minimalist.",
            "aspect_ratio": aspect,
        }
    }
    r = requests.post(f"{BASE}/jobs/createTask", headers=HEADERS, json=payload, timeout=30)
    body = r.json()
    task_id = (body.get("data") or body).get("taskId")
    print(f"  Task created: {task_id}")
    if not task_id:
        print(f"  Failed to create: {body}")
        return

    for i in range(8):
        time.sleep(6)
        r2 = requests.get(f"{BASE}/jobs/recordInfo", headers=HEADERS, params={"taskId": task_id}, timeout=30)
        result = r2.json()
        data = result.get("data") or result
        state = (data.get("state") or data.get("status") or "?").upper()
        print(f"  [{i+1}] {state}")
        if state in ("SUCCESS","COMPLETED","DONE","FINISH","FAILED","FAIL","ERROR"):
            print(f"  failMsg: {data.get('failMsg','')}")
            break

test_prompt("1:1 square", "1:1")
test_prompt("16:9 wide", "16:9")
EOF
echo ""
echo "Done. Press any key to close."
read -n 1
