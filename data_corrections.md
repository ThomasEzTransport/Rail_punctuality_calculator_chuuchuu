# Chuuchuu data corrections log

The parquet files are not tracked in git (they live on the shared drive and in `intermediate_outputs/`), so every
change made directly to the data is recorded here.

## 2026-11-05 : OEBB trains with no delay data at all dropped in the pipeline

**Issue.** Some OEBB trains have no `arrivalDelay` at any stop and no cancellation flag. Step 7 counts them in
`N total train` as not delayed (i.e. on time). For OEBB long-distance day trains with a known journey type that is 5,600 of
126,777 units (4.4%); 5,502 of them have no measured arrival anywhere in Austria. Other operators are much less affected
(SBB 2.0%, Trenitalia 0.8%, DB 0.2%), except Westbahn (71.8%, not treated).

**Change.** The parquet/CSV files are **not** modified: `Chuuchuu_pipeline.ipynb` (right after `OEBB_EXCLUDED_DAYS`)
drops every OEBB-agency train except Westbahn (`routeType` `WB`) (key: `routeType`, `routeNumber`, `date`) where no stop has an `arrivalDelay` and none is
cancelled. Trains with at least one measured delay or a cancellation are kept. Applied to all route types of the OEBB agency, not only long distance: on the raw 2025 OEBB file it removes ~37,000 of ~177,000 non-Westbahn trains, mostly CAT airport trains (23,829), buses and GEP. The row count is reported in the final
"Summary of the process" cell.

## 2026-11-04 : OEBB outage / missing-delay days excluded in the pipeline

**Issue (confirmed by the data provider, no backup data exists).** OEBB: no data 22-31 Oct; only partly recorded on
27 Jan, 23-24 Apr and 1 Nov; on 24-25 Jul, 8-9 Nov and 22-23 Nov (and slightly 24 Nov) 41-70% of the rows have no delay.

**Change.** Unlike NS, the parquet/CSV files are **not** modified: `Chuuchuu_pipeline.ipynb` (right after Step 0's
invalid-timestamp filter, `OEBB_EXCLUDED_DAYS`) drops the OEBB rows of these 11 days, nothing else. October OEBB is a
21-day month. The DB-agency `81...` stop rows are deliberately not used as a substitute (double count with DB, ~10% of
volume, international trains only). Other OEBB findings (Westbahn / foreign-operator missing delays, new IR type) are
not treated.

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
| shared drive (raw CSV) | `delay_records_full_2025.csv` | 239,293 lines (of 85,236,926 records) |
| shared drive (raw CSV) | `delay_records_2025.csv.gz` | 239,293 lines (of 85,236,926 records) |
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
- Other raw CSVs: `delay_records_FR_2025.csv`, `delay_records_sbb_2025.csv` (single agency, no NS) and the 2026 test
  exports have no NS rows for these dates.
- `processed_data/old runs/` (archive of earlier runs) and the legacy local files
  `data_chuuchuu_full_enriched_04_09.parquet` and `data_chuuchuu_full_2025_april_enriched.parquet`.
- Summary xlsx files in `summary_stats/` still reflect the data **before** this removal and must be regenerated.
- 2025-04-23 (5 NS rows, collector outage) and the June days with elevated NS cancellations (6, 10, 12, 13, 17, 24 June)
  were not touched: the latter may be real strikes and have not been verified.

**CSV method.** The CSVs hold one record per line, so the NS lines of the four dates were dropped by streaming and every
other byte was copied unchanged (the header, line endings and the quoted JSON `extra` field are untouched). The number
of removed lines (239,293) was required to equal the number of rows removed from `delay_records_full_2025.parquet`
before the original was replaced; the rewritten files were then re-read to check integrity and that no artifact line remains.
Anything re-exported from the source or regenerated from an older copy must be filtered again (rerun the script, it is idempotent).

**Reversibility.** The removed rows were saved (one parquet per parquet file, one `.csv.gz` per CSV) in the scratchpad of
the session that made the change; they are not stored in the repo or on the drive.
