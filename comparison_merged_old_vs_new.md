# Comparison: `chuuchuu_summary_monthly_merged_old.xlsx` vs `chuuchuu_summary_monthly_merged.xlsx`

Written for: the pipeline owner, to decide whether the new merged file can replace the old one.

Both files were read read-only and compared sheet by sheet. Rows were matched on all non-count columns (Year, Month, operator, scope, joint service, route/journey type, HSR, long distance, night train). Neither file has duplicate keys. Explanations of *why* things changed are inferences (see end); the numbers are measured.

## 1. Bottom line

- **Same structure, slightly lower counts.** Same 8 sheets and same columns (Summary has no "Joint service" column, per-operator sheets do). Only the row counts differ.
- **Overall, the new file has 0.38% fewer trains** (8,029,942 → 7,999,098, −30,844). Cancellations fall 0.93%, delays >5 min 0.99%, delays >15 min 1.60%.
- **Almost all of the drop is in a few operators**: DB (−12,085), SNCF (−4,069), SNCB (−3,445), SBB (−3,410), Eurostar (−2,197), UNKNOWN_OPERATOR (−1,659), Ceske Drahy (−1,374), OEBB (−1,287), NS (−860), PKP (−783).
- **The change looks like de-duplication, not data loss**: it is spread over all 12 months and the cancelled/delay counts fall roughly in line with trains. The exception is SBB delays (see §4).
- **The new file looks better and should be preferred**, but check the items in §5 first.
- **Internal consistency is OK in both files**: full + partial cancellations equal the "full + partial" column in every row, and no delay bucket exceeds total trains.

## 2. Summary sheet, by month (total trains)

| Month   |     Old |     New |   Diff | Diff % |
|:--------|--------:|--------:|-------:|-------:|
| 2025-01 | 619,773 | 618,339 | −1,434 | −0.23% |
| 2025-02 | 572,376 | 570,819 | −1,557 | −0.27% |
| 2025-03 | 625,538 | 623,737 | −1,801 | −0.29% |
| 2025-04 | 580,168 | 578,659 | −1,509 | −0.26% |
| 2025-05 | 647,761 | 645,894 | −1,867 | −0.29% |
| 2025-06 | 611,488 | 608,616 | −2,872 | −0.47% |
| 2025-07 | 627,843 | 624,153 | −3,690 | −0.59% |
| 2025-08 | 610,831 | 607,336 | −3,495 | −0.57% |
| 2025-09 | 646,573 | 643,599 | −2,974 | −0.46% |
| 2025-10 | 813,038 | 809,662 | −3,376 | −0.42% |
| 2025-11 | 806,549 | 803,581 | −2,968 | −0.37% |
| 2025-12 | 868,004 | 864,703 | −3,301 | −0.38% |
| **Total** | **8,029,942** | **7,999,098** | **−30,844** | **−0.38%** |

The drop is stable at 0.2–0.6% per month, with a slightly larger effect from June onward.

Row-level on the Summary sheet: 2,362 old rows vs 2,361 new. 2,344 rows are in both, and 564 of those have different values. 18 rows exist only in the old file (1,659 trains) and 17 only in the new file (605 trains).

- Old-only rows are mostly scope "national network", route type D, international.
- New-only rows are all scope "whole journey", route type D.
- That pattern looks like trains moving from national-network scope to whole-journey scope, mostly operator UNKNOWN_OPERATOR.
- Trains in "national network" scope fall from 7,932,753 to 7,903,505 (−29,248), and in "whole journey" scope from 97,189 to 95,593 (−1,596).

## 3. Differences by operator

Total trains, old → new:

| Operator             |       Old |       New |    Diff |  Diff % |
|:---------------------|----------:|----------:|--------:|--------:|
| **DB**               |   345,991 |   333,906 | −12,085 |  −3.49% |
| SNCF                 |   834,087 |   830,018 |  −4,069 |  −0.49% |
| SNCB                 | 1,047,006 | 1,043,561 |  −3,445 |  −0.33% |
| SBB                  |   368,228 |   364,818 |  −3,410 |  −0.93% |
| **Eurostar**         |    42,681 |    40,484 |  −2,197 |  −5.15% |
| UNKNOWN_OPERATOR     |    84,256 |    82,597 |  −1,659 |  −1.97% |
| **Ceske Drahy**      |    22,548 |    21,174 |  −1,374 |  −6.09% |
| OEBB                 |   142,931 |   141,644 |  −1,287 |  −0.90% |
| NS                   | 1,903,643 | 1,902,783 |    −860 |  −0.05% |
| **PKP**              |    12,165 |    11,382 |    −783 |  −6.44% |
| DSB                  |    10,120 |    10,005 |    −115 |  −1.14% |
| **SJ**               |       702 |       631 |     −71 | −10.11% |
| Trenitalia           | 2,970,390 | 2,970,347 |     −43 |   ~0%   |
| MAV                  |    17,676 |    17,659 |     −17 |  −0.10% |
| ZSSK                 |     2,114 |     2,102 |     −12 |  −0.57% |
| Other CH operators   |   123,551 |   123,544 |      −7 |   ~0%   |
| Flixtrain            |     6,231 |     6,228 |      −3 |  −0.05% |
| Westbahn             |    21,042 |    21,041 |      −1 |   ~0%   |
| **Snalltaget** (new) |         0 |       594 |    +594 |    new  |

Bold rows are the largest absolute or relative changes.

The remaining operators are unchanged: Panorama Express, Ouigo, CFL, CFR, HZ, European Sleeper, SZ, Trenitalia France, UZ.

**Snalltaget is a new operator in the new file** (594 trains, 162 delayed >15 min, plus 11 OEBB_Snalltaget rows on the OEBB sheet). It is probably carved out of UNKNOWN_OPERATOR, which loses 1,659 trains. That is only an inference from the numbers.

## 4. Per-sheet findings

| Sheet      | Rows old | Rows new |  Trains old |  Trains new | Diff % |
|:-----------|---------:|---------:|------------:|------------:|-------:|
| SNCF       |      288 |      288 |     834,087 |     830,018 | −0.49% |
| DB         |      687 |      757 |     345,991 |     333,906 | −3.49% |
| NS         |      163 |      193 |   1,903,643 |   1,902,783 | −0.05% |
| OEBB       |      647 |      676 |     142,931 |     141,644 | −0.90% |
| SBB        |      401 |      442 |     368,228 |     364,818 | −0.93% |
| SNCB       |      194 |      194 |   1,047,006 |   1,043,561 | −0.33% |
| Trenitalia |      394 |      394 |   2,970,390 |   2,970,347 |   ~0%  |

Notes per sheet:

- **SNCF**: drop concentrated in June–September (−2.3% to −2.8% per month). Joint service SNCB: 19,020 → 16,917.
- **DB**: 80 new-only rows (1,347 trains, mostly NJ/IC/EN). Cancellations fall 6.1%. The drop grows over the year (−2.4% in Jan → −6.1% in Dec).
- **NS**: 31 new-only rows (346 trains, mostly NJ), new joint services DB_OEBB and DB_OEBB_SBB.
- **OEBB**: new joint services (OEBB_Snalltaget, DB_OEBB_PKP, Ceske Drahy_DB/PKP) and 11 "whole journey" trains where there were none.
- **SBB**: delays >5 min fall 5.9% and >15 min 6.3%, far more than trains (−0.9%).
- **SNCB**: same rows. Only 16 rows changed, mostly July–August.
- **Trenitalia**: same rows. Only 6 changed (−43 trains).

Other observations:

- **Joint-service labels are being re-attributed.** Examples: Ceske Drahy_DB_PKP 684 → 181 with Ceske Drahy_DB_OEBB_PKP 53 → 217; DB_SBB (DB sheet) 20,193 → 19,315; OEBB (DB sheet) 12,372 → 9,932; DB_OEBB appears on the SBB sheet (548) and NS sheet (194). Labels were relabelled or merged across the sheets, so **do not compare joint-service rows between the two files without re-aggregating**.
- **Joint service labels now include more partners** (PKP, SJ, DSB, SBB with OEBB). The DB sheet gained ~70 rows, so the mapping of joint services is more granular in the new file.

## 5. Things to check before replacing the old file

1. **Why SBB delays fall 6% while trains fall 0.9%.** This is out of proportion to every other sheet. It may be legitimate (removing duplicate delayed international trains) or a side effect of the dedup/matching logic.
2. **DB drop of 3.5% (6.1% cancellations)** and its growth through the year (−2.4% in Jan → −6.1% in Dec). Verify that the removed trains are true duplicates and that the cause does not start mid-year.
3. **Eurostar (−5.2%), Ceske Drahy (−6.1%), PKP (−6.4%) and SJ (−10.1%)** are the largest relative changes. They are small operators, but they are international services, which are the ones most exposed to double counting.
4. **Snalltaget**: confirm the intended source of the new operator and that UNKNOWN_OPERATOR's drop matches.
5. **The Summary sheet has 18 old-only and 17 new-only rows** with tiny counts (1–290 trains each), mostly scope changes between "national network" and "whole journey". These are likely classification changes, not missing data.

## 6. Likely cause

The last commits in the repo are "Updating pipeline to deduplicate trains running with two train sets", "Simplifying deduplication phase - Adding Flixtrain and WB services in the general deduplication phase" and "Re run after changing deduplication step Flix and WB". I did not inspect the notebook diff, so this is an inference: the smaller counts, concentrated in international and joint-service trains (DB, SNCF, SNCB, SBB, Eurostar, Ceske Drahy, PKP), match removal of duplicate train records and relabelling of joint services. Trenitalia, SNCB (apart from a few rows), Ouigo and CFL, which run few or no trains with two train sets, are almost unchanged, which supports this.

## 7. Method note

Files compared: `summary_stats/chuuchuu_summary_monthly_merged_old.xlsx` and `summary_stats/chuuchuu_summary_monthly_merged.xlsx`. No existing file was modified; this report is the only new file written. The temporary scripts are in the session scratchpad.
