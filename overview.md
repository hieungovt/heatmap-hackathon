## Project overview

This repository currently contains a single healthcare facility dataset intended for exploratory analysis and visualization (for example, building a geographic heatmap for a hackathon project).

- **Main data file**: `data/NIRD 20230130 Database_Hackathon.csv`
  - **Content**: A table of hospitals and medical centers across the United States, with emphasis on trauma and burn capabilities.
  - **Each row**: One facility (hospital or medical center).

### Key columns

- **Location & identity**
  - `STATE_FULL`, `STATE`, `COUNTY`, `CITY`, `ADDRESS`, `ZIP_CODE`
  - `HOSPITAL_NAME`, `AHA_ID`, `PHONE`

- **Capacity**
  - `TOTAL_BEDS`, `BURN_BEDS`

- **Trauma & burn designations**
  - `TRAUMA_ADULT`, `TRAUMA_PEDS`
  - `BURN_ADULT`, `BURN_PEDS`
  - `ACS_VERIFIED`, `ABA_VERIFIED`
  - `ADULT_TRAUMA_L1`, `ADULT_TRAUMA_L2`, `PEDS_TRAUMA_L1`, `PEDS_TRAUMA_L2`
  - `TC_STATE_DESIGNATED`, `BC_STATE_DESIGNATED`

### Possible uses

- **Mapping & heatmaps**
  - Visualize hospital, trauma center, and burn center density by state, county, or ZIP code.
  - Create capacity-based heatmaps using `TOTAL_BEDS` and `BURN_BEDS`.

- **Access & coverage analysis**
  - Identify regions with limited access to adult or pediatric trauma care.
  - Compare ACS/ABA-verified facilities to state-designated centers.

### Environment configuration

- **Cursor configuration**: `.cursor/settings.json` currently only enables the `superpowers` plugin and does not define additional editor or project-specific behavior.
