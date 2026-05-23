# 🌳 Environmental Equity in NYC

[![Live Site](https://img.shields.io/badge/Live%20Site-View%20Map-2fa05e?style=for-the-badge)](https://j3ssc0des.github.io/Enviromental-Equity-In-NYC)
[![Data](https://img.shields.io/badge/Data-NYC%20Open%20Data-blue?style=for-the-badge)](https://opendata.cityofnewyork.us)

An interactive map exploring green space inequity across NYC neighborhoods using the 2005 & 2015 Street Tree Census — analyzing the relationship between tree density, household income, and urban heat vulnerability.

## 🗺 [View the Live Map →](https://j3ssc0des.github.io/Enviromental-Equity-In-NYC)

## About

Every decade, NYC Parks counts every street tree in the city. The data tells a story that goes beyond parks and sidewalks — neighborhoods with fewer trees are hotter in summer, have worse air quality, and tend to have lower median incomes.

This project analyzes two census snapshots (2005 and 2015) to quantify that inequity at the neighborhood level. Using an underserved index that weights both tree density and household income, it identifies the neighborhoods most in need of green infrastructure investment — from Hunts Point and Mott Haven in the Bronx to East New York and Brownsville in Brooklyn. The 2025 census is currently underway — this map will be updated when results are published.

## Map Layers

| Layer | Description |
|---|---|
| 🌳 Tree Density | Trees per km² by neighborhood (2015) |
| 💵 Median Income | Household income by neighborhood |
| 🔴 Underserved Index | Low density + low income combined score |
| 📈 Canopy Change | Tree count change from 2005 to 2015 |
| 🌡 Heat Vulnerability | Estimated urban heat risk |

## Data Sources

- [NYC Street Tree Census 2015](https://data.cityofnewyork.us/resource/uvpi-gqnh)
- [NYC Street Tree Census 2005](https://data.cityofnewyork.us/resource/29bw-z7pj)
- [NYC Neighborhood Tabulation Areas](https://data.cityofnewyork.us/api/geospatial/d3qk-6yt9)

## Built With

Python · Pandas · GeoPandas · Folium · GitHub Pages · GitHub Actions
