import pandas as pd
import json
import re
import time
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ---------------------- CONFIGURATION ----------------------
INPUT_FILE = r"C:\Users\SyedRehmanAli\Downloads\response.json"
# -----------------------------------------------------------

def sanitize_name(name):
    return re.sub(r'[^A-Za-z0-9_.-]', '_', str(name))

def uniquify(name, used_names):
    base = name
    i = 1
    while name in used_names:
        name = f"{base}_{i}"
        i += 1
    used_names.add(name)
    return name

def is_array_of_dicts(value):
    return isinstance(value, list) and all(isinstance(v, dict) for v in value)

def union_keys(list_of_dicts):
    keys = set()
    for d in list_of_dicts[:500]:
        keys.update(d.keys())
    return keys

def traverse_and_collect(node, path, sheets, used_names, stats):
    """
    Recursively traverse JSON and collect EVERY array-of-dicts as its own sheet.
    IMPORTANT CHANGE: do NOT return after collecting; continue recursing to find nested arrays.
    """
    if is_array_of_dicts(node):
        # give the root a real name so the CSV isn't blank
        sheet_name = sanitize_name(path or "root")
        sheet_name = uniquify(sheet_name, used_names)
        sheets[sheet_name].extend(node)
        stats['arrays_found'] += 1
        # <-- removed the early 'return' so we still descend into children

    if isinstance(node, dict):
        for k, v in node.items():
            new_path = f"{path}.{k}" if path else k
            traverse_and_collect(v, new_path, sheets, used_names, stats)

    elif isinstance(node, list):
        for i, item in enumerate(node):
            # keep a precise path so child sheets get sensible names, e.g. "Data.Result"
            new_path = f"{path}[{i}]" if path else f"[{i}]"
            traverse_and_collect(item, new_path, sheets, used_names, stats)

def rows_to_dataframe(rows):
    """Convert list of dicts to DataFrame, flattening nested dicts (deep)."""
    df = pd.DataFrame(rows)
    if not df.empty:
        changed = True
        # keep expanding dict columns until none left
        while changed:
            changed = False
            for col in list(df.columns):
                if df[col].apply(lambda x: isinstance(x, dict)).any():
                    expanded = pd.json_normalize(df[col])
                    expanded.columns = [f"{col}.{sub}" for sub in expanded.columns]
                    df = pd.concat([df.drop(columns=[col]), expanded], axis=1)
                    changed = True
    return df

def main():
    start_time = datetime.now()
    print("🚀 Starting JSON → CSV conversion")
    print(f"📂 Input file: {INPUT_FILE}")
    print(f"🕒 Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    input_path = Path(INPUT_FILE)
    if not input_path.exists():
        print(f"❌ Error: File not found → {input_path}")
        return

    # Load JSON
    with open(input_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            print("✅ JSON file loaded successfully.\n")
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            return

    # Initialize
    sheets = defaultdict(list)
    used_names = set()
    stats = {'arrays_found': 0}

    # Traverse JSON (now also captures nested arrays like Data.Result)
    traverse_and_collect(data, "", sheets, used_names, stats)

    # Prepare output
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_prefix = f"{input_path.stem}_{timestamp}"
    output_dir = input_path.parent

    if not sheets:
        print("⚠️ No arrays of objects found in the JSON file.")
        return

    # Write CSVs
    total_rows = 0
    for sheet_name, rows in sheets.items():
        df = rows_to_dataframe(rows)
        csv_path = output_dir / f"{output_prefix}_{sanitize_name(sheet_name)}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"📄 Saved: {csv_path.name} ({len(df)} rows, {df.shape[1]} columns)")
        total_rows += len(df)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n📊 --- SUMMARY ---")
    print(f"📁 Total sheets created: {len(sheets)}")
    print(f"📦 Total arrays found: {stats['arrays_found']}")
    print(f"🧾 Total rows processed: {total_rows}")
    print(f"💾 Files saved in: {output_dir}")
    print(f"🕒 Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🕒 End:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️ Duration: {duration:.2f} seconds")
    print("\n✅ Conversion completed successfully.")

if __name__ == "__main__":
    main()
