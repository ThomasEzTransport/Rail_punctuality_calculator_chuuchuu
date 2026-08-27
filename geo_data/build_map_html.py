"""
Assemble geo_data/chuuchuu_stations_on_rfn.html from map_template.html + map_data.json.

Run after build_map_data.py (either env with pandas is fine, no geopandas needed here):
  python geo_data/build_map_html.py
"""
with open("geo_data/map_data.json", encoding="utf-8") as f:
    data_json = f.read()

with open("geo_data/map_template.html", encoding="utf-8") as f:
    template = f.read()

output = template.replace("/*__DATA__*/", data_json)

with open("geo_data/chuuchuu_stations_on_rfn.html", "w", encoding="utf-8") as f:
    f.write(output)

print(f"wrote geo_data/chuuchuu_stations_on_rfn.html ({len(output):,} bytes)")
