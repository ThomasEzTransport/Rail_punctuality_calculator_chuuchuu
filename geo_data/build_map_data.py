"""
Build the JSON data payload embedded in chuuchuu_stations_on_rfn.html.

Reads:
  - geo_data/rfn_caracteristiques.gpkg   -> track geometry, one code_ligne per segment
  - intermediate_outputs/data_chuuchuu_french_lines.parquet
        -> per-stop-event code_ligne match (output of 6_Chuuchuu_data_test_line_matching.ipynb)
  - sup_data/stations.csv                -> station lon/lat/uic

Writes:
  - geo_data/map_data.json

Run with the geo_data_env conda environment (has geopandas):
  conda run -n geo_data_env python geo_data/build_map_data.py
"""
import json

import geopandas as gpd
import pandas as pd

SIMPLIFY_TOLERANCE_DEG = 0.0005  # roughly 50 m at French latitudes

# --- Track geometry, tagged with code_ligne + per-troncon characteristics ---
rfn = gpd.read_file("geo_data/rfn_caracteristiques.gpkg")[
    ["code_ligne", "lib_ligne", "rg_troncon", "ICV", "Vitesse", "geometry"]
]
rfn["geometry"] = rfn["geometry"].simplify(SIMPLIFY_TOLERANCE_DEG, preserve_topology=True)

line_names = (
    rfn.dropna(subset=["code_ligne"])
    .drop_duplicates(subset=["code_ligne"])
    .set_index("code_ligne")["lib_ligne"]
    .to_dict()
)

lines = []
for _, row in rfn.iterrows():
    code = row["code_ligne"]
    if pd.isna(code):
        continue
    code = str(int(code))
    geom = row["geometry"]
    if geom is None or geom.is_empty:
        continue
    geoms = geom.geoms if geom.geom_type == "MultiLineString" else [geom]
    for part in geoms:
        coords = [[round(x, 5), round(y, 5)] for x, y in part.coords]
        if len(coords) >= 2:
            lines.append({
                "code_ligne": code,
                "coords": coords,
                "rg_troncon": None if pd.isna(row["rg_troncon"]) else int(row["rg_troncon"]),
                "icv": None if pd.isna(row["ICV"]) else round(float(row["ICV"]), 1),
                "vitesse": None if pd.isna(row["Vitesse"]) else round(float(row["Vitesse"]), 1),
            })

print(f"{len(lines)} track segments across {len(line_names)} lines")

# --- Station -> code_ligne lookup, from the line-matching notebook output --
lines_df = pd.read_parquet(
    "intermediate_outputs/data_chuuchuu_french_lines.parquet",
    columns=[
        "deutscheBahnStopId", "stopName", "country", "code_ligne", "code_ligne_candidates",
        "line_match_status", "arrivalDelay", "originalRoute", "journey_id", "sort_time",
    ],
)
station_lookup = lines_df.drop_duplicates(subset=["deutscheBahnStopId"])[
    ["deutscheBahnStopId", "stopName", "country", "code_ligne", "code_ligne_candidates", "line_match_status"]
].copy()
station_lookup["db_id_str"] = station_lookup["deutscheBahnStopId"].astype("Int64").astype(str)

# --- Average arrival delay per station (seconds) ----------------------------
delay_stats = (
    lines_df.groupby("deutscheBahnStopId")["arrivalDelay"]
    .agg(avg_delay_sec="mean", n_delay_samples="count")
    .reset_index()
)
station_lookup = station_lookup.merge(delay_stats, on="deutscheBahnStopId", how="left")

stations_csv = pd.read_csv("sup_data/stations.csv", sep=";", low_memory=False)
stations_csv = stations_csv.dropna(subset=["db_id", "latitude", "longitude"])
stations_csv["db_id_str"] = stations_csv["db_id"].astype("int64").astype(str)
stations_csv_small = stations_csv[["db_id_str", "uic", "latitude", "longitude"]].drop_duplicates(subset=["db_id_str"])

merged = station_lookup.merge(stations_csv_small, on="db_id_str", how="inner")
print(f"{len(merged)} / {len(station_lookup)} unique stations resolved to coordinates")

stations = []
for _, row in merged.iterrows():
    candidates = row["code_ligne_candidates"]
    candidates = list(candidates) if candidates is not None and len(candidates) else []
    candidates = [str(int(c)) for c in candidates]
    code = row["code_ligne"]
    n_samples = row["n_delay_samples"]
    stations.append({
        "name": row["stopName"],
        "db_id": row["db_id_str"],
        "uic": None if pd.isna(row["uic"]) else int(row["uic"]),
        "lon": round(float(row["longitude"]), 5),
        "lat": round(float(row["latitude"]), 5),
        "code_ligne": None if pd.isna(code) else str(int(code)),
        "candidates": candidates,
        "status": row["line_match_status"],
        "avg_delay_sec": None if pd.isna(row["avg_delay_sec"]) else round(float(row["avg_delay_sec"]), 1),
        "n_delay_samples": 0 if pd.isna(n_samples) else int(n_samples),
    })

print(f"{len(stations)} stations exported")
n_with_delay = sum(1 for s in stations if s["avg_delay_sec"] is not None)
print(f"{n_with_delay} / {len(stations)} stations have arrival-delay data")

# --- Routes ("trains"): originalRoute -> ordered list of station db_ids -----
# originalRoute (e.g. "INTERCITES 3604") is a recurring named service, not a single
# day's run -- it operates on many dates under the same journey_id pattern. Per
# route, take the MODAL stop sequence across all its runs (not just the first one),
# so an occasional detour/holiday-schedule day doesn't define the "canonical" path.
# Sequences are then filtered down to only the stations we actually have coordinates
# for (this script's `stations` list) -- any stop outside that set is dropped from
# the path rather than breaking the whole route.
resolved_ids = {s["db_id"] for s in stations}

route_rows = lines_df.dropna(subset=["originalRoute", "deutscheBahnStopId", "sort_time"]).copy()
route_rows["db_id_str"] = route_rows["deutscheBahnStopId"].astype("Int64").astype(str)
route_rows = route_rows.sort_values(["originalRoute", "journey_id", "sort_time"])

journey_sequences = (
    route_rows.groupby(["originalRoute", "journey_id"])["db_id_str"]
    .apply(tuple)
    .reset_index()
)


def modal_sequence(group):
    return group["db_id_str"].value_counts().idxmax()


modal_sequences = journey_sequences.groupby("originalRoute").apply(modal_sequence, include_groups=False)

routes = {}
for route_name, seq in modal_sequences.items():
    filtered = [db_id for db_id in seq if db_id in resolved_ids]
    if len(filtered) >= 2:
        routes[route_name] = filtered

print(f"{len(routes)} / {len(modal_sequences)} routes exported (>=2 mapped stations)")

data = {
    "lines": lines,
    "line_names": line_names,
    "stations": stations,
    "routes": routes,
}

with open("geo_data/map_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

print("wrote geo_data/map_data.json")
