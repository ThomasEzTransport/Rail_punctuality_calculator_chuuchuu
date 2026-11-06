"""Stack the monthly Swiss summaries (summary_stats/swiss_summary_YYYY_MM.xlsx) into one Excel file.

Each sheet (Summary, Summary_partial_alt, Summary_all_stops) is appended across months separately, so the
output keeps the same sheets and columns as the monthly files. Written to
summary_stats/swiss_summary_monthly_merged.xlsx (never re-ingested: only YYYY_MM files are read).

    python merge_swiss_summaries.py
"""

import re
import sys
from pathlib import Path

import pandas as pd

SUMMARY_DIR = Path(__file__).resolve().parent / "summary_stats"
OUTPUT_FILE = SUMMARY_DIR / "swiss_summary_monthly_merged.xlsx"
pattern = re.compile(r"^swiss_summary_(\d{4})_(\d{2})\.xlsx$")

files = sorted(f for f in SUMMARY_DIR.iterdir() if pattern.match(f.name))
if not files:
    sys.exit(f"No swiss_summary_YYYY_MM.xlsx files in {SUMMARY_DIR}")
print(f"{len(files)} monthly files: {', '.join(f.name[14:21] for f in files)}")
if len(files) != 12:
    print("WARNING: not 12 months (run run_swiss_pipeline.py for the missing ones)")

parts, columns = {}, {}
for f in files:
    for sheet, df in pd.read_excel(f, sheet_name=None).items():
        columns.setdefault(sheet, list(df.columns))
        if list(df.columns) != columns[sheet]:
            sys.exit(f"Column mismatch in {f.name} / {sheet}")
        parts.setdefault(sheet, []).append(df)

merged = {sheet: pd.concat(dfs, ignore_index=True)[columns[sheet]] for sheet, dfs in parts.items()}
for sheet, df in merged.items():
    assert len(df) == sum(len(d) for d in parts[sheet]), f"{sheet}: row count mismatch"
    print(f"{sheet:<22}{df.shape}")

with pd.ExcelWriter(OUTPUT_FILE) as writer:
    for sheet, df in merged.items():
        df.to_excel(writer, sheet_name=sheet, index=False)
print(f"Saved to {OUTPUT_FILE}")
