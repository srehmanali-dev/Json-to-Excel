#!/usr/bin/env python3
import json
import sys
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple, Set, Iterable
from collections import defaultdict
import pandas as pd
from datetime import datetime

# -------------------------------
# Helpers
# -------------------------------

INVALID_NAME_CHARS = r'[^A-Za-z0-9_.+ -]'

def sanitize_name(name: str, max_len: int = 64) -> str:
    """Sanitize a filename-like sheet name."""
    name = name.strip() or "sheet"
    name = re.sub(INVALID_NAME_CHARS, "_", name)
    if len(name) > max_len:
        name = name[:max_len]
    return name

def uniquify(name: str, used: Set[str]) -> str:
    base = name
    i = 2
    while name in used:
        name = f"{base}_{i}"
        i += 1
    used.add(name)
    return name

def is_array_of_dicts(x: Any) -> bool:
    return isinstance(x, list) and len(x) > 0 and all(isinstance(i, dict) for i in x)

def union_keys(rows: List[Dict[str, Any]], sample: int = 500) -> frozenset:
    """Compute schema as union of keys over up to 'sample' rows (for speed on huge lists)."""
    keys = set()
    for i, r in enumerate(rows):
        keys.update(r.keys())
        if i + 1 >= sample:
            break
    return frozenset(keys)

def rows_to_dataframe(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert list[dict] -> DataFrame with union of all keys. Missing -> NaN (empty in CSV)."""
    if not rows:
        return pd.DataFrame()
    # pandas will union keys automatically across dict records
    return pd.DataFrame(rows)

# -------------------------------
# Core traversal
# -------------------------------

def traverse_and_collect(
    node: Any,
    path: List[str],
    sheets: Dict[str, List[Dict[str, Any]]],
    used_names: Set[str],
):
    """
    Recursively:
      - For each dict node, find *sibling* arrays-of-dicts under its keys.
        Group arrays with identical schemas -> one CSV.
      - Recurse into arrays' elements (dicts) and any nested dicts.
      - For top-level array-of-dicts, create a 'root' CSV.
    """

    # Top-level array-of-dicts (or any array we decided to process directly)
    if is_array_of_dicts(node):
        # Name based on current path; 'root' if empty path
        base_name = path[-1] if path else "root"
        name = uniquify(sanitize_name(base_name), used_names)
        sheets[name].extend(node)
        # Recurse into each dict element to discover nested arrays within the objects
        for item in node:
            traverse_and_collect(item, path, sheets, used_names)
        return

    # dict node: look for arrays-of-dicts under keys at this level
    if isinstance(node, dict):
        # 1) Group arrays-of-dicts by schema (key set)
        schema_groups: Dict[frozenset, List[Tuple[str, List[Dict[str, Any]]]]] = defaultdict(list)
        for k, v in node.items():
            if is_array_of_dicts(v):
                schema = union_keys(v)
                if len(schema) == 0:
                    # All empty dicts (unlikely) -> skip
                    continue
                schema_groups[schema].append((k, v))

        # 2) Emit one sheet per schema group. If multiple arrays share same schema, merge them.
        for schema, items in schema_groups.items():
            # Choose a name: if single key -> that key; else join keys with '+'
            keys_here = [k for (k, _rows) in items]
            if len(keys_here) == 1:
                base_name = keys_here[0]
            else:
                base_name = "+".join(keys_here)
            # Prepend parent hint if no explicit parent name and to reduce collisions
            parent_hint = path[-1] if path else ""
            if parent_hint and not base_name.startswith(parent_hint + "."):
                base_name = f"{parent_hint}.{base_name}"

            sheet_name = uniquify(sanitize_name(base_name), used_names)

            # Merge all rows from arrays in this group
            merged_rows: List[Dict[str, Any]] = []
            for _k, rows in items:
                merged_rows.extend(rows)
            sheets[sheet_name].extend(merged_rows)

            # Recurse into each dict element of these arrays to find deeper arrays
            for _k, rows in items:
                for item in rows:
                    traverse_and_collect(item, path + [sheet_name], sheets, used_names)

        # 3) Recurse into other children (non array-of-dicts)
        for k, v in node.items():
            if is_array_of_dicts(v):
                # already handled (and recursed into) above
                continue
            # If child is dict or list, keep going
            if isinstance(v, (dict, list)):
                traverse_and_collect(v, path + [k], sheets, used_names)
        return

    # list but NOT array-of-dicts: recurse into its items to discover nested arrays-of-dicts
    if isinstance(node, list):
        for item in node:
            # path does not change because list has no key name;
            # nested arrays-of-dicts under dict keys will be picked up there.
            traverse_and_collect(item, path, sheets, used_names)
        return

    # scalars: nothing to do
    return

# -------------------------------
# Main entry
# -------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python json_to_table.py <path_to_json>")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"❌ File not found: {json_path}")
        sys.exit(1)

    try:
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)

    # Output folder next to the input JSON
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = json_path.parent / f"{json_path.stem}_tables_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Collect sheets (name -> list of row dicts)
    sheets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    used_names: Set[str] = set()

    # Special-case: if top-level is array-of-dicts, we still want a CSV for it
    if is_array_of_dicts(data):
        traverse_and_collect(data, [], sheets, used_names)
    else:
        traverse_and_collect(data, [], sheets, used_names)

    # Write CSVs
    if not sheets:
        print("⚠️ No arrays of objects found. No CSVs created.")
        sys.exit(0)

    created = 0
    for sheet_name, rows in sheets.items():
        if not rows:
            # Don't create empty CSVs
            continue
        df = rows_to_dataframe(rows)
        csv_path = out_dir / f"{sheet_name}.csv"
        # Always UTF-8 CSV
        df.to_csv(csv_path, index=False, encoding="utf-8")
        created += 1

    if created == 0:
        print("⚠️ Arrays found but they were empty. No CSVs created.")
    else:
        print(f"✅ Created {created} CSV file(s) in:\n{out_dir}")

if __name__ == "__main__":
    main()
