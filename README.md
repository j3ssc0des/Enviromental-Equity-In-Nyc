# NYC Green Space Inequity — Street Tree Census Analysis

Mapping green space inequity across NYC neighborhoods using the 2005 & 2015 
Street Tree Census — analyzing the relationship between tree density, household 
income, and urban heat vulnerability.

## Overview

Every decade, NYC Parks counts every street tree in the city. The data tells a 
story that goes beyond parks and sidewalks — neighborhoods with fewer trees are 
hotter in summer, have worse air quality, and tend to have lower median incomes.

This project analyzes two census snapshots (2005 and 2015) to quantify that 
inequity at the neighborhood level. Using an underserved index that weights both 
tree density and household income, it identifies the NTAs most in need of green 
infrastructure investment — from Hunts Point and Mott Haven in the Bronx to 
East New York and Brownsville in Brooklyn.

## Output

An interactive Folium map with five switchable layers:
- 🌳 Tree density (2015)
- 💵 Median household income
- 🔴 Underserved index
- 📈 Canopy change 2005→2015
- 🌡 Urban heat vulnerability

## Quick Start

Open in GitHub Codespaces, then:

```bash
install-datascience.sh
pip install geopandas folium branca shapely
python3 nyc_trees_analysis.py
```

Right-click `nyc_trees_map.html` → **Open in Browser**.

## Data Sources

- [NYC Street Tree Census 2015](https://data.cityofnewyork.us/resource/uvpi-gqnh)
- [NYC Street Tree Census 2005](https://data.cityofnewyork.us/resource/29bw-z7pj)
- [NYC Neighborhood Tabulation Areas](https://data.cityofnewyork.us/api/geospatial/d3qk-6yt9)
