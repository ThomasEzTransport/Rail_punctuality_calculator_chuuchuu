# Chuuchuu data corrections log

The parquet files are not tracked in git (they live on the shared drive and in `intermediate_outputs/`), so every
change made directly to the data is recorded here.

## 2026-11-04 : NS "all trains cancelled" artifact days removed

**Issue.** On 2025-02-06, 2025-02-20, 2025-04-03 and 2025-04-08 the NS feed flags ~99% of the stops as cancelled
(`arrivalCancelled = t` at the source), with an identical hour-by-hour pattern on the four days (0% between 02:00 and
03:00, 100% from 05:00 to the end of the day) and snapshot timestamps running until ~08:00 the next morning. A real
stoppage would not repeat identically on four ordinary days, so this is treated as a data-collection artifact.

**Impact if left in.**
- ~204k cancelled stops = 24% of all NS cancelled stops of 2025.
- NS stop-level cancellation rate: February 10.6% -> 4.1%, April 10.0% -> 2.7% without these days.
- NS punctuality (cancelled stops are counted as delayed): 3 min 86.5% -> ~87.6%, 10 min 93.6% -> ~94.8%.

**Change.** All rows with `agency == "NS"` and `date` in the four days were removed by
`suppress_ns_artifact_days.py` from:

| Where | File | Rows removed |
|---|---|---|
| shared drive (raw) | `delay_records_2025_02.parquet` | 116,587 |
| shared drive (raw) | `delay_records_2025_04.parquet` | 122,706 |
| shared drive (raw) | `delay_records_full_2025_april.parquet` | 122,706 |
| shared drive (raw) | `delay_records_full_2025_NS.parquet` | 239,293 |
| shared drive (raw) | `delay_records_full_2025.parquet` | 239,293 |
| shared drive `processed_data/` (enriched) | `data_chuuchuu_2025_02_enriched.parquet` | 112,464 |
| shared drive `processed_data/` (enriched) | `data_chuuchuu_2025_04_enriched.parquet` | 119,443 |
| shared drive `processed_data/` (enriched) | `data_chuuchuu_2025_01_to_2025_12_enriched.parquet` | 231,904 |
| local `intermediate_outputs/` (enriched) | the same three enriched files | **NOT DONE YET**, see below |

(The raw yearly file holds more rows than the enriched one because the pipeline's Step 0 had already dropped some rows.)

**Pending: local copies.** The three enriched files in `intermediate_outputs/` (112,464 / 119,443 / 231,904 rows to drop)
were not rewritten: the script's final file swap was refused with "Access denied" in the session that made the change
(the files were not locked and are unchanged). They are duplicates of the cleaned `processed_data/` files; to fix them run
`python suppress_ns_artifact_days.py --backup-dir <folder>` from the project environment (already-cleaned files are skipped),
or copy the cleaned files down from `processed_data/`.

**Not changed.**
- Raw CSV files (`delay_records_2025.csv.gz`, `delay_records_full_2025.csv`): they still contain these rows; anything
  re-converted from them must be filtered again (rerun the script, it is idempotent).
- `processed_data/old runs/` (archive of earlier runs) and the legacy local files
  `data_chuuchuu_full_enriched_04_09.parquet` and `data_chuuchuu_full_2025_april_enriched.parquet`.
- Summary xlsx files in `summary_stats/` still reflect the data **before** this removal and must be regenerated.
- 2025-04-23 (5 NS rows, collector outage) and the June days with elevated NS cancellations (6, 10, 12, 13, 17, 24 June)
  were not touched: the latter may be real strikes and have not been verified.

**Reversibility.** The removed rows were saved (one parquet per file) in the scratchpad of the session that made the change;
they can also be regenerated from the raw CSV.
