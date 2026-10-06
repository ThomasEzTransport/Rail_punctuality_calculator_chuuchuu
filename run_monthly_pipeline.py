"""Run Chuuchuu_pipeline.ipynb once per month with papermill, each month in a fresh kernel.

A fresh kernel per month means memory is fully released between months (no leftover globals or
output history), which is what makes the full year fit in RAM. The notebook's `parameters` cell
(data_selection, export_enriched, export_summary) is overridden for each run; every executed
notebook is saved to papermill_runs/ with its outputs, including the failed ones (the failing cell
is highlighted at the top). A failing month doesn't stop the next ones.

The monthly enriched parquet files can then be stacked with merge_processed_parquet.py.

Usage (chuuchuu conda env):

    python run_monthly_pipeline.py                        # 2025_01 .. 2025_12
    python run_monthly_pipeline.py 2025_03 2025_04        # only these months
    python run_monthly_pipeline.py --no-export-enriched   # summaries only
    python run_monthly_pipeline.py --log-output           # stream cell outputs to the terminal

One-off setup on a new machine (registers the chuuchuu env as a kernel papermill can find):
    python -m pip install papermill
    python -m ipykernel install --user --name chuuchuu --display-name chuuchuu
"""

import argparse
import sys
import time
from pathlib import Path

import papermill as pm

HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "Chuuchuu_pipeline.ipynb"
RUNS_DIR = HERE / "papermill_runs"
DEFAULT_MONTHS = [f"2025_{month:02d}" for month in range(1, 13)]


def run_month(month, args):
    output_path = RUNS_DIR / f"Chuuchuu_pipeline_{month}.ipynb"
    parameters = {
        "data_selection": month,
        "export_enriched": "y" if args.export_enriched else "n",
        "export_summary": "y" if args.export_summary else "n",
    }
    print(f"\n=== {month} : running -> {output_path.relative_to(HERE)}", flush=True)
    try:
        pm.execute_notebook(
            NOTEBOOK,
            output_path,
            parameters=parameters,
            kernel_name=args.kernel,
            cwd=HERE,  # the notebook reads sup_data/ and writes summary_stats/ with relative paths
            log_output=args.log_output,
        )
        return "OK"
    except pm.PapermillExecutionError as e:
        # a Python error inside a cell (including the final sanity-check assert : exports run before it)
        return f"FAILED in cell [{e.exec_count}] : {e.ename}: {e.evalue}"
    except Exception as e:
        # anything else, e.g. the kernel dying when it runs out of memory
        return f"FAILED : {type(e).__name__}: {e}"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("months", nargs="*", default=DEFAULT_MONTHS,
                        help="data_selection values to run, e.g. 2025_01 (default: every month of 2025)")
    parser.add_argument("--kernel", default="chuuchuu", help="Jupyter kernel to run the notebook with")
    parser.add_argument("--no-export-enriched", dest="export_enriched", action="store_false",
                        help="don't write the enriched parquet for each month")
    parser.add_argument("--no-export-summary", dest="export_summary", action="store_false",
                        help="don't write the summary xlsx for each month")
    parser.add_argument("--log-output", action="store_true", help="stream cell outputs to the terminal")
    args = parser.parse_args()

    RUNS_DIR.mkdir(exist_ok=True)
    results = {}
    for month in args.months:
        start = time.time()
        status = run_month(month, args)
        results[month] = f"{status} ({(time.time() - start) / 60:.1f} min)"
        print(f"=== {month} : {results[month]}", flush=True)

    print("\n=== Summary")
    for month, status in results.items():
        print(f"{month}: {status}")
    n_failed = sum(status.startswith("FAILED") for status in results.values())
    if n_failed:
        print(f"\n{n_failed} month(s) failed : open the matching notebook in {RUNS_DIR.name}/ to see where")
    sys.exit(1 if n_failed else 0)


if __name__ == "__main__":
    main()
