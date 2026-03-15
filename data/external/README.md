## External datasets used

### 1) US state population (2012 total population)

- **Source files downloaded**
  - `state_population_raw.csv` from `https://raw.githubusercontent.com/jakevdp/data-USstates/master/state-population.csv`
  - `state_abbrevs.csv` from `https://raw.githubusercontent.com/jakevdp/data-USstates/master/state-abbrevs.csv`
- **Derived file**
  - `state_population_2012.csv`
- **Transformation**
  - Filter `ages == "total"` and `year == 2012`.
  - Join to state abbreviations.
  - Keep `STATE` and `population`.

### Why this was added

The main hospital dataset does not include denominator population fields. This external dataset enables per-capita metrics such as:

- `total_beds_per_100k`
- `burn_beds_per_100k`

These are required for equitable access analysis and judge-form alignment.

### 2) Rural-Urban Continuum Codes (RUCC) 2023

- **Source file downloaded**
  - `rucc_2023_county.csv` from `https://ers.usda.gov/sites/default/files/_laserfiche/DataFiles/53251/Ruralurbancontinuumcodes2023.csv`
- **Usage**
  - Build state-level `rural_county_share` as an equity and telemedicine readiness feature.

### 3) ACS 2022 Broadband Subscription (state-level)

- **Source**
  - US Census API endpoint:
    - `https://api.census.gov/data/2022/acs/acs1/profile?get=NAME,DP02_0154PE&for=state:*`
- **Derived file**
  - `state_broadband_acs2022.csv`
- **Usage**
  - Broadband adoption proxy for telemedicine feasibility.

### 4) US State Boundaries (Census cartographic shapefile)

- **Source file downloaded**
  - `cb_2023_us_state_20m.zip` from `https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_state_20m.zip`
- **Usage**
  - State centroid distance estimates for referral network routing recommendations.
