# json-to-table

**json_to_csv.py** — Flatten **large JSON arrays of objects** into clean **CSV files** — reliable, transparent, and completely free to use.

Developed after struggling with inconsistent tools, this script was built to help **anyone** convert complex JSON into usable CSVs **without hassle**.  
Please feel free to use and share it — just don’t misuse it.  
💼 Connect or credit me if it helps you: [**Syed Rehman Ali**](https://www.linkedin.com/in/srehmanali/)

---

## 🚀 What it does

- Recursively scans your JSON for every **array of objects** (`[{...}, {...}]`).
- Writes a **single CSV output file** in the **same folder** as the input file, with a **timestamped filename**.
- Prints a **detailed summary** on the console:
  - Start time, end time, and total duration.
  - Total number of rows processed.
  - File paths and summary statistics.
- Handles **very large JSON files** without crashing.
- Each object’s **keys become CSV headers**; missing fields are filled with blanks.

> This script **only outputs CSV** — it does not create Excel or database files.

---

## 🧩 Requirements

- Python 3.8+
- `pandas`

Install once:

```bash
python -m pip install --user pandas
```

---

## ⚙️ How to Use

### 1) Define your input file

Inside the script, set your JSON file path in the `input_file` variable:

```python
input_file = r"C:\path\to\your_file.json"
```

You don’t need to provide a command-line argument — just edit the path in the code once.

### 2) Run the script

```bash
python json_to_csv.py
```

### 3) Output

The script creates a CSV file in the **same folder** as your input JSON.

The output filename includes a timestamp, e.g.:

```
your_file_20251030_115500.csv
```

You’ll see progress details and a summary in the console.

---

## 🧾 Example Console Output

```text
========================================
JSON to CSV Conversion Started
----------------------------------------
Input File: C:\data\sample.json
Output File: C:\data\sample_20251030_115500.csv
Start Time: 2025-10-30 11:55:00
----------------------------------------
Processing large JSON file...
✅ Total records processed: 487,321
✅ Unique columns found: 24
----------------------------------------
End Time: 2025-10-30 11:56:12
Duration: 0:01:12
========================================
Conversion completed successfully!
```

---

## 💡 Notes

- Works with nested JSON structures — automatically flattens nested fields into columns.  
- Automatically detects all arrays of objects inside your JSON.  
- Writes all data into a single flattened CSV.  
- Supports UTF-8 encoded JSON files.

---

## ⚠️ Limitations (by design)

- Only handles arrays of dictionaries (`list[dict]`).  
- Large files are fully loaded into memory (no streaming mode yet).  
- Does not support JSON with trailing commas or invalid syntax.

---

## 🧰 Troubleshooting

| Problem                         | Solution                                                     |
|---------------------------------|--------------------------------------------------------------|
| `ValueError: Trailing data`     | Ensure your JSON is valid UTF-8 and properly formatted.      |
| `ModuleNotFoundError: pandas`   | Run `python -m pip install --user pandas`.                   |
| No arrays found                 | Ensure your file contains at least one array of objects.     |

---

## ❤️ Open for Everyone

This tool is completely free — I created it after struggling to find a simple, reliable JSON converter.  
If it helps you, please give credit or connect on LinkedIn: 👉 **Syed Rehman Ali**

Let’s make data processing simple and accessible for everyone.

---

## 🪪 License

**MIT License** — use, modify, and distribute freely. Attribution appreciated.
