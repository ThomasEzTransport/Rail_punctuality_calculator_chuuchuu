"""Shared-drive locations of the Chuuchuu data, used by every notebook of the project.

The raw delay records and the enriched parquet files are too large for the repo: they live on the
T&A Google Drive (Rail_databases/punctuality_big_data/Chuuchuu). This module is the only place
where the local mount points of that folder are listed.

    from chuuchuu_paths import CHUUCHUU_DIR, ENRICHED_DIR, output_path

    output_path("2025_01")              # monthly enriched file written by Chuuchuu_pipeline.ipynb
    output_path("2025_01_to_2025_12")   # merged file written by 8_Chuuchuu_merge_monthly_summary.ipynb
"""

import os
from pathlib import Path

# personal PC / VM shared-drive mount points for the Chuuchuu folder : add a new entry here if
# the project runs somewhere else and the folder isn't found
CANDIDATE_CHUUCHUU_FOLDERS = [
    r"G:\.shortcut-targets-by-id\1fop_2EKRGMK369J15pyuC9039CxT_tnw\Rail_databases\punctuality_big_data\Chuuchuu",  # personal PC
    r"H:\.shortcut-targets-by-id\18oT0tHU4ycBoKA7-PZZc_W0DyRedU_Jt\T&A\Shared knowledge tools and data\data_sources\Rail_databases\punctuality_big_data\Chuuchuu",  # VM
    r"D:\.shortcut-targets-by-id\18oT0tHU4ycBoKA7-PZZc_W0DyRedU_Jt\T&A\Shared knowledge tools and data\data_sources\Rail_databases\punctuality_big_data\Chuuchuu",  # VM (older drive letter)
]

# os.path.isdir rather than Path.is_dir: a drive letter mapped to something else on this machine
# (e.g. G: on the VM) raises PermissionError with Path.is_dir, os.path.isdir just returns False
CHUUCHUU_DIR = next((Path(path) for path in CANDIDATE_CHUUCHUU_FOLDERS if os.path.isdir(path)), None)
if CHUUCHUU_DIR is None:
    raise FileNotFoundError(
        "Could not find the Chuuchuu shared-drive folder on this machine : no path in "
        "CANDIDATE_CHUUCHUU_FOLDERS exists. Add this machine's local mount path to chuuchuu_paths.py."
    )

# enriched per-stop parquet files (pipeline outputs, monthly and merged)
ENRICHED_DIR = CHUUCHUU_DIR / "processed_data"


def output_path(data_selection):
    """Path of the enriched parquet file for a data_selection, e.g. "2025_01" or "2025_01_to_2025_12"."""
    return ENRICHED_DIR / f"data_chuuchuu_{data_selection}_enriched.parquet"
