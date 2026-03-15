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

## 5. Infrastructure and Certification Mismatch: Beyond the Burn Centre Label

The previous sections used burn-centre designation (the `BURN_ADULT` / `BURN_PEDS` flags) as the primary measure of capability. This section broadens the lens to the **physical infrastructure** (burn beds, `BURN_BEDS`) and the **certification layer** (ABA-verified, ACS-verified, or state-designated), exposing a deeper and more dangerous layer of inconsistency that the centre-flag analysis alone cannot reveal.

The NIRD contains six overlapping capability indicators for each facility:

| Field | What it means |
|-------|---------------|
| `BURN_BEDS` | Physical beds designated for burn patients (0 for most facilities) |
| `BURN_ADULT` / `BURN_PEDS` | Capability flags (can be set even with no dedicated burn beds) |
| `ABA_VERIFIED` | American Burn Association formal accreditation |
| `BC_STATE_DESIGNATED` | State-level burn-centre designation (lower bar than ABA) |
| `ACS_VERIFIED` | American College of Surgeons trauma verification (not burn-specific) |

Reading these fields jointly produces three alarming patterns.

### 5.1 Burn Bed Infrastructure vs. Certification Status

Of the 635 NIRD facilities, only **136** have any recorded burn beds (`BURN_BEDS > 0`). The chart below breaks this group by verification status:

| Facility Category | Count | Burn Beds Held |
|-------------------|-------|----------------|
| Burn beds **+** ABA/State verified | ~80 | ~1,620 |
| Burn beds but **NOT** ABA or State verified | **~56** | **534** |
| ABA/State verified but **zero** burn beds | **several** | 0 |
| Neither burn beds nor any verification | 499 | 0 |

![Burn bed infrastructure vs certification (donut)](figures/narr_ea_infra_cert_donut.png)

**534 burn beds — roughly 25% of all US burn bed capacity — sit in facilities that hold no ABA accreditation and no state burn-centre designation.** These facilities can receive burn patients (and will, in surge or proximity-driven transfer scenarios), but they operate outside the quality and safety standards that ABA or state verification is designed to ensure. A burned patient routed to one of these facilities may receive care in an unverified environment, with variable staff training, supply protocols, and outcome monitoring.

Conversely, several ABA-recognised facilities show zero recorded burn beds in the NIRD, raising a data-quality concern: either their burn bed count is not reported (a data gap) or they have shed physical capacity since their verification was granted (a latent infrastructure-certification mismatch). In either case, the verification label overestimates those facilities' actual capacity to receive burn patients.

![Verified vs unverified burn beds by state (stacked bar)](figures/narr_ea_unverified_beds_by_state.png)

The stacked bar chart above shows the split state by state. Missouri (81 unverified beds), Texas (76), Tennessee (37), South Carolina (25), Arkansas (10) and others hold substantial unverified burn bed inventories. In Missouri specifically, **87% of all burn beds sit in non-ABA/non-state-designated facilities**, yet the state is not flagged as a burn-access gap because it has burn centres — the mismatch is entirely invisible when looking at centre flags alone.

### 5.2 ACS vs. ABA Certification Inconsistency

The ACS trauma verification and ABA burn accreditation are **parallel, non-interchangeable** credentialling tracks. A hospital can be ACS-verified for trauma and simultaneously hold burn beds without ever having been reviewed for burn-specific competency. This creates a distinct certification gap:

![ACS vs ABA certification mismatch (bar chart)](figures/narr_ea_acs_aba_cert_mismatch.png)

Of the 136 facilities that physically have burn beds:
- **ACS-only** (trauma certified, NOT burn-certified): a significant cohort holds burn beds under ACS verification only — meaning their burn care competency has never been independently audited by ABA or their state.
- **Neither ACS nor ABA**: Some facilities have burn beds with **no formal certification at all**.
- **Both ACS + ABA/State** (fully aligned): the minority of facilities with complete, consistent credentialling.

The practical consequence: when a 911 dispatcher or ER attending conducts a real-time referral search, they may identify a nearby ACS-verified facility with burn beds and route the patient there — believing it to be an appropriate burn-care destination. The ACS stamp does not guarantee the staff training, wound management protocols, or infection-control environments specific to severe burns. **ACS verification is necessary but not sufficient for burn care.**

### 5.3 Adult vs. Pediatric Burn Bed Mismatch (Infrastructure Level)

The previous section identified the mismatch at the centre-flag level (which states list adult vs pediatric burn capability). The infrastructure-level question is different: **where are the physical burn beds actually available for children?**

![Adult vs pediatric burn beds by state (grouped bar)](figures/narr_ea_age_mismatch_beds.png)

The grouped bar chart above compares, for the 25 highest-volume states, the number of burn beds in adult-capable facilities vs. beds in peds-capable facilities. Several states with meaningful adult burn bed inventory show **zero** peds-capable burn beds (red-shaded columns). This is the infrastructure-level proof of the capability-flag mismatch: it is not merely a labelling gap — the physical beds for children simply do not exist in those states.

An additional category surfaces from this bed-level analysis: **facilities that report burn beds but set neither the `BURN_ADULT` nor `BURN_PEDS` flag**. These facilities possess physical burn infrastructure but are not counted in any capability-based analysis, creating beds that are invisible to referral systems.

### 5.4 State Infrastructure Scorecard

Combining burn beds, capability flags, and verification status into a unified state scorecard produces four categories:

| Infrastructure Status | States | Key Risk |
|-----------------------|--------|----------|
| **Adequate** (beds + verified) | 19 | Low |
| **Risk: Unverified burn beds present** | **22** | 534 beds outside quality framework |
| **Critical: No burn beds at all** | **8** | AK, DE, MS, MT, ND, NH, RI*,SD |
| **Partial: Adult-Only bed access** | 1 (CT) | Children cannot access beds in-state |

*RI has ABA verification but zero recorded burn beds — verified-without-infrastructure anomaly.

![State infrastructure scorecard heatmap](figures/narr_ea_infrastructure_scorecard.png)

![Verification coverage scatter by state](figures/narr_ea_pct_verified_beds_scatter.png)

The scatter of verification coverage (% of burn beds in verified facilities) vs. total burn bed volume shows a clear pattern: **smaller-volume states are more likely to have 0% of their burn beds in verified facilities** (AR, NM, ID, KY, WV, VT, HI all appear at 0%), while high-volume states tend toward better alignment. This is a structural incentive problem: only states with enough burn volume to support a dedicated verified burn programme have the patient throughput to maintain ABA or state accreditation.

### 5.5 Infrastructure Mismatch as Root Cause of Real-Time Referral Delays

The burn-centre flag analysis (Section 5, previous version) established that 12 states have no in-state pediatric burn centre. The infrastructure analysis deepens this finding:

1. **States where referral ends in an unverified facility**: A patient transferred from a gap state may arrive at the "nearest hub" only to find a facility whose burn beds were never subject to ABA quality review — possibly delaying appropriate care further once physically present.

2. **States where referral bypasses existing (unverified) beds**: Referral algorithms typically filter for verified/designated centres. The 534 unverified burn beds are generally invisible to coordinated referral networks, meaning patients are transported further when local unverified beds might, in an emergency, be serviceable — at the cost of uncertain quality outcomes.

3. **The zero-bed verified anomaly**: States like RI that are nominally "verified" but whose single NIRD-listed burn facility records zero burn beds present a false confidence problem: the verification label is on file, the physical infrastructure may not match it.

![US map of burn coverage status](figures/narr_ea_mismatch_map.png)

![States where children need peds burn referral](figures/narr_ea_peds_referral_states.png)

![Referral distance burden chart](figures/narr_ea_referral_delay_distance.png)

The average referral distance for adults in no-burn-center states is **626.5 km**. Alaska remains the most extreme case at 2,617 km. The critical NH→VT referral chain failure identified previously is compounded here: VT has 9 burn beds in a 0%-verified facility, meaning a pediatric NH patient routed to VT arrives at an unverified bed — a double failure.

### 5.6 Burn Fatality Rate Correlation with Infrastructure Quality

States with an Adult-Only Gap or No Burn Centre show elevated burn fatality rates compared to states with verified adult and pediatric burn coverage. This correlation holds at the infrastructure quality level as well: the states with the highest proportions of **unverified** burn bed capacity (MO, TN, AL, LA) show burn mortality above the national mean of 1.19/100k.

![Mismatch vs fatality scatter](figures/narr_ea_mismatch_vs_fatality.png)

The mechanism operates at every link: absence of verified infrastructure lengthens the pre-treatment interval (no verified referral destination), degrades care quality upon arrival (unverified facility), and reduces the probability of early specialist intervention (no ABA-trained burn team).

---

## 6. Cross-Challenge Synthesis

Equitable access is not an isolated problem. The cross-challenge vulnerability heatmap below combines all four dimensions of this project -- access risk, capacity fragility, referral dependency, and telemedicine priority -- into a single normalised view. States that appear red across all columns face compounding healthcare access challenges. New Mexico, Alaska, Oklahoma, and Mississippi consistently rank among the most vulnerable states across every dimension.

![Cross-challenge heatmap](figures/narr_cross_challenge_heatmap.png)

---

## 7. Recommendations and Practical Impact

**For state health agencies in the six Critical-tier states (NM, OK, WA, MD, KY, AK):** prioritise federal grant applications under the HRSA Trauma Systems Program to expand trauma and burn bed capacity. The per-capita metrics in this report provide the quantitative evidence required for competitive grant narratives. Timeline: 6-18 months.

**For states with 100% capacity fragility (NM, RI, VT):** develop redundancy plans immediately. Designate backup facilities for surge scenarios, sign interstate memoranda of understanding with neighbouring states, and conduct tabletop exercises for facility-loss scenarios. Timeline: 3-6 months.

**For payers and quality improvement teams:** embed the per-capita access metric in annual network adequacy reports. States flagged as Critical or Moderate should trigger review of clinical coverage sufficiency. This pipeline is fully reproducible and can be re-run annually with updated data. Timeline: 1-3 months for initial integration.

**[NEW] For the 5 Adult-Only Gap states (CT, KY, ME, VT, WV):** Commission a feasibility assessment for designating an existing children's hospital or paediatric unit within the state as an ABA-verified paediatric burn centre — with actual dedicated burn beds (minimum 4 beds). The capability flag alone is insufficient; the physical bed infrastructure must accompany the designation. Timeline: ABA verification within 18--36 months.

**[NEW] For the 7 No-Burn-Center / no-burn-bed states (AK, DE, MS, MT, ND, NH, SD):** prioritise **referral protocol formalisation and burn-specific telemedicine integration** as the immediate intervention. Pre-establish age-appropriate transfer agreements to the nearest ABA-verified adult AND paediatric burn centres. For Alaska (2,617 km to WA), pre-position burn resuscitation kits at regional air hubs. Timeline: 3--12 months.

**[NEW] For the 22 states with unverified burn beds (534 beds total):** Mandate a time-limited ABA verification review for any facility that (a) has five or more burn beds and (b) currently holds only ACS trauma verification. Facilities that do not achieve ABA or state burn-centre designation within 24 months should not appear in official referral directories as burn-capable destinations. This closes the ACS≠ABA certification gap and prevents patients from being routed to unqualified facilities. States with the most urgent caseload: Missouri (81 beds), Texas (76), Tennessee (37), Alabama (52). Timeline: 12--24 months for audit; 24--36 months for full remediation.

**[NEW] Fix the referral chain failure (NH→VT) and audit all hub states:** The referral network currently routes NH patients to VT without checking VT's Adult-Only Gap or zero-verified-bed status. All referral protocols and EMS dispatch systems must enforce **age-appropriate routing with verification filtering**: (i) paediatric burn patients from NH should be routed to Boston Children's Hospital; (ii) the referral engine should exclude any facility with 0 recorded burn beds or 0% verified burn bed coverage from paediatric burn referral directories. Timeline: 0--6 months (policy fix, no capital required).

---

## 8. Data and Reproducibility

| Asset | Path |
|-------|------|
| NIRD dataset | `data/NIRD 20230130 Database_Hackathon.csv` |
| CDC WISQARS Fatal Burn Data (2023) | `data/external/fatal_report_per_state.csv` |
| Census population | `data/external/state_population_2012.csv` |
| Pipeline script | `src/challenge_pipeline.py` |
| Mismatch analysis (centre flags) | `scripts/analyze_mismatch_full.py` |
| Infrastructure & certification analysis | `scripts/analyze_infrastructure.py` |
| Output CSV (state metrics) | `outputs/equitable_access_state_metrics.csv` |
| Output CSV (centre-flag mismatch) | `outputs/burn_mismatch_by_state.csv` |
| Output CSV (infrastructure scorecard) | `outputs/burn_infrastructure_scorecard.csv` |
| Output CSV (bed age mismatch) | `outputs/burn_bed_age_mismatch.csv` |
| All figures | `docs/figures/narr_ea_*.png`, `docs/figures/narr_fatal_*.png` |

```bash
python src/challenge_pipeline.py               # regenerates CSVs
python scripts/generate_narrative_figures.py    # regenerates original figures
python scripts/analyze_mismatch_full.py        # regenerates centre-flag mismatch
python scripts/analyze_infrastructure.py       # regenerates infrastructure + certification analysis
```

