# Datasets to Add Manually

The following datasets would significantly enrich the HeatMap Hackathon reports but are **not available via public API** and must be acquired manually through interactive portals, formal data requests, or direct downloads.

---

## 1. Burn Injury Incidence by State

### Why It Matters
State-level burn injury counts and rates would allow us to calculate **burn demand vs burn supply** — i.e., how many burn injuries occur per state relative to the state's burn centre capacity. This is the missing denominator for the equitable access analysis: currently we measure supply (beds, centres) but not demand (injuries).

### Recommended Sources

#### Option A: CDC WISQARS Nonfatal Injury Data (Preferred)
- **URL**: https://wisqars.cdc.gov/nonfatal
- **How to get it**:
  1. Go to the WISQARS Interactive Query Tool
  2. Select "Nonfatal Injury Reports" → "Nonfatal Injury Data"
  3. Set Intent = "All Intents"
  4. Set Mechanism/Cause = "Fire/Burn"
  5. Set Year = most recent available (2021 or 2022)
  6. Group by = "State"
  7. Click "Submit" then "Download Data CSV"
- **Expected fields**: State, Number of injuries, Population, Crude rate per 100,000, Age-adjusted rate
- **Save as**: `data/external/wisqars_burn_injuries_by_state.csv`

#### Option B: CDC WISQARS Fatal Injury Data
- **URL**: https://wisqars.cdc.gov/fatal
- **How to get it**:
  1. Select "Fatal Injury Reports" → "Fatal Injury Data"
  2. Cause of Death = "Fire/Burn"
  3. Year = most recent
  4. Group by = "State"
  5. Download CSV
- **Expected fields**: State, Deaths, Population, Crude rate, Age-adjusted rate
- **Save as**: `data/external/wisqars_burn_deaths_by_state.csv`

#### Option C: ABA Burn Injury Summary Report (BISR)
- **URL**: https://ameriburn.org/quality-care/burn-care-quality-platform/
- **How to get it**: Request data access from ABA's BCQP program. Available to academic researchers, non-profit orgs, public health professionals. The 2024 BISR has regional breakdowns with data from burn centres in 38 states.
- **Expected fields**: State/region, admissions, demographics, injury severity, outcomes
- **Save as**: `data/external/aba_bisr_burn_admissions.csv`

#### Option D: Burn Model System (BMS) National Database
- **URL**: https://www.openicpsr.org (search "Burn Model System")
- **How to get it**: Download the public access dataset (annually updated, 1994-2024). Contains moderate-to-severe burn injury data with state identifiers.
- **Save as**: `data/external/bms_national_burn_data.csv`

---

## 2. Fire Department / EMS Response Time Data by State

### Why It Matters
Response time data would enable analysis of how quickly burn patients reach initial care, complementing the transfer distance analysis in the referral networks report.

### Recommended Source
- **NFIRS (National Fire Incident Reporting System)**
- **URL**: https://www.usfa.fema.gov/nfirs/
- **How to get it**: Download or request from USFA/FEMA. Contains fire incident records with response times.
- **Save as**: `data/external/nfirs_response_times_by_state.csv`

---

## How to Integrate Once Acquired

After downloading the datasets, place them in `data/external/` and update:
1. `src/challenge_pipeline.py` — add a new function to load and join the burn injury data
2. `scripts/generate_narrative_figures.py` — add demand-vs-supply visualisation
3. Reports — add "Burn Injury Demand Analysis" section

The pipeline is designed to be modular; each new data source is loaded in its own function and joined to the state-level metrics table.
