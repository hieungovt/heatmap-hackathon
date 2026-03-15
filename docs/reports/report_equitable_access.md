# Challenge Area 1: Equitable Access to Trauma and Burn Care

## 1. Understanding the Problem

Trauma and burn injuries are among the most time-sensitive medical emergencies. A patient suffering a severe burn or major traumatic injury requires access to a specialised facility within a narrow treatment window -- often referred to as the "golden hour." If no such facility exists within a reasonable distance, the patient must be transferred, losing precious time and facing elevated risk of morbidity or mortality. The fundamental question of equitable access asks: **is the capacity to treat these patients distributed fairly across the nation, or are some populations structurally disadvantaged by geography and resource concentration?**

This is not merely an academic concern. Communities in states with fewer trauma and burn resources face longer transport times, higher out-of-state transfer rates, and increased strain on the few facilities that do exist. During mass-casualty events or seasonal surges, even modest capacity gaps can become catastrophic. The goal of this analysis is to quantify where those gaps exist, how severe they are, and what can be done about them -- starting from the foundational NIRD dataset and building outward with external population and resilience data.

---

## 2. The NIRD Dataset: What It Contains and What It Reveals

### 2.1 Dataset Overview

The foundation of this analysis is the **ABA/ACS National Inventory of Regional Datasets (NIRD)**, a comprehensive registry of **635 trauma and burn care facilities** across the United States. Each row represents a single facility, and the dataset contains the following critical fields:

| Field | Description |
|-------|-------------|
| `STATE`, `COUNTY`, `CITY` | Geographic identifiers for every facility |
| `TOTAL_BEDS` | Total licensed bed count, ranging from 6 to 1,573 |
| `BURN_BEDS` | Beds specifically dedicated to burn care (0 for most facilities) |
| `TRAUMA_ADULT` / `TRAUMA_PEDS` | Boolean flags for adult and pediatric trauma capability |
| `BURN_ADULT` / `BURN_PEDS` | Boolean flags for adult and pediatric burn capability |
| `ACS_VERIFIED` | Whether the facility holds American College of Surgeons verification |
| `ADULT_TRAUMA_L1` / `L2` | Level I vs Level II adult trauma designation |

This dataset allows us to answer foundational questions about the distribution of care: which states have the most and fewest facilities, where burn capability is absent, and how bed capacity clusters geographically.

### 2.2 Initial Findings from the NIRD Data Alone

The first step in any analysis is to understand the shape and structure of the underlying data. Before joining any external datasets, the NIRD alone reveals striking disparities.

**Facility counts vary dramatically by state.** When we count the number of NIRD-listed facilities per state, the imbalance is immediately visible. States like Texas, California, Illinois, and New York each host dozens of facilities, while smaller or more rural states may have only two or three. This raw count alone signals uneven distribution, though it does not account for population differences.

![Facility count by state](figures/narr_ea_facility_count.png)

**Bed sizes are highly skewed.** Across all 635 facilities, the distribution of total beds is right-skewed: the median facility has roughly 400 beds, but a long tail extends beyond 1,000 beds. A small number of very large academic medical centres (University Hospital at UAB with 1,157 beds, Yale-New Haven with 1,573) dominate their respective states. This concentration of capacity in a few large institutions is a warning sign for systemic resilience: if one or two large facilities in a state become unavailable (due to disaster, pandemic, or closure), the remaining capacity may be inadequate.

![Bed distribution histogram](figures/narr_ea_bed_distribution.png)

**Burn capability is far less common than trauma capability.** Nearly all 635 facilities have some form of trauma designation, but only about 120 have adult burn centre capability. When we look at the top 20 states by total facility count, the gap between blue (trauma) bars and red (burn) bars is dramatic: most facilities are trauma-only. This means that burn patients in many regions must be transferred to a specialised centre, often in another state entirely.

![Trauma vs burn capability](figures/narr_ea_capability_matrix.png)

**Seven states have no adult burn centre at all.** Perhaps the most striking initial finding is the binary one: a pie chart of states with versus without any adult burn centre reveals that approximately 14% of all US states (7 states) have zero burn centre capability. Patients in these states are entirely dependent on out-of-state referrals for specialised burn care.

![Burn gap pie chart](figures/narr_ea_burn_gap_pie.png)

These initial findings from the NIRD data alone establish the case for concern: facility counts, bed capacity, and burn capability are all unevenly distributed. However, raw facility counts do not tell the full story. A state with 50 facilities and 40 million people may have worse per-capita access than a state with 5 facilities and 500,000 people. To answer the "equitable" part of equitable access, we need population data.

---

## 3. Expanding with External Data: Population-Adjusted Analysis

### 3.1 The Approach

The NIRD dataset tells us what exists. To determine whether what exists is *sufficient*, we joined it with the **US Census 2012 State Population Estimates** (`state_population_2012.csv`), which provides the denominator needed for per-capita calculation. The analytical pipeline (`src/challenge_pipeline.py`) performs the following steps:

1. **Aggregate NIRD to state level**: total beds, burn beds, number of adult burn centres, and the bed share of the single largest facility per state.
2. **Join with Census population**: merge on state abbreviation to produce a per-capita denominator.
3. **Calculate key metrics**:
   - **Total beds per 100k population**: total NIRD beds / (state population / 100,000). This is the primary per-capita access metric.
   - **Capacity fragility (%)**: the percentage of a state's total beds held in its single largest facility. If this number is 100%, losing that single facility eliminates all state capacity.
4. **Tier classification**: states are categorised as Critical (<50 beds/100k), Moderate (50-100), or Adequate (>100).

All outputs are saved to `outputs/equitable_access_state_metrics.csv` and can be regenerated deterministically by re-running the pipeline.

### 3.2 What the Enriched Data Reveals

**Per-capita access varies by more than 10 times across states.** Once population is accounted for, the picture shifts considerably. New Mexico, with only one NIRD facility, drops to just 26.7 beds per 100k population -- the lowest in the nation. At the other extreme, the District of Columbia has 303 beds per 100k. Six states fall into the Critical tier, 27 into Moderate, and 18 into Adequate. The ranked bar chart below provides a policy-ready view: any state in red is a candidate for capacity investment.

![Per-capita ranking](figures/narr_ea_percapita_ranked.png)

**Fragility compounds access gaps.** The scatter plot below maps per-capita beds (x-axis) against capacity fragility (y-axis), with bubble size proportional to population and colour indicating the number of burn centres. The lower-right quadrant -- low beds, high fragility -- identifies the most vulnerable states. New Mexico, Rhode Island, and Vermont all have 100% fragility, meaning their entire NIRD capacity sits in a single facility. Delaware appears resource-adequate (139 beds/100k) but 89% of that capacity is in one hospital, creating what we call the **"false adequacy" trap**: these states look well-served by raw numbers but are acutely vulnerable to any single disruption.

![Fragility scatter](figures/narr_ea_fragility_scatter.png)

**Approximately 15.5 million Americans live in Critical-tier states.** Translating the per-capita tiers into population counts reveals the human scale of the problem. The bar chart below quantifies how many people fall into each tier. The ~15.5 million in the Critical tier represent the highest-priority target population for equitable access interventions.

![Population tier exposure](figures/narr_ea_population_tier.png)

**Geographic patterns emerge on the map.** The US choropleth below shades each state by beds per 100k. The South, Pacific Northwest, and parts of the Mountain West are visibly lighter (lower capacity), while the Midwest and Northeast are darker. This geographic view is essential for policy discussions, where stakeholders need to see their state in regional context.

![US access map](figures/narr_ea_us_map.png)

## 4. Burn Fatality Demand Analysis (CDC WISQARS 2023)

### 4.1 The Demand Side: Who Is Dying from Burns, and Where?

The supply-side analysis above measures beds and facilities, but equitable access ultimately depends on whether supply is proportionate to **demand**. With the CDC WISQARS 2023 fatal fire/burn data now integrated, we can answer this directly. In 2023, **4,001 Americans died from fire and burn injuries**, with crude rates ranging from 0.50 per 100k (Utah) to 7.53 per 100k (Hawaii) -- a **fifteen-fold variation** across states.

The ranked bar chart below reveals a stark geographic pattern: the Southeast and Great Plains carry the heaviest burden. Alaska (3.00), Mississippi (2.82), Arkansas (2.67), Oklahoma (2.64), West Virginia (2.49), Alabama (2.27), Tennessee (2.08), Kentucky (2.01), and Kansas (1.97) all exceed the national average of 1.19 per 100k by significant margins. Meanwhile, California (0.60), Colorado (0.60), Massachusetts (0.63), and Utah (0.50) have rates less than half the national average.

![Burn fatality rate ranking](figures/narr_fatal_rate_ranking.png)

### 4.2 Demand vs Supply: The Critical Mismatch

The scatter plot below is the analytical centrepiece of this enrichment: it maps beds per 100k (supply, x-axis) against burn fatality rate (demand proxy, y-axis), with bubble size proportional to total deaths and colour indicating burn centre count. The **upper-left quadrant** -- high demand, low supply -- identifies the most underserved states.

Oklahoma (2.64 deaths/100k, only 37.7 beds/100k), Alaska (3.00 deaths/100k, 52.1 beds/100k), and Mississippi (2.82 deaths/100k, 71.2 beds/100k) all cluster in this critical zone. These states have both elevated burn mortality and below-median capacity. The implication is clear: these populations are dying at higher rates partly because they lack proximate specialised care. Conversely, states in the lower-right quadrant (DC, NE, ND) have high per-capita capacity and very low fatality rates, confirming that supply adequacy correlates with better outcomes.

![Demand vs supply scatter](figures/narr_fatal_demand_supply.png)

**The geographic pattern is visible on the map.** The US choropleth below shades each state by its burn death rate. The Deep South and Appalachia form a contiguous high-burden band, while the West Coast and Northeast are consistently lighter. Hawaii's rate of 7.53 is driven by its concentrated population and the Maui 2023 wildfires, making it an outlier influenced by a single catastrophic event.

![Burn fatality map](figures/narr_fatal_us_map.png)

---


## 5. Cross-Challenge Synthesis

Equitable access is not an isolated problem. The cross-challenge vulnerability heatmap below combines all four dimensions of this project -- access risk, capacity fragility, referral dependency, and telemedicine priority -- into a single normalised view. States that appear red across all columns face compounding healthcare access challenges. New Mexico, Alaska, Oklahoma, and Mississippi consistently rank among the most vulnerable states across every dimension.

![Cross-challenge heatmap](figures/narr_cross_challenge_heatmap.png)

---

## 6. Recommendations and Practical Impact

**For state health agencies in the six Critical-tier states (NM, OK, WA, MD, KY, AK):** prioritise federal grant applications under the HRSA Trauma Systems Program to expand trauma and burn bed capacity. The per-capita metrics in this report provide the quantitative evidence required for competitive grant narratives. Timeline: 6-18 months.

**For states with 100% capacity fragility (NM, RI, VT):** develop redundancy plans immediately. Designate backup facilities for surge scenarios, sign interstate memoranda of understanding with neighbouring states, and conduct tabletop exercises for facility-loss scenarios. Timeline: 3-6 months.

**For payers and quality improvement teams:** embed the per-capita access metric in annual network adequacy reports. States flagged as Critical or Moderate should trigger review of clinical coverage sufficiency. This pipeline is fully reproducible and can be re-run annually with updated data. Timeline: 1-3 months for initial integration.

---

## 7. Data and Reproducibility

| Asset | Path |
|-------|------|
| NIRD dataset | `data/NIRD 20230130 Database_Hackathon.csv` |
| CDC WISQARS Fatal Burn Data (2023) | `data/external/fatal_report_per_state.csv` |
| Census population | `data/external/state_population_2012.csv` |
| Pipeline script | `src/challenge_pipeline.py` |
| Output CSV | `outputs/equitable_access_state_metrics.csv` |
| Figure generation | `scripts/generate_narrative_figures.py` |
| All figures | `docs/figures/narr_ea_*.png`, `docs/figures/narr_fatal_*.png` |

```bash
python src/challenge_pipeline.py               # regenerates CSVs
python scripts/generate_narrative_figures.py    # regenerates all figures
```
