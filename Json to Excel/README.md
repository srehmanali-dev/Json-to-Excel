# json_to_table.py

Flatten **JSON arrays of objects** into **CSV files**—simple, predictable, and fast.

## What it does
- Recursively searches your JSON for every **array of objects** (e.g., `[{...}, {...}]`).
- Writes **one CSV per discovered array** into a timestamped folder next to your input file.
- If multiple arrays under the **same parent object** share the **same schema** (same set of keys), they are **merged into one CSV**.
- **Skips empty arrays** and arrays that aren’t arrays of objects (arrays of scalars are ignored).
- Each object’s **keys become CSV headers**; values become rows. Missing keys → blank cells.

> This script **only** outputs CSV. It does not create Excel files.

## Requirements
- Python 3.8+
- `pandas`

Install once:
```bash
python -m pip install --user pandas
```

## Quick start
```bash
python json_to_table.py path/to/your.json
```
Output folder: `path/to/your_tables_YYYYMMDD_HHMMSS/` with one or more `*.csv` files.

### Windows PowerShell one-liner
```powershell
py -m pip install --user pandas; py .\json_to_table.py ".\your.json"
```

## How it decides what becomes a CSV
- **Exports:** Any array that is a list of dictionaries (list[dict]) → one CSV.
- **Merges:** Arrays under the **same parent** with the **same schema** are merged into a single CSV (to avoid redundant files).
- **Skips:** Empty arrays; arrays of scalars; standalone dicts (unless they appear inside an exported array).

## Naming rules
- File names are based on the **array’s key** (e.g., `employees.csv`).
- If multiple arrays are merged, the name becomes a **`key1+key2`** style.
- A parent hint is added where helpful to avoid collisions.
- Names are sanitized and de-duplicated: `name`, `name_2`, `name_3`, …

## Examples

### 1) Top-level array of objects
```json
[{ "id": 1, "name": "A" }, { "id": 2, "name": "B" }]
```
Produces a folder with:
```
root.csv
```
with headers `id,name` and two rows.

### 2) Object with multiple arrays (same schema) → merged
```json
{
  "morning": [{ "id": 1, "item": "Tea" }],
  "evening": [{ "id": 2, "item": "Tea" }]
}
```
Both arrays share keys `{id,item}` → one CSV, e.g.:
```
<parent>.morning+evening.csv
```

### 3) Nested arrays
```json
{
  "dept": {
    "teams": [
      {
        "name": "Alpha",
        "members": [{ "user": "u1" }, { "user": "u2" }]
      }
    ]
  }
}
```
Exports **teams** (if object arrays) and **members** (nested array of objects) as separate CSVs.

## Limitations (by design, to keep it simple)
- Only arrays-of-dicts are exported. Single objects are not exported as standalone CSVs.
- Very large arrays load into memory at once (no chunked/streaming write).
- Input must be valid UTF‑8 JSON.
- Schema matching for merging uses the **set of keys** (sampled up to 500 rows for speed).

## Troubleshooting
- **"Invalid JSON"** → Fix trailing commas/ellipses and ensure UTF‑8 encoding.
- **"No arrays of objects found"** → Your JSON likely has no `[{...}]` structures.
- **ModuleNotFoundError: pandas** → Run `python -m pip install --user pandas`.

---

## License
MIT (do what you want; attribution appreciated).
