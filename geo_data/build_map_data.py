"""
Build the JSON data payload embedded in chuuchuu_stations_on_rfn.html.

Reads:
  - geo_data/rfn_caracteristiques.gpkg   -> track geometry, one code_ligne per segment
  - intermediate_outputs/data_chuuchuu_french_lines.parquet
        -> per-stop-event code_ligne match (output of 6_Chuuchuu_data_test_line_matching.ipynb)
  - sup_data/stations.csv                -> station lon/lat/uic
  - intermediate_outputs/network_routing_legs.parquet
  - intermediate_outputs/network_routing_segment_traffic.parquet
        -> shortest-path-per-leg + segment_id->code_ligne (output of 7_Chuuchuu_network_routing.ipynb)

Writes:
  - geo_data/map_data.json

Run with the geo_data_env conda environment (has geopandas):
  conda run -n geo_data_env python geo_data/build_map_data.py
"""
import json

import geopandas as gpd
import pandas as pd

intermediate_outputs_dir = "intermediate_outputs"

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

# --- Trains ("verify a specific run"): (route, distinct real stop-sequence) -> ----
# {stations, lines, legs}, for visually checking notebook 7's network-routing output.
# Keyed by distinct sequence rather than raw journey_id/date: two runs of the same
# route stopping at exactly the same stations always route through the same RFN
# segments, so journey_id/date would add ~857k near-duplicate entries for zero
# extra information. Collapsing to distinct (route, sequence) pairs gives far fewer
# entries (~1.4x the route count above) while still surfacing every real detour /
# holiday-schedule variant that the "modal sequence" above deliberately hides.
variant_counts = (
    journey_sequences.rename(columns={"db_id_str": "seq"})
    .groupby(["originalRoute", "seq"])
    .size()
    .rename("n_occurrences")
    .reset_index()
    .sort_values(["originalRoute", "n_occurrences"], ascending=[True, False])
)
variant_counts["variant_rank"] = variant_counts.groupby("originalRoute").cumcount() + 1
variant_counts["n_variants"] = variant_counts.groupby("originalRoute")["originalRoute"].transform("size")

leg_routing = pd.read_parquet(
    f"{intermediate_outputs_dir}/network_routing_legs.parquet",
    columns=["stop_lo", "stop_hi", "routing_status", "segment_ids", "path_coords"],
)
routed_legs = leg_routing[leg_routing["routing_status"] == "routed"].copy()
routed_legs["stop_lo"] = routed_legs["stop_lo"].astype("Int64").astype(str)
routed_legs["stop_hi"] = routed_legs["stop_hi"].astype("Int64").astype(str)
leg_to_segments = {(row.stop_lo, row.stop_hi): row.segment_ids for row in routed_legs.itertuples()}

segment_traffic = pd.read_parquet(
    f"{intermediate_outputs_dir}/network_routing_segment_traffic.parquet",
    columns=["segment_id", "code_ligne"],
).dropna(subset=["code_ligne"])
segment_to_line = {int(row.segment_id): str(int(row.code_ligne)) for row in segment_traffic.itertuples()}

# Real routed-path geometry per unique leg (deduplicated once at the network level,
# not per train -- many trains/routes share the same physical hop). A train's
# highlighted path is then just a lookup of its ordered `legs` keys into this table,
# rather than each of the ~44k trains embedding its own copy of the geometry.
# Highlighting the exact traveled path (instead of the whole code_ligne, the map's
# original approach) matters because a leg's shortest path can run through only a
# short stretch of a long line -- and, per a route/straight-line-distance check, a
# real subset of legs (~2% of leg-rows) are also implausible network-graph-artifact
# detours (station pairs a few km apart routed hundreds of km) that a whole-line
# highlight would have hidden entirely. Seeing the real path surfaces those directly.
leg_paths = {}
for row in routed_legs.itertuples():
    coords = row.path_coords
    if coords is None or len(coords) < 2:
        continue
    lo, hi = sorted((row.stop_lo, row.stop_hi))
    leg_paths[f"{lo}|{hi}"] = [[round(float(x), 5), round(float(y), 5)] for x, y in coords]

trains = {}
for row in variant_counts.itertuples():
    seq = row.seq
    filtered = [db_id for db_id in seq if db_id in resolved_ids]
    if len(filtered) < 2:
        continue

    # Candidate lines + routed legs come from the FULL real stop-to-stop sequence
    # (every actual leg the train ran), not the coordinate-filtered `filtered` list
    # above -- a station missing coordinates can still anchor a routed leg on either
    # side of it. `legs` lists EVERY real hop, including ones with no routed path
    # geometry (leg_key absent from leg_paths) -- the JS side needs that placeholder
    # to tell "no route data for this hop" apart from "hop doesn't exist", so it can
    # draw an actual gap instead of a misleading straight line bridging over it.
    # Kept in NATURAL travel order (stop_a|stop_b, not sorted lo|hi) -- leg_paths
    # geometry is always stored lo->hi regardless of which way a train actually
    # traveled it, so the JS side needs the real direction to know when to reverse
    # a leg's coordinates before stitching it onto the next one.
    candidate_lines = set()
    leg_keys = []
    for stop_a, stop_b in zip(seq, seq[1:]):
        lo, hi = sorted((stop_a, stop_b))
        leg_keys.append(f"{stop_a}|{stop_b}")
        for segment_id in leg_to_segments.get((lo, hi), ()):
            code = segment_to_line.get(int(segment_id))
            if code is not None:
                candidate_lines.add(code)

    key = row.originalRoute if row.n_variants == 1 else (
        f"{row.originalRoute} · variant {row.variant_rank}/{row.n_variants} ({row.n_occurrences} runs)"
    )
    trains[key] = {"stations": filtered, "lines": sorted(candidate_lines), "legs": leg_keys}

def _canonical_leg_key(key):
    a, b = key.split("|")
    return f"{a}|{b}" if a <= b else f"{b}|{a}"


print(f"{len(trains)} / {len(variant_counts)} train stop-sequences exported (>=2 mapped stations)")
n_with_lines = sum(1 for t in trains.values() if t["lines"])
n_with_path = sum(1 for t in trains.values() if any(_canonical_leg_key(k) in leg_paths for k in t["legs"]))
n_fully_routed = sum(
    1 for t in trains.values() if t["legs"] and all(_canonical_leg_key(k) in leg_paths for k in t["legs"])
)
print(f"{n_with_lines} / {len(trains)} have at least one candidate line from network routing")
print(f"{n_with_path} / {len(trains)} have at least one hop with routed path geometry")
print(f"{n_fully_routed} / {len(trains)} have every real hop routed (no gaps)")
print(f"{len(leg_paths)} unique routed-leg geometries exported")

data = {
    "lines": lines,
    "line_names": line_names,
    "stations": stations,
    "routes": routes,
    "trains": trains,
    "leg_paths": leg_paths,
}

with open("geo_data/map_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

print("wrote geo_data/map_data.json")
