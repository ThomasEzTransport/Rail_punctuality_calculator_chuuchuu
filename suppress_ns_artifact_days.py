"""Remove the NS rows of the service days affected by the NS "all trains cancelled" feed artifact.

On 2025-02-06, 2025-02-20, 2025-04-03 and 2025-04-08 the NS feed flags ~99% of the stops as cancelled
(identical hour-by-hour pattern, snapshot timestamps running until ~08:00 the next morning). These
~200k cancelled stops are a data-collection artifact, not real cancellations, and distort the NS
cancellation rate and punctuality (cancelled stops count as delayed for NS). See data_corrections.md.

The script drops the rows (agency == "NS" and date in NS_ARTIFACT_DATES) from every active parquet file
that holds them: raw delay records and enriched files, monthly and yearly, on the shared drive and in
the local intermediate_outputs folder, and from the two raw full-year CSV exports (--only-csv / --skip-csv
to choose, --expect-csv-removed N as a safety check on the number of lines removed). It is idempotent (files without matching rows are left alone),
so it can be re-run after regenerating or re-exporting data. The "old runs" archive is not touched.

    python suppress_ns_artifact_days.py --dry-run          # count the rows per file, change nothing
    python suppress_ns_artifact_days.py --backup-dir DIR   # rewrite the files, saving the removed rows in DIR
"""

import argparse
import gzip
import os
import re
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).parent))  # chuuchuu_paths.py sits next to this script
from chuuchuu_paths import CHUUCHUU_DIR, ENRICHED_DIR  # noqa: E402

NS_ARTIFACT_DATES = ["2025-02-06", "2025-02-20", "2025-04-03", "2025-04-08"]
LOCAL_DIR = Path(__file__).parent / "intermediate_outputs"

TARGETS = [
    # raw delay records (monthly, yearly, NS only)
    CHUUCHUU_DIR / "delay_records_2025_02.parquet",
    CHUUCHUU_DIR / "delay_records_2025_04.parquet",
    CHUUCHUU_DIR / "delay_records_full_2025_april.parquet",
    CHUUCHUU_DIR / "delay_records_full_2025_NS.parquet",
    CHUUCHUU_DIR / "delay_records_full_2025.parquet",
    # enriched files, shared drive
    ENRICHED_DIR / "data_chuuchuu_2025_02_enriched.parquet",
    ENRICHED_DIR / "data_chuuchuu_2025_04_enriched.parquet",
    ENRICHED_DIR / "data_chuuchuu_2025_01_to_2025_12_enriched.parquet",
    # enriched files, local copies
    LOCAL_DIR / "data_chuuchuu_2025_02_enriched.parquet",
    LOCAL_DIR / "data_chuuchuu_2025_04_enriched.parquet",
    LOCAL_DIR / "data_chuuchuu_2025_01_to_2025_12_enriched.parquet",
]


def artifact_mask(table):
    """Boolean mask of the rows to remove."""
    return pc.and_(
        pc.equal(table["agency"], "NS"),
        pc.is_in(table["date"], value_set=pa.array(NS_ARTIFACT_DATES, type=table["date"].type)),
    )


def count_rows(path):
    pf = pq.ParquetFile(path)
    hits = 0
    for i in range(pf.num_row_groups):
        mask = artifact_mask(pf.read_row_group(i, columns=["agency", "date"]))
        hits += pc.sum(pc.cast(mask, pa.int64())).as_py() or 0
    return hits, pf.metadata.num_rows


def agency_counts(path):
    pf = pq.ParquetFile(path)
    counts = {}
    for i in range(pf.num_row_groups):
        vc = pc.value_counts(pf.read_row_group(i, columns=["agency"])["agency"])
        for item in vc:
            counts[item["values"].as_py()] = counts.get(item["values"].as_py(), 0) + item["counts"].as_py()
    return counts


def rewrite(path, backup_dir):
    """Rewrite `path` without the artifact rows (via a temp file, replaced only once verified)."""
    pf = pq.ParquetFile(path)
    schema = pf.schema_arrow
    compression = pf.metadata.row_group(0).column(0).compression
    before = agency_counts(path)
    tmp = path.with_name(path.name + ".tmp")
    removed_path = Path(backup_dir) / ("removed_" + path.parent.name + "__" + path.name)
    with pq.ParquetWriter(tmp, schema, compression=compression) as keep_writer, \
            pq.ParquetWriter(removed_path, schema, compression="zstd") as removed_writer:
        for i in range(pf.num_row_groups):
            table = pf.read_row_group(i)
            mask = artifact_mask(table)
            removed = table.filter(mask)
            if removed.num_rows:
                removed_writer.write_table(removed)
            kept = table.filter(pc.invert(mask))
            if kept.num_rows:
                keep_writer.write_table(kept)
    # verification before replacing the original
    hits_after, rows_after = count_rows(tmp)
    after = agency_counts(tmp)
    removed_rows = pq.ParquetFile(removed_path).metadata.num_rows
    expected = dict(before)
    expected["NS"] = expected.get("NS", 0) - removed_rows
    assert hits_after == 0, f"{path.name}: artifact rows still present"
    assert rows_after == pf.metadata.num_rows - removed_rows, f"{path.name}: row count mismatch"
    assert after == expected, f"{path.name}: other agencies changed {before} -> {after}"
    assert pq.ParquetFile(tmp).schema_arrow.equals(schema, check_metadata=True), f"{path.name}: schema changed"
    os.replace(tmp, path)
    return removed_rows, pf.metadata.num_rows, rows_after


# raw CSV exports of the full year (the other CSVs are single-agency, FR / SBB, or 2026 test data)
CSV_TARGETS = [
    CHUUCHUU_DIR / "delay_records_full_2025.csv",
    CHUUCHUU_DIR / "delay_records_2025.csv.gz",
]
# the records are one per line, "agency,routeType,routeNumber,date,..." : match the NS lines of the four dates
CSV_ARTIFACT_RE = re.compile(rb"^NS,[^,]*,[^,]*,(?:" + b"|".join(d.encode() for d in NS_ARTIFACT_DATES) + rb"),")


def process_csv(path, backup_dir=None, expected_removed=None):
    """Stream a raw CSV (or .csv.gz) and drop the artifact lines, every other byte is copied unchanged.

    Without backup_dir only counts the lines. Otherwise the kept lines go to a temp file which replaces the
    original once checked; the removed lines (with the header) are saved in backup_dir. If expected_removed
    is given, the number of removed lines must match it or the original is left untouched.
    """
    gz = path.suffix == ".gz"
    open_in = gzip.open if gz else open
    tmp = path.with_name(path.name + ".tmp")
    write = backup_dir is not None
    kept = removed = odd = 0
    out = rem = None
    try:
        if write:
            out = gzip.open(tmp, "wb", compresslevel=6) if gz else open(tmp, "wb")
            rem = gzip.open(Path(backup_dir) / ("removed_" + path.name.replace(".gz", "") + ".gz"), "wb")
        with open_in(path, "rb") as fin:
            for n, line in enumerate(fin):
                if n == 0:
                    if write:
                        out.write(line)
                        rem.write(line)
                    kept += 1
                    continue
                if line.startswith(b"NS,") and CSV_ARTIFACT_RE.match(line):
                    removed += 1
                    if write:
                        rem.write(line)
                    continue
                if not line[:1].isalpha():
                    odd += 1  # a line that does not start a record (embedded newline / blank line): report only
                kept += 1
                if write:
                    out.write(line)
    finally:
        for fh in (out, rem):
            if fh is not None:
                fh.close()
    if not write:
        return removed, kept + removed, odd
    if expected_removed is not None and removed != expected_removed:
        tmp.unlink()
        raise AssertionError(f"{path.name}: removed {removed} lines, expected {expected_removed}; original untouched")
    # verification pass on the temp file (gzip integrity, line count, no artifact line left)
    check_kept = check_hits = 0
    with open_in(tmp, "rb") as fin:
        for line in fin:
            check_kept += 1
            check_hits += bool(line.startswith(b"NS,") and CSV_ARTIFACT_RE.match(line))
    assert check_hits == 0 and check_kept == kept, f"{path.name}: verification failed ({check_hits} hits, {check_kept} vs {kept} lines)"
    os.replace(tmp, path)
    return removed, kept + removed, odd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--backup-dir", default=None, help="folder where the removed rows are saved (one parquet per file)")
    parser.add_argument("--skip-csv", action="store_true", help="only process the parquet files")
    parser.add_argument("--only-csv", action="store_true", help="only process the raw CSV files")
    parser.add_argument("--expect-csv-removed", type=int, default=None,
                        help="number of artifact lines each raw CSV must contain (safety check before replacing it)")
    args = parser.parse_args()
    if not args.dry_run and not args.backup_dir:
        sys.exit("--backup-dir is required unless --dry-run")
    if args.backup_dir:
        Path(args.backup_dir).mkdir(parents=True, exist_ok=True)

    if not args.skip_csv:
        for path in CSV_TARGETS:
            if not path.exists():
                print(f"missing   {path}")
                continue
            if args.dry_run:
                removed, total, odd = process_csv(path)
                print(f"would drop {removed:>8} of {total:>10} lines ({odd} lines not starting a record)  {path.name}", flush=True)
            else:
                removed, total, odd = process_csv(path, args.backup_dir, args.expect_csv_removed)
                print(f"dropped   {removed:>8} of {total:>10} lines ({odd} lines not starting a record)  {path.name}", flush=True)
    if args.only_csv:
        return

    for path in TARGETS:
        if not path.exists():
            print(f"missing   {path}")
            continue
        hits, rows = count_rows(path)
        if hits == 0:
            print(f"nothing   {path.name} ({path.parent.name})")
        elif args.dry_run:
            print(f"would drop {hits:>8} of {rows:>10} rows  {path.name} ({path.parent.name})")
        else:
            removed, before, after = rewrite(path, args.backup_dir)
            print(f"dropped   {removed:>8} rows ({before} -> {after})  {path.name} ({path.parent.name})", flush=True)


if __name__ == "__main__":
    main()
