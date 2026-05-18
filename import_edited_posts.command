#!/bin/bash
# Import edited posts JSON back into posts_schedule.xlsx
# After editing in the HTML editor, export the JSON and drop it in the Automation Scripts folder
# Then double-click this script to merge the changes back into the Excel file.

SCRIPT_DIR="/Users/cwl/Desktop/Claude Missions/Dr Liew Social Media/Automation Scripts"
cd "$SCRIPT_DIR" || exit 1

python3 - << 'PYEOF'
import json, sys
from pathlib import Path
from openpyxl import load_workbook

SCRIPT_DIR = Path("/Users/cwl/Desktop/Claude Missions/Dr Liew Social Media/Automation Scripts")
JSON_PATH = SCRIPT_DIR / "posts_edited.json"
EXCEL_PATH = SCRIPT_DIR / "posts_schedule.xlsx"

if not JSON_PATH.exists():
    print(f"ERROR: posts_edited.json not found in {SCRIPT_DIR}")
    print("Export your edits from the HTML editor and save as 'posts_edited.json' in the Automation Scripts folder.")
    sys.exit(1)

with open(JSON_PATH, encoding='utf-8') as f:
    edited = json.load(f)

# Build a lookup by ID
edits = {int(p['ID']): p for p in edited}
print(f"Loaded {len(edits)} edited posts from JSON")

wb = load_workbook(EXCEL_PATH)
ws = wb['Posts Schedule']

# Find column indices
headers = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1)]
col_map = {h: i+1 for i, h in enumerate(headers) if h}

UPDATABLE = ['Topic', 'Caption', 'Website Link', 'Kie.ai Image Description']

updated = 0
for row_idx in range(2, ws.max_row + 1):
    id_cell = ws.cell(row=row_idx, column=col_map.get('ID', 1))
    try:
        post_id = int(id_cell.value or 0)
    except (ValueError, TypeError):
        continue

    if post_id in edits:
        edit = edits[post_id]
        for field in UPDATABLE:
            col = col_map.get(field)
            if col:
                ws.cell(row=row_idx, column=col).value = edit.get(field, '')
        updated += 1

wb.save(EXCEL_PATH)
print(f"Updated {updated} rows in posts_schedule.xlsx")
print("Done! Your Excel file is up to date.")
PYEOF

read -p "Press Enter to close..."
