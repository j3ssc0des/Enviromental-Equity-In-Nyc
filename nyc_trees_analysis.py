

#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║   NYC STREET TREE CENSUS  ·  Green Space Inequity Analysis       ║
║   Data: NYC Open Data 2005 & 2015 Street Tree Census             ║
║   Tools: Python · Pandas · GeoPandas · Folium                    ║
╚══════════════════════════════════════════════════════════════════╝

HOW TO USE:
  LIVE_DATA = True  — fetch live from data.cityofnewyork.us (default)
  LIVE_DATA = False — use realistic embedded dataset (offline / CI fallback)

  The script automatically falls back to embedded data if the API is
  unreachable, so it always produces a map regardless of network state.

OUTPUT: nyc_trees_map.html  (interactive Folium choropleth map)
"""

import warnings, json, textwrap, io, time
import numpy as np
import pandas as pd
import folium
from folium import GeoJson, LayerControl
from folium.plugins import HeatMap, MiniMap
from branca.colormap import LinearColormap
from branca.element import Element
import geopandas as gpd
from shapely.geometry import Polygon, Point, mapping
warnings.filterwarnings("ignore")

# ────────────────────────────────────────────────────────────────
LIVE_DATA   = True    # Set False to use embedded dataset
OUTPUT_HTML = "nyc_trees_map.html"
# ────────────────────────────────────────────────────────────────

print("=" * 65)
print("  🌳  NYC Green Space Inequity — Street Tree Census Analysis")
print("=" * 65)


# ════════════════════════════════════════════════════════════════
# 1.  DATA
#     Embedded dataset is always defined — it acts as both the
#     offline fallback AND the income lookup for live mode
#     (income is not in the tree census datasets).
# ════════════════════════════════════════════════════════════════

NTA_RECORDS = [
    # code, name, borough, lat, lon, area_km2, trees_15, trees_05, income
    # ── MANHATTAN ──────────────────────────────────────────────────────
    ("MN2501","Battery Park City-Lower Manhattan","Manhattan",40.7127,-74.0148,1.1, 820, 690,140000),
    ("MN2502","Greenwich Village-SoHo",           "Manhattan",40.7264,-74.0026,1.4,1350,1100,125000),
    ("MN2503","Chinatown",                        "Manhattan",40.7158,-73.9970,0.9, 480, 390, 38000),
    ("MN2504","Lower East Side",                  "Manhattan",40.7153,-73.9853,1.8,1120, 940, 32000),
    ("MN2505","Upper East Side-Carnegie Hill",    "Manhattan",40.7749,-73.9565,3.2,3200,2900,145000),
    ("MN2506","Lenox Hill-Roosevelt Island",      "Manhattan",40.7665,-73.9607,2.8,2800,2500,132000),
    ("MN2507","Central Harlem South",             "Manhattan",40.8134,-73.9468,2.2,2100,1750, 36000),
    ("MN2508","East Harlem (El Barrio)",          "Manhattan",40.7957,-73.9376,3.1,2950,2600, 30000),
    ("MN2509","Washington Heights North",         "Manhattan",40.8501,-73.9396,2.7,2700,2200, 38000),
    ("MN2510","Washington Heights South",         "Manhattan",40.8397,-73.9401,2.4,2400,2050, 40000),
    ("MN2511","Inwood",                           "Manhattan",40.8676,-73.9221,2.9,3100,2700, 44000),
    ("MN2701","West Village",                     "Manhattan",40.7341,-74.0038,1.2,1180, 950,155000),
    ("MN2702","Chelsea-Hudson Yards",             "Manhattan",40.7465,-74.0014,2.6,1900,1650,130000),
    ("MN2703","Hell's Kitchen-Clinton",           "Manhattan",40.7625,-73.9912,2.1,1750,1520, 90000),
    ("MN2704","Midtown-Midtown South",            "Manhattan",40.7549,-73.9840,3.5,1420,1280,105000),
    ("MN2705","Murray Hill-Kips Bay",             "Manhattan",40.7465,-73.9771,1.6,1250,1100,115000),
    ("MN2706","Stuyvesant Town-Cooper Village",   "Manhattan",40.7315,-73.9786,0.8, 740, 680,105000),
    ("MN2707","East Village",                     "Manhattan",40.7268,-73.9816,1.7,1100, 960, 72000),
    ("MN2708","Upper West Side",                  "Manhattan",40.7870,-73.9754,3.0,3100,2800,130000),
    ("MN2709","Morningside Heights",              "Manhattan",40.8101,-73.9610,1.9,2000,1800, 55000),
    ("MN2710","Hamilton Heights",                 "Manhattan",40.8231,-73.9522,1.8,1900,1600, 48000),
    # ── BROOKLYN ───────────────────────────────────────────────────────
    ("BK0101","Greenpoint",                       "Brooklyn",40.7292,-73.9519,2.8,3200,2700, 78000),
    ("BK0102","Williamsburg",                     "Brooklyn",40.7081,-73.9571,3.9,3900,3100, 72000),
    ("BK0201","Clinton Hill",                     "Brooklyn",40.6883,-73.9617,1.9,2100,1800, 92000),
    ("BK0202","Fort Greene",                      "Brooklyn",40.6893,-73.9752,1.7,2000,1700, 88000),
    ("BK0203","Brooklyn Heights-Cobble Hill",     "Brooklyn",40.6956,-73.9937,2.1,2300,2000,145000),
    ("BK0204","Carroll Gardens-Red Hook",         "Brooklyn",40.6773,-73.9987,3.8,4200,3600, 82000),
    ("BK0301","Crown Heights North",              "Brooklyn",40.6737,-73.9373,4.1,4800,4100, 48000),
    ("BK0302","Crown Heights South",              "Brooklyn",40.6571,-73.9373,3.8,4200,3500, 42000),
    ("BK0401","East New York",                    "Brooklyn",40.6501,-73.8826,9.2,7200,5800, 32000),
    ("BK0402","Cypress Hills-City Line",          "Brooklyn",40.6727,-73.8847,4.2,3900,3100, 34000),
    ("BK0501","Flatbush",                         "Brooklyn",40.6419,-73.9580,5.1,5600,4800, 52000),
    ("BK0502","East Flatbush-Farragut",           "Brooklyn",40.6376,-73.9393,5.8,6200,5200, 46000),
    ("BK0601","Canarsie",                         "Brooklyn",40.6337,-73.9029,7.4,7800,6500, 58000),
    ("BK0701","Bay Ridge",                        "Brooklyn",40.6313,-74.0300,6.9,7500,6600, 72000),
    ("BK0702","Dyker Heights",                    "Brooklyn",40.6246,-74.0113,3.4,4100,3500, 78000),
    ("BK0801","Bensonhurst West",                 "Brooklyn",40.6108,-73.9978,4.6,5200,4400, 62000),
    ("BK0802","Bensonhurst East",                 "Brooklyn",40.6092,-73.9835,4.3,4800,4100, 58000),
    ("BK0901","Sunset Park West",                 "Brooklyn",40.6497,-74.0027,3.6,3800,3100, 48000),
    ("BK1001","Borough Park",                     "Brooklyn",40.6275,-73.9960,4.8,5300,4500, 56000),
    ("BK1101","Sheepshead Bay",                   "Brooklyn",40.5990,-73.9464,7.2,8100,6800, 68000),
    ("BK1201","Brownsville",                      "Brooklyn",40.6637,-73.9113,4.7,3900,3000, 26000),
    ("BK1202","Ocean Hill",                       "Brooklyn",40.6784,-73.9156,2.3,2400,1900, 30000),
    ("BK1301","Flatlands",                        "Brooklyn",40.6198,-73.9327,8.1,9200,7800, 64000),
    ("BK1401","Park Slope-Gowanus",               "Brooklyn",40.6723,-73.9844,4.2,4900,4200,115000),
    ("BK1501","Prospect Heights",                 "Brooklyn",40.6769,-73.9670,1.8,2100,1800, 98000),
    # ── BRONX ──────────────────────────────────────────────────────────
    ("BX0101","Wakefield-Woodlawn",               "Bronx",40.8988,-73.8593,7.3,6800,5800, 52000),
    ("BX0201","Norwood",                          "Bronx",40.8804,-73.8764,3.8,3600,3000, 46000),
    ("BX0301","Fordham South",                    "Bronx",40.8596,-73.8978,2.9,2700,2200, 34000),
    ("BX0302","Fordham North",                    "Bronx",40.8698,-73.8881,3.2,3000,2500, 36000),
    ("BX0401","Mott Haven-Port Morris",           "Bronx",40.8088,-73.9217,3.6,2400,1900, 24000),
    ("BX0402","Melrose South-Mott Haven North",   "Bronx",40.8201,-73.9216,2.8,1900,1500, 26000),
    ("BX0501","Highbridge",                       "Bronx",40.8372,-73.9249,2.4,2300,1800, 28000),
    ("BX0601","Hunts Point",                      "Bronx",40.8121,-73.8944,4.8,2900,2300, 22000),
    ("BX0701","Longwood",                         "Bronx",40.8237,-73.9003,2.1,2000,1600, 25000),
    ("BX0801","Morrisania-Melrose",               "Bronx",40.8330,-73.9092,3.2,2800,2200, 28000),
    ("BX0901","Soundview-Bruckner",               "Bronx",40.8213,-73.8722,5.7,5100,4200, 36000),
    ("BX1001","Pelham Parkway",                   "Bronx",40.8603,-73.8661,5.2,5600,4700, 54000),
    ("BX1101","Parkchester",                      "Bronx",40.8422,-73.8641,4.6,4200,3500, 44000),
    ("BX1201","Throgs Neck-Co-op City",           "Bronx",40.8382,-73.8310,12.4,9800,7800, 58000),
    ("BX1301","Riverdale-Spuyten Duyvil",         "Bronx",40.9011,-73.9102,6.8,7800,6500, 90000),
    ("BX1401","Country Club",                     "Bronx",40.8399,-73.8301,5.1,5400,4500, 62000),
    # ── QUEENS ─────────────────────────────────────────────────────────
    ("QN0101","Astoria",                          "Queens",40.7721,-73.9303,5.7,5800,4900, 68000),
    ("QN0102","Woodside",                         "Queens",40.7448,-73.9014,4.2,4500,3800, 64000),
    ("QN0201","Flushing",                         "Queens",40.7675,-73.8330,7.8,7500,6200, 58000),
    ("QN0202","Murray Hill-Flushing",             "Queens",40.7563,-73.8256,5.4,5600,4700, 62000),
    ("QN0301","Jamaica",                          "Queens",40.7068,-73.8038,8.3,7200,5900, 46000),
    ("QN0302","South Jamaica",                    "Queens",40.6896,-73.7921,5.1,4300,3500, 38000),
    ("QN0401","Richmond Hill",                    "Queens",40.6995,-73.8334,5.8,5900,4900, 60000),
    ("QN0402","Woodhaven",                        "Queens",40.6960,-73.8562,4.5,5200,4400, 62000),
    ("QN0501","Forest Hills-Rego Park",           "Queens",40.7189,-73.8501,7.1,8200,6900, 88000),
    ("QN0502","Kew Gardens",                      "Queens",40.7079,-73.8295,3.8,4600,3900, 82000),
    ("QN0601","Far Rockaway-Bayswater",           "Queens",40.6052,-73.7562,9.2,6500,5200, 42000),
    ("QN0701","Howard Beach-Lindenwood",          "Queens",40.6596,-73.8476,8.9,9100,7600, 72000),
    ("QN0801","Maspeth",                          "Queens",40.7296,-73.9097,5.6,6200,5200, 76000),
    ("QN0901","Fresh Meadows-Utopia",             "Queens",40.7310,-73.7891,9.8,11200,9400, 90000),
    ("QN1001","Bayside-Bayside Hills",            "Queens",40.7663,-73.7726,8.4,10200,8700, 95000),
    ("QN1101","Springfield Gardens North",        "Queens",40.6666,-73.7686,6.7,6400,5200, 52000),
    ("QN1201","Jackson Heights",                  "Queens",40.7516,-73.8830,3.9,4200,3500, 55000),
    ("QN1301","Long Island City-Astoria",         "Queens",40.7447,-73.9483,4.4,4100,3300, 76000),
    # ── STATEN ISLAND ──────────────────────────────────────────────────
    ("SI0101","St. George-New Brighton",          "Staten Island",40.6439,-74.0901,5.6,6200,5100, 64000),
    ("SI0201","Mariner's Harbor-Arlington",       "Staten Island",40.6343,-74.1564,7.8,8400,7000, 58000),
    ("SI0301","West Brighton-Port Richmond",      "Staten Island",40.6346,-74.1322,6.4,7100,5900, 60000),
    ("SI0401","Stapleton-Rosebank",               "Staten Island",40.6248,-74.0739,5.1,5700,4700, 62000),
    ("SI0501","Richmond Town-Richmond Valley",    "Staten Island",40.5698,-74.1554,14.2,18400,14500, 82000),
    ("SI0601","Great Kills",                      "Staten Island",40.5533,-74.1500,9.7,12300,10100, 86000),
    ("SI0701","Tottenville-Charleston",           "Staten Island",40.5119,-74.2004,21.8,28200,22000, 88000),
    ("SI0801","Annadale-Huguenot",                "Staten Island",40.5368,-74.1682,12.1,15600,12400, 90000),
    ("SI0901","New Springville-Bloomfield",       "Staten Island",40.5859,-74.1726,11.4,14200,11200, 84000),
    ("SI1001","South Shore",                      "Staten Island",40.5348,-74.1907,10.8,13500,10700, 87000),
]

_COLS = ["nta_code","nta_name","boro_name","lat","lon","area_km2",
         "trees_2015","trees_2005","median_income"]

# Income lookup keyed by both code and name (used in live mode)
_INCOME_BY_CODE = {r[0]: r[8] for r in NTA_RECORDS}
_INCOME_BY_NAME = {r[1]: r[8] for r in NTA_RECORDS}
_DEFAULT_INCOME = int(np.median([r[8] for r in NTA_RECORDS]))

# ── Retry helper ─────────────────────────────────────────────────────────
def _fetch(url, params=None, max_retries=3, timeout=40):
    """GET with exponential-backoff retry. Raises on final failure."""
    import requests
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            r.raise_for_status()
            return r
        except Exception as exc:
            if attempt == max_retries:
                raise
            delay = 2 ** attempt
            print(f"   ⚠ Attempt {attempt}/{max_retries} failed: {exc}")
            print(f"     Retrying in {delay}s…")
            time.sleep(delay)

# ── Live fetch ────────────────────────────────────────────────────────────
live_ok = False

if LIVE_DATA:
    try:
        import requests

        print("\n📡 Fetching 2015 tree census from NYC Open Data…")
        r = _fetch(
            "https://data.cityofnewyork.us/resource/uvpi-gqnh.json",
            params={"$select": "nta,boroname,COUNT(*) as trees",
                    "$group":  "nta,boroname",
                    "$where":  "nta IS NOT NULL",
                    "$limit":  "500"},
        )
        df15 = pd.DataFrame(r.json())
        df15 = df15.rename(columns={"nta": "nta_code", "boroname": "boro_name"})
        df15["trees_2015"] = pd.to_numeric(df15["trees"], errors="coerce").fillna(0).astype(int)
        df15 = df15[["nta_code", "trees_2015"]]
        print(f"   ✓ {df15['trees_2015'].sum():,.0f} trees · {len(df15)} NTAs")

        print("📡 Fetching 2005 tree census from NYC Open Data…")
        r = _fetch(
            "https://data.cityofnewyork.us/resource/29bw-z7pj.json",
            params={"$select": "nta_name,boroname,COUNT(*) as trees",
                    "$group":  "nta_name,boroname",
                    "$where":  "nta_name IS NOT NULL",
                    "$limit":  "500"},
        )
        df05 = pd.DataFrame(r.json())
        df05["trees_2005"] = pd.to_numeric(df05["trees"], errors="coerce").fillna(0).astype(int)
        df05 = df05[["nta_name", "trees_2005"]]
        print(f"   ✓ {df05['trees_2005'].sum():,.0f} trees · {len(df05)} NTAs")

        print("📡 Fetching 2010 census tract boundaries from US Census Bureau…")
        gdf_tracts = gpd.read_file(
            "https://www2.census.gov/geo/tiger/GENZ2010/gz_2010_36_140_00_500k.zip"
        )
        gdf_tracts = gdf_tracts.to_crs("EPSG:4326")
        nyc_counties = {"005", "047", "061", "081", "085"}
        gdf_tracts = gdf_tracts[
            gdf_tracts["COUNTY"].astype(str).str.zfill(3).isin(nyc_counties)
        ].copy()
        gdf_tracts["COUNTY"] = gdf_tracts["COUNTY"].astype(str).str.zfill(3)
        gdf_tracts["TRACT"]  = gdf_tracts["TRACT"].astype(str).str.zfill(6)
        print(f"   ✓ {len(gdf_tracts)} NYC census tracts loaded")

        print("📡 Fetching NTA crosswalk from NYC Open Data…")
        r = _fetch(
            "https://data.cityofnewyork.us/resource/8ius-dhrr.json",
            params={"$limit": "3000"},
        )
        xwalk = pd.DataFrame(r.json()).rename(columns={
            "_2010_census_tract":                    "TRACT",
            "_2010_census_bureau_fips_county_code":  "COUNTY",
            "neighborhood_tabulation_area_nta_code": "nta_code",
            "neighborhood_tabulation_area_nta_name": "nta_name",
            "borough":                               "boro_name",
        })
        xwalk["COUNTY"] = xwalk["COUNTY"].astype(str).str.zfill(3)
        xwalk["TRACT"]  = xwalk["TRACT"].astype(str).str.zfill(6)
        xwalk = xwalk[["TRACT","COUNTY","nta_code","nta_name","boro_name"]].drop_duplicates()
        print(f"   ✓ {len(xwalk)} crosswalk rows · {xwalk['nta_code'].nunique()} NTAs")

        gdf_with_nta = gdf_tracts.merge(xwalk, on=["TRACT","COUNTY"], how="left")
        gdf_with_nta = gdf_with_nta.dropna(subset=["nta_code"])
        gdf_boundaries = gdf_with_nta.dissolve(by="nta_code", aggfunc="first").reset_index()
        gdf_boundaries = gdf_boundaries.set_crs("EPSG:4326", allow_override=True)
        print(f"   ✓ {len(gdf_boundaries)} NTA polygons assembled")

        # Merge tree counts onto real boundary polygons
        # 2015: join on NTA code (e.g. "BX31") — direct match
        merged = gdf_boundaries.merge(df15, on="nta_code", how="left")
        # 2005: join on NTA name — best available key in the 2005 dataset
        merged = merged.merge(df05, on="nta_name", how="left")
        merged["trees_2015"] = merged["trees_2015"].fillna(0).astype(int)
        merged["trees_2005"] = merged["trees_2005"].fillna(0).astype(int)

        # Real area from polygon geometry (project to metres first)
        merged["area_km2"] = (
            merged.to_crs("EPSG:3857").geometry.area / 1e6
        ).round(2).clip(lower=0.1)

        # Income from embedded lookup (not present in tree census)
        merged["median_income"] = (
            merged["nta_code"].map(_INCOME_BY_CODE)
            .fillna(merged["nta_name"].map(_INCOME_BY_NAME))
            .fillna(_DEFAULT_INCOME)
            .astype(int)
        )

        # Centroid lat/lon for circle markers
        cents = merged.to_crs("EPSG:4326").geometry.centroid
        merged["lat"] = cents.y.round(4)
        merged["lon"] = cents.x.round(4)

        merged = gpd.GeoDataFrame(merged, geometry="geometry", crs="EPSG:4326")
        live_ok = True

        print(f"\n✅ Live data loaded — {len(merged)} NTAs · "
              f"{int(merged['trees_2015'].sum()):,} trees (2015) · "
              f"{int(merged['trees_2005'].sum()):,} trees (2005)")

    except Exception as exc:
        import traceback
        print(f"\n⚠  Live data unavailable: {exc}")
        traceback.print_exc()
        print("   Falling back to embedded dataset…")

# ── Embedded fallback ─────────────────────────────────────────────────────
if not live_ok:
    if not LIVE_DATA:
        print("\n📦 Using embedded census dataset (set LIVE_DATA=True for real API)")

    df_data = pd.DataFrame(NTA_RECORDS, columns=_COLS)
    print(f"   ✓  {df_data['trees_2015'].sum():,} trees  ·  {len(df_data)} NTAs  (embedded)")


# ════════════════════════════════════════════════════════════════
# 2.  PREPARE GEOMETRIES
#     Live mode  → real NTA polygons from the API (already in `merged`)
#     Embedded   → approximate hexagons generated from centroid + area
# ════════════════════════════════════════════════════════════════

def hex_polygon(lat, lon, area_km2):
    """Return a hexagonal Shapely polygon approximating the NTA area."""
    r_lat = (area_km2 / (1.5 * np.sqrt(3))) ** 0.5 / 111.0
    r_lon = r_lat / np.cos(np.radians(lat))
    angles = np.linspace(0, 2 * np.pi, 7)[:-1]
    pts = [(lon + r_lon * np.sin(a), lat + r_lat * np.cos(a)) for a in angles]
    return Polygon(pts)


if not live_ok:
    df_data["geometry"] = df_data.apply(
        lambda r: hex_polygon(r.lat, r.lon, r.area_km2), axis=1
    )
    merged = gpd.GeoDataFrame(df_data, geometry="geometry", crs="EPSG:4326")


# ════════════════════════════════════════════════════════════════
# 2b. AIR QUALITY (PM2.5)
#     Fetched independently — failure here never blocks the map.
#     NaN is kept for unmatched NTAs; median fill is used only
#     inside the underserved normalisation in Section 3.
# ════════════════════════════════════════════════════════════════

merged["pm25"] = np.nan   # default; overwritten below if fetch succeeds

if LIVE_DATA:
    try:
        import requests, re
        print("\n📡 Fetching air quality (PM2.5) from NYC Open Data…")
        # PM2.5 NTA-level data is not in this dataset; finest available is UHF42
        # (42 United Hospital Fund health districts). We match NTA names to UHF42
        # areas by token overlap then assign the UHF42-level PM2.5 value.
        r = _fetch(
            "https://data.cityofnewyork.us/resource/c3uy-2p5r.json",
            params={
                "$where": ("name='Fine particles (PM 2.5)' AND geo_type_name='UHF42'"
                           " AND time_period LIKE 'Annual%'"),
                "$limit": "500",
            },
        )
        aq = pd.DataFrame(r.json())
        aq["data_value"] = pd.to_numeric(aq["data_value"], errors="coerce")
        aq = aq.dropna(subset=["data_value", "geo_place_name"])

        # Most recent annual average year
        aq["_yr"] = pd.to_datetime(aq["start_date"], errors="coerce").dt.year
        latest_yr = int(aq["_yr"].max())
        aq = aq[aq["_yr"] == latest_yr].copy()
        print(f"   ✓ {len(aq)} UHF42 PM2.5 annual readings · year {latest_yr}")

        # Build lowercase name → value lookup
        uhf_map = {row["geo_place_name"].lower().strip(): float(row["data_value"])
                   for _, row in aq.iterrows()}

        # Match NTA name to best-fitting UHF42 area by token overlap
        def _match_uhf(nta_name):
            key = nta_name.lower().strip()
            if key in uhf_map:
                return uhf_map[key]
            tokens = set(re.split(r"[\s\-–,()]+", key)) - {"the","and","or","of","etc",""}
            best_val, best_score = None, 0.0
            for uhf_name, val in uhf_map.items():
                uhf_tok = set(re.split(r"[\s\-–,()]+", uhf_name)) - {"the","and","or","of",""}
                ov = len(tokens & uhf_tok)
                if ov > 0:
                    score = ov / max(len(tokens), 1)
                    if score > best_score:
                        best_score, best_val = score, val
            return best_val if best_score >= 0.30 else None

        merged["pm25"] = merged["nta_name"].apply(_match_uhf).round(2)
        matched = merged["pm25"].notna().sum()
        print(f"   ✓ PM2.5 matched to {matched} / {len(merged)} NTAs (UHF42 granularity)")

    except Exception as exc:
        import traceback
        print(f"\n⚠  PM2.5 data unavailable: {exc}")
        traceback.print_exc()


# ════════════════════════════════════════════════════════════════
# 3.  DERIVED METRICS
# ════════════════════════════════════════════════════════════════

merged["trees_2015"]   = pd.to_numeric(merged.get("trees_2015", merged.get("trees",0)), errors="coerce").fillna(0)
merged["trees_2005"]   = pd.to_numeric(merged.get("trees_2005", 0), errors="coerce").fillna(0)
merged["area_km2"]     = pd.to_numeric(merged["area_km2"], errors="coerce").fillna(1)
merged["median_income"]= pd.to_numeric(merged["median_income"], errors="coerce")

merged["density_2015"] = (merged["trees_2015"] / merged["area_km2"]).round(1)
merged["density_2005"] = (merged["trees_2005"] / merged["area_km2"]).round(1)
merged["tree_change"]  = (merged["trees_2015"] - merged["trees_2005"]).astype(int)
merged["pct_change"]   = ((merged["tree_change"] / merged["trees_2005"].replace(0, np.nan)) * 100).round(1)
merged["median_income"]= merged["median_income"].fillna(merged["median_income"].median())

# Normalise 0–1
def norm01(s):
    lo, hi = s.min(), s.max()
    return (s - lo) / (hi - lo + 1e-9)

merged["inc_norm"]    = norm01(merged["median_income"])
merged["den_norm"]    = norm01(merged["density_2015"])
merged["heat_proxy"]  = (1 - merged["den_norm"] * 0.6 - merged["inc_norm"] * 0.4).round(3)

# PM2.5: fill NaN with median for normalisation (keeps every NTA in the index)
_pm25_fill       = merged["pm25"].fillna(merged["pm25"].median() if merged["pm25"].notna().any() else 8.0)
merged["pm25_norm"] = norm01(_pm25_fill)

# Composite underserved index — low density + low income + high PM2.5 = most underserved
merged["underserved"] = (
    0.40 * (1 - merged["den_norm"]) +
    0.35 * (1 - merged["inc_norm"]) +
    0.25 * merged["pm25_norm"]
).round(3)

# Bucket for labelling
def bucket(val, labels=("Well-Served","Adequate","Needs Attention","Underserved","Critical")):
    breaks = [0, 0.30, 0.50, 0.65, 0.80, 1.01]
    for i in range(len(breaks)-1):
        if breaks[i] <= val < breaks[i+1]:
            return labels[i]
    return labels[-1]

merged["equity_label"] = merged["underserved"].apply(bucket)

# ════════════════════════════════════════════════════════════════
# 4.  CONSOLE REPORT
# ════════════════════════════════════════════════════════════════

print("\n" + "─" * 65)
print("  BOROUGH SUMMARY (2015)")
print("─" * 65)
bsumm = (merged.groupby("boro_name")
         .agg(Total_Trees=("trees_2015","sum"),
              Avg_Density =("density_2015","mean"),
              Avg_Income  =("median_income","mean"),
              NTAs        =("nta_code","count"))
         .round(0).sort_values("Avg_Density", ascending=False))
print(bsumm.to_string())

print("\n" + "─" * 65)
print("  TOP 10 MOST UNDERSERVED NTAs")
print("─" * 65)
top10 = (merged.nlargest(10, "underserved")
         [["nta_name","boro_name","density_2015","median_income","underserved","equity_label"]]
         .reset_index(drop=True))
top10.index += 1
print(top10.to_string())

print("\n" + "─" * 65)
print("  TREE CHANGE 2005→2015  (biggest losers)")
print("─" * 65)
losers = (merged.nsmallest(8,"tree_change")
          [["nta_name","boro_name","trees_2005","trees_2015","tree_change","pct_change"]]
          .reset_index(drop=True))
print(losers.to_string())

if merged["pm25"].notna().any():
    print("\n" + "─" * 65)
    print("  TOP 5 MOST POLLUTED NTAs (PM2.5 μg/m³)")
    print("─" * 65)
    pm25_top = (merged.dropna(subset=["pm25"])
                .nlargest(5, "pm25")
                [["nta_name", "boro_name", "pm25"]]
                .reset_index(drop=True))
    pm25_top.index += 1
    print(pm25_top.to_string())


# ════════════════════════════════════════════════════════════════
# 5.  FOLIUM MAP
# ════════════════════════════════════════════════════════════════

print("\n" + "─" * 65)
print("  BUILDING INTERACTIVE FOLIUM MAP …")
print("─" * 65)

# ── Convert to WGS-84 for Folium ────────────────────────────────
gdf_wgs = merged.to_crs("EPSG:4326") if merged.crs else merged

# ── Colour maps ─────────────────────────────────────────────────
DENSITY_CM = LinearColormap(
    ["#071a0e","#0d4021","#1a6b3c","#2fa05e","#5cc98a","#a8e6bf"],
    vmin=0, vmax=float(merged["density_2015"].quantile(0.92)),
    caption="Tree Density (trees / km²)",
)
INCOME_CM = LinearColormap(
    ["#1a0533","#52155b","#9c3587","#d968b0","#f3b8db","#fce8f3"],
    vmin=float(merged["median_income"].quantile(0.05)),
    vmax=float(merged["median_income"].quantile(0.95)),
    caption="Median Household Income ($)",
)
UNDERSERVED_CM = LinearColormap(
    ["#003f5c","#2c7fa6","#f5b800","#d94f00","#6d0000"],
    vmin=0, vmax=1,
    caption="Underserved Index (0=well-served → 1=critical)",
)
CHANGE_CM = LinearColormap(
    ["#7b0000","#d03000","#f7f7f7","#3aaa5c","#005c2a"],
    vmin=float(merged["tree_change"].quantile(0.05)),
    vmax=float(merged["tree_change"].quantile(0.95)),
    caption="Tree Count Change (2005 → 2015)",
)
HEAT_CM = LinearColormap(
    ["#fff5f0","#fcbba1","#fb6a4a","#cb181d","#67000d"],
    vmin=0, vmax=1,
    caption="Urban Heat Vulnerability (estimated)",
)
PM25_CM = LinearColormap(
    ["#00441b","#1b7837","#f7f7f7","#d6604d","#67001f"],
    vmin=5.0, vmax=12.0,
    caption="PM2.5 (μg/m³) — Annual Mean",
)

# ── Map object ───────────────────────────────────────────────────
m = folium.Map(
    location=[40.7128, -74.0060],
    zoom_start=11,
    tiles=None,
    control_scale=True,
)

folium.TileLayer("CartoDB dark_matter",  name="Dark (default)", show=True).add_to(m)
folium.TileLayer("CartoDB positron",     name="Light").add_to(m)
folium.TileLayer("OpenStreetMap",        name="Street Map").add_to(m)

# ── GeoJson layer factory ────────────────────────────────────────
EQUITY_COLORS = {
    "Well-Served":     "#2fa05e",
    "Adequate":        "#a8e6bf",
    "Needs Attention": "#f5b800",
    "Underserved":     "#d94f00",
    "Critical":        "#6d0000",
}

def make_layer(value_col, colormap, layer_name, show=False):
    fg = folium.FeatureGroup(name=layer_name, show=show)

    def style(feat):
        val = feat["properties"].get(value_col) or 0
        try:    color = colormap(float(val))
        except: color = "#444"
        return {"fillColor": color, "color": "#ffffff",
                "weight": 0.5, "fillOpacity": 0.80}

    def highlight(feat):
        return {"weight": 2.5, "color": "#ffffcc", "fillOpacity": 0.95}

    GeoJson(
        data=gdf_wgs.__geo_interface__,
        style_function=style,
        highlight_function=highlight,
    ).add_to(fg)
    return fg

# ── Add all layers ───────────────────────────────────────────────
make_layer("density_2015", DENSITY_CM,    "🌳 Tree Density (2015)",           show=True ).add_to(m)
make_layer("median_income",INCOME_CM,     "💵 Median Household Income",        show=False).add_to(m)
make_layer("underserved",  UNDERSERVED_CM,"🔴 Underserved Index",              show=False).add_to(m)
make_layer("tree_change",  CHANGE_CM,     "📈 Tree Change 2005→2015",          show=False).add_to(m)
make_layer("heat_proxy",   HEAT_CM,       "🌡 Urban Heat Vulnerability",       show=False).add_to(m)
make_layer("pm25",         PM25_CM,       "💨 Air Quality (PM2.5)",            show=False).add_to(m)

# ── Underserved markers (critical NTAs) ──────────────────────────
critical_fg = folium.FeatureGroup(name="🚨 Critical NTAs (top 15)", show=True)
top15 = merged.nlargest(15, "underserved")
for _, row in top15.iterrows():
    try:
        lat_, lon_ = float(row["lat"]), float(row["lon"])
    except Exception:
        continue

    folium.CircleMarker(
        location=[lat_, lon_],
        radius=8,
        color="#ff3300",
        weight=2,
        fill=True,
        fill_color="#ff6600",
        fill_opacity=0.85,
        tooltip=f"⚠ {row['nta_name']} ({row['boro_name']})\n"
                f"Underserved: {row['underserved']:.2f}  |  "
                f"Density: {row['density_2015']:.0f} trees/km²  |  "
                f"Income: ${int(row['median_income']):,}",
    ).add_to(critical_fg)
critical_fg.add_to(m)

# ── Tree density heatmap (centroid-based) ────────────────────────
heat_fg = folium.FeatureGroup(name="🔥 Density Heatmap", show=False)
heat_pts = []
for _, row in merged.iterrows():
    try:
        lat_ = float(row["lat"])
        lon_ = float(row["lon"])
        weight = min(float(row["density_2015"]) / 1500, 1.0)
        heat_pts.append([lat_, lon_, weight])
    except Exception:
        continue
HeatMap(heat_pts, min_opacity=0.3, radius=25, blur=20,
        gradient={"0.3":"#052e16","0.6":"#15803d","0.85":"#86efac","1.0":"#ffffff"}
        ).add_to(heat_fg)
heat_fg.add_to(m)

# ── Layer control ────────────────────────────────────────────────
LayerControl(collapsed=False, position="topright").add_to(m)

# ── Custom legend panel + universal tooltip (injected HTML) ─────
_TOOLTIP_JS = """
(function(){
  var EQ={'Well-Served':'#2fa05e','Adequate':'#a8e6bf',
          'Needs Attention':'#f5b800','Underserved':'#d94f00','Critical':'#6d0000'};

  function buildTooltipHTML(p){
    var name=window.__activeLayerName||'';
    var html='<div style="font-family:DM Sans,sans-serif;min-width:155px">'
      +'<b style="font-size:13px;color:#e8f0e8;display:block;margin-bottom:5px">'
      +(p.nta_name||'')+'</b>';
    if(name.indexOf('Tree Density')>=0){
      var dens=Math.round(parseFloat(p.density_2015)||0).toLocaleString();
      html+='<div style="color:#b0cbb0;font-size:11px;margin-bottom:4px">🌳 '+dens+' trees/km²</div>'
           +'<span style="background:'+(EQ[p.equity_label]||'#888')
           +';color:#fff;padding:2px 8px;border-radius:3px;font-size:10px">'
           +(p.equity_label||'')+'</span>';
    }else if(name.indexOf('Income')>=0){
      var inc=parseInt(p.median_income)||0;
      var sc=inc>=63000?'#2fa05e':'#d94f00';
      html+='<div style="color:#b0cbb0;font-size:11px;margin-bottom:4px">💵 $'
           +inc.toLocaleString()+' median income</div>'
           +'<span style="color:'+sc+';font-size:10px">'
           +(inc>=63000?'↑ above NYC avg':'↓ below NYC avg')+'</span>';
    }else if(name.indexOf('Underserved')>=0){
      var score=(parseFloat(p.underserved)||0).toFixed(2);
      html+='<div style="color:#b0cbb0;font-size:11px;margin-bottom:4px">🔴 Underserved Score: '+score+'</div>'
           +'<span style="background:'+(EQ[p.equity_label]||'#888')
           +';color:#fff;padding:2px 8px;border-radius:3px;font-size:10px">'
           +(p.equity_label||'')+'</span>';
    }else if(name.indexOf('Change')>=0){
      var chg=parseInt(p.tree_change)||0;
      var cc=chg>=0?'#2fa05e':'#d94f00';
      html+='<div style="color:'+cc+';font-size:11px">'
           +(chg>=0?'📈 +':'📉 ')
           +Math.abs(chg).toLocaleString()+' trees since 2005</div>';
    }else if(name.indexOf('Heat')>=0){
      var heat=parseFloat(p.heat_proxy)||0;
      var hl=heat>=0.75?'Critical':heat>=0.55?'High':heat>=0.35?'Moderate':'Low';
      var hc=heat>=0.75?'#c0392b':heat>=0.55?'#d94f00':heat>=0.35?'#f5b800':'#2fa05e';
      html+='<div style="color:#b0cbb0;font-size:11px;margin-bottom:4px">🌡 Heat Risk: '+heat.toFixed(3)+'</div>'
           +'<span style="color:'+hc+';font-size:10px">'+hl+'</span>';
    }else if(name.indexOf('Air')>=0||name.indexOf('PM')>=0){
      var pm=parseFloat(p.pm25)||0;
      if(pm>0){
        var pml=pm<8?'Clean':pm<10?'Moderate':pm<12?'Poor':'Hazardous';
        var pmc=pm<8?'#2fa05e':pm<10?'#f5b800':'#c0392b';
        html+='<div style="color:#b0cbb0;font-size:11px;margin-bottom:4px">💨 PM2.5: '
             +pm.toFixed(1)+' μg/m³</div>'
             +'<span style="color:'+pmc+';font-size:10px">'+pml+'</span>';
      }else{
        html+='<div style="color:#b0cbb0;font-size:11px">💨 PM2.5: N/A</div>';
      }
    }else{
      html+='<span style="background:'+(EQ[p.equity_label]||'#888')
           +';color:#fff;padding:2px 8px;border-radius:3px;font-size:10px">'
           +(p.equity_label||'')+'</span>';
    }
    return html+'</div>';
  }

  // Start with the default-visible layer name
  window.__activeLayerName = '🌳 Tree Density (2015)';
  var tip = document.getElementById('custom-tooltip');

  // Attach mouseover / mousemove / mouseout / click to every GeoJSON feature
  var _attached = {};
  function attachEvents(layer){
    if(!layer||!layer.eachLayer) return;
    layer.eachLayer(function(sub){
      if(sub.feature&&sub.feature.properties){
        var lid = L.stamp(sub);
        if(!_attached[lid]){
          _attached[lid] = true;
          sub.on('mouseover', function(e){
            tip.innerHTML = buildTooltipHTML(e.target.feature.properties);
            tip.style.display = 'block';
          });
          sub.on('mousemove', function(e){
            tip.style.left = (e.originalEvent.clientX + 15) + 'px';
            tip.style.top  = (e.originalEvent.clientY - 10) + 'px';
          });
          sub.on('mouseout', function(){
            tip.style.display = 'none';
          });
          sub.on('click', function(e){
            window.parent.postMessage(
              {type:'nta_click', props:e.target.feature.properties}, '*');
          });
        }
      }
      attachEvents(sub);
    });
  }

  // Update active layer name when parent dashboard switches layers
  window.addEventListener('message', function(msg){
    if(!msg||!msg.data) return;
    if(msg.data.type==='toggle_layer'&&msg.data.show)
      window.__activeLayerName = msg.data.name;
  });

  // Poll until Leaflet map is ready
  var t = setInterval(function(){
    for(var k in window){
      try{
        var v = window[k];
        if(v&&typeof v==='object'&&v.getZoom&&v.eachLayer){
          clearInterval(t);
          // Attach to all layers already on the map
          v.eachLayer(function(l){ if(l.eachLayer) attachEvents(l); });
          // Also update active layer name when user manually checks LayerControl
          v.on('overlayadd', function(e){
            window.__activeLayerName = e.name;
            attachEvents(e.layer);
          });
          return;
        }
      }catch(e){}
    }
  }, 200);
})();
"""

title_html = (
    "<style>"
    "@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@500&family=DM+Sans:wght@400;600&display=swap');"
    ".eql{position:fixed;bottom:28px;left:54px;z-index:9999;background:rgba(8,12,8,0.88);"
    "border:1px solid #222;padding:8px 10px;border-radius:4px;box-shadow:0 2px 12px rgba(0,0,0,0.4)}"
    ".eql h4{margin:0 0 5px;font-size:9px;color:#5a7a5a;text-transform:uppercase;letter-spacing:1px;font-family:'DM Sans',sans-serif}"
    ".eql .er{display:flex;align-items:center;gap:6px;margin:2px 0}"
    ".eql .dt{width:9px;height:9px;border-radius:50%;flex-shrink:0}"
    ".eql span{font-size:10px;color:#b0c8b0;font-family:'DM Sans',sans-serif}"
    "</style>"
    "<div id='custom-tooltip' style='"
    "position:fixed;background:#0d1117;color:#cce0cc;padding:8px 12px;"
    "border-radius:4px;font-family:DM Sans,sans-serif;font-size:12px;"
    "pointer-events:none;z-index:99999;border:1px solid #2fa05e;"
    "display:none;max-width:240px;line-height:1.5;"
    "'></div>"
    "<div class='eql'><h4>Equity Status</h4>"
    "<div class='er'><div class='dt' style='background:#2fa05e'></div><span>Well-Served</span></div>"
    "<div class='er'><div class='dt' style='background:#a8e6bf'></div><span>Adequate</span></div>"
    "<div class='er'><div class='dt' style='background:#f5b800'></div><span>Needs Attention</span></div>"
    "<div class='er'><div class='dt' style='background:#d94f00'></div><span>Underserved</span></div>"
    "<div class='er'><div class='dt' style='background:#6d0000'></div><span>Critical</span></div>"
    "</div>"
    "<script>" + _TOOLTIP_JS + "</script>"
)
m.get_root().html.add_child(Element(title_html))

# ── Save ─────────────────────────────────────────────────────────
m.save(OUTPUT_HTML)
print(f"\n✅  Map saved → {OUTPUT_HTML}")
print(f"    Open in any browser for the interactive map.")
if not live_ok:
    print(f"\n📌  DATA NOTE: Using embedded dataset.")
    print(f"    Set LIVE_DATA=True to pull live from NYC Open Data.")
