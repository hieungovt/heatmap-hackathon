# Challenge Area 2: Referral Networks for Trauma and Burn Care

## 1. Understanding the Problem

Not every hospital in the United States can treat severe burns. When a burn patient presents at a facility that lacks a dedicated burn centre, that patient must be **transferred** to a facility that has one -- often across state lines, over hundreds or even thousands of kilometres. This transfer process is governed by referral networks: the predetermined agreements, routing protocols, and geographic assignments that determine which patients go where.

In many regions, these networks are informal or non-existent. Transfer decisions are made ad hoc, with emergency physicians calling around to find an available bed. This introduces delays, uncertainty, and suboptimal routing. In the worst cases, patients in states with no burn centre at all face multi-hour air transports with no guaranteed destination, wasting golden-hour minutes on coordination rather than treatment. Before we can design an effective referral network, however, we must first understand what exists: **what burn care infrastructure already exists within each state**, and where the true gaps are that require out-of-state solutions.

---

## 2. The NIRD Dataset: Mapping In-State Burn Care First

### 2.1 Dataset Overview -- Through the Lens of Referral Capacity

The NIRD dataset contains 635 trauma and burn care facilities across the United States. For the referral networks challenge, the critical fields are `BURN_ADULT` (a boolean indicating whether a facility has adult burn centre capability) and `BURN_BEDS` (the count of beds specifically dedicated to burn care). By aggregating these at the state level, we can build a complete picture of what burn care exists within each state's borders -- the essential first step before discussing inter-state referrals.

The approach is deliberate: **map what exists locally before reaching outward**. A state with three burn centres and 60 burn beds faces a fundamentally different referral challenge than a state with one centre and 8 beds, even if both technically "have burn capability." Understanding the in-state landscape shapes the nature of the referral question.

### 2.2 In-State Burn Center Inventory

The dual-panel chart below provides the foundational view: for every state, how many adult burn centres exist (left panel) and how many dedicated burn beds are available (right panel). Red bars indicate states with zero capability -- these are the states that are entirely referral-dependent. Orange (1-2 centres) indicates fragile capability, and green (3+) indicates more robust in-state coverage.

Several patterns are immediately apparent. Georgia leads the nation with 129 burn beds across multiple facilities, driven by the Joseph M. Still Burn Center in Augusta. Texas, New York, California, and Illinois also have substantial in-state infrastructure. But numerous states show the orange "fragile" pattern: technically they have a burn centre, but capacity is thin. States like New Mexico, Vermont, and Rhode Island each have only a single burn centre, creating extreme single-point-of-failure risk even though they are not classified as referral-dependent.

![In-state burn center detail](figures/narr_rn_instate_detail.png)

### 2.3 Burn Specialisation: How Much of the System is Dedicated to Burns?

Having a burn centre is necessary, but how much of a state's total capacity is actually dedicated to burn care? The specialisation ratio -- burn beds as a percentage of total state beds -- reveals which states have built proportionally deep burn infrastructure and which treat burn care as a minor adjunct to their trauma system.

The chart below shows specialisation ratios for all states with burn capability. New Jersey stands out with the highest ratio, despite having only one small burn-only facility (12 beds). Nebraska's ratio is elevated because its burn facility is a dedicated 16-bed centre (CHI Health St. Elizabeth) in a smaller state. States like California and Texas, despite having many burn beds in absolute terms, show lower specialisation ratios because their total bed counts are so large that burn care represents a small fraction of overall capacity.

This matters for referrals: a state with low specialisation may have adequate general trauma care but still need to refer complex burn cases. Conversely, states with high specialisation are natural "hub" candidates because they have disproportionately invested in burn expertise.

![Burn specialisation ratio](figures/narr_rn_burn_specialisation.png)

### 2.4 Anchor Institutions: The Largest Burn Facility in Each State

Before designing inter-state referral routes, it is essential to know **which facility would receive the patients** in each hub state. The chart below identifies the largest burn facility (by burn bed count) in every state with burn capability, annotated with the facility name and city.

Several facilities stand out as regional anchors: the Joseph M. Still Burn Center (Augusta, GA) with 99 burn beds is by far the largest, followed by Harborview Medical Center (Seattle, WA) with 40 beds, Banner University Medical Center (Tucson, AZ) with 35 beds, and Parkland Memorial Hospital (Dallas, TX) with 30 beds. These are the institutions that would serve as natural hubs for referral-dependent states nearby.

Critically, this view also reveals **single-facility risks** in hub states. Washington's entire burn capability for the region (including Alaska's referrals) depends on Harborview's 40 beds. If Harborview reaches capacity during a regional event, the entire Pacific Northwest referral network fails.

![Largest burn facility per state](figures/narr_rn_largest_burn_facility.png)

### 2.5 The Coverage Gap: Which States Have No Burn Centre?

With the in-state landscape fully mapped, we can now precisely identify the gap. Seven states -- shown in red on the map below -- have zero adult burn centres: **Alaska, Delaware, Mississippi, Montana, New Hampshire, North Dakota, and South Dakota**. These states are fully referral-dependent for burn care. Every severe burn patient in these states must be transferred out of state, a process that adds time, cost, and clinical risk.

![Burn coverage map](figures/narr_rn_burn_coverage_map.png)

The geographic pattern of these gaps is notable and has implications for referral design. The Great Plains states (MT, ND, SD) form a contiguous cluster, suggesting a regional consortium approach. Delaware and New Hampshire are geographically adjacent to well-resourced states (Maryland and Vermont), suggesting quick-win bilateral agreements. Alaska is categorically different: isolated by geography, with the longest potential transfer distance in the nation, requiring a fundamentally different solution.

**Burn bed concentration confirms the fragility.** Even among states that have burn centres, the distribution of beds is highly concentrated in a few states. The chart below shows total burn beds per state. The gap between the top tier (GA, TX, NY, CA) and the many states with 6-15 beds is enormous. This concentration means that hub states absorb not just their own burn volume but the referral volume of neighbouring dependent states.

![Burn beds concentration](figures/narr_rn_burn_beds_concentration.png)

---

## 3. Expanding with External Data: Geographic Hub Assignment

### 3.1 The Approach

With the in-state picture complete, we can now compute inter-state referral pathways for the seven gap states. We brought in two external datasets:

1. **US Census TIGER State Boundaries** (`cb_2023_us_state_20m.shp`): state boundary polygons for centroid computation and distance calculation.
2. **US Census 2012 State Population Estimates** (`state_population_2012.csv`): to quantify the at-risk population in each dependent state.

The pipeline (`src/challenge_pipeline.py`) reprojects state boundaries to EPSG:2163 (US National Equal Area), computes centroids, calculates centroid-to-centroid distances from each dependent state to all hub states, and selects the nearest hub. Each corridor is then classified by urgency:
- **Immediate** (>1,000 km): requires dedicated air transport protocols
- **Short-term** (200-1,000 km): standard air or ground transport, formalise within 6-12 months
- **Quick-win** (<200 km): ground transport feasible, formalise within 3-6 months

### 3.2 What the Enriched Data Reveals

**Alaska faces the most extreme transfer burden.** At 2,617 km from its nearest hub (Washington), Alaska's transfer corridor requires fixed-wing aircraft and can take 4-6 hours depending on weather. For context, this is roughly the distance from New York to Denver. No other state faces a comparable burden.

The urgency-tier chart below colour-codes each corridor and annotates it with the recommended hub state and the at-risk population. Mississippi, despite a moderate distance (266 km to Alabama), has the largest at-risk population at approximately 2.99 million people -- making it the highest-impact short-term priority.

![Referral urgency tiers](figures/narr_rn_urgency_tiers.png)

**Delaware and New Hampshire are quick-win opportunities.** Both states are less than 110 km from their nearest hub. Formalising a referral agreement between Delaware and Maryland (which has the Johns Hopkins Burn Center) or between New Hampshire and Vermont (which has the UVM Burn Center) can be achieved with minimal operational complexity. These two corridors should be prioritised for immediate implementation as proof-of-concept agreements that can then be used as templates for more complex corridors.

**The Great Plains cluster enables a regional consortium.** Montana (→Idaho, 489 km), North Dakota (→Minnesota, 486 km), and South Dakota (→Nebraska, 325 km) are geographically proximate to one another and to their respective hubs. A coordinated Midwestern burn referral consortium -- involving all six states -- could provide shared capacity tracking, mutual surge protocols, and coordinated air transport dispatch. This is more efficient than three separate bilateral agreements.

**The referral map makes the full picture clear.** The map below shows all referral-dependent states in red with hub assignments and distances annotated. The contrast between the Eastern quick-wins (DE, NH) and the Western challenge (AK, MT) is visually immediate.

![Referral assignment map](figures/narr_rn_referral_map.png)

---

## 4. Cross-Challenge Synthesis

Referral dependency compounds other access challenges. The cross-challenge vulnerability heatmap below shows that referral-dependent states also tend to rank high on access risk, capacity fragility, and telemedicine priority. Alaska, Mississippi, and Montana appear red across nearly every dimension, confirming that referral gaps are part of a broader, compounding healthcare access crisis.

This has a practical implication: referral agreements alone are insufficient. These states need a multi-layered intervention: expanded in-state capacity (Challenge 1), formalised referral agreements (this challenge), and telemedicine pre-transfer consult services (Challenge 3). The three solutions are complementary, not competing.

![Cross-challenge heatmap](figures/narr_cross_challenge_heatmap.png)

---

## 5. Burn Fatality Burden in Referral-Dependent States (CDC WISQARS 2023)

The integration of CDC WISQARS 2023 fatal fire/burn data reveals the human cost of referral dependency. Across the seven states with no in-state burn centre, **burn deaths are not rare**. Mississippi alone recorded 83 burn fatalities in 2023 at a crude rate of 2.82 per 100k -- more than double the national average of 1.19. Alaska had 22 deaths at a rate of 3.00 per 100k, the third-highest in the nation.

The chart below quantifies the fatality burden in each referral-dependent state. Collectively, these seven states experienced over **233 burn deaths** in 2023 -- deaths that occurred in populations with no in-state burn centre. While not all of these deaths would have been prevented by local burn care (some are fire-scene fatalities), studies consistently show that proximity to a burn centre reduces burn mortality by 20-30%, particularly for moderate-severity injuries where early specialised intervention changes outcomes.

Mississippi's combination of high fatality rate (2.82) and large at-risk population (2.99M) makes it the single highest-impact state for referral formalisation. Alaska's extreme fatality rate (3.00) and extreme transfer distance (2,617 km) make it the highest-urgency state for telemedicine pre-transfer consults.

![Referral burden fatalities](figures/narr_fatal_referral_burden.png)

---

## 6. Recommendations and Practical Impact

**Total population impact:** approximately **7.4 million Americans** across the seven referral-dependent states would benefit from formalised referral agreements.

**For quick-win corridors (DE→MD, NH→VT):** adapt existing interstate trauma compact frameworks to establish burn-specific referral protocols within 3-6 months. These two corridors serve as low-cost proof-of-concept implementations.

**For the Midwestern cluster (MT, ND, SD):** convene a regional burn referral consortium with hubs in ID, MN, and NE. A HRSA-funded regional coordinator can establish shared capacity tracking and mutual surge protocols. Timeline: 12-18 months.

**For Alaska→Washington:** establish a dedicated air transport protocol and pre-transfer telemedicine consult service. Alaska requires a fundamentally different approach due to extreme distance, weather constraints, and limited 5G infrastructure. Timeline: 6-12 months, with federal health funding (Indian Health Service) as a potential lever.

**For hub burn centres:** formally accept referral assignments from dependent neighbours, designate a referral coordinator, and build incoming referral volume into surge planning models. Hub centres benefit from predictable referral volume rather than ad hoc calls.

---

## 7. Data and Reproducibility

| Asset | Path |
|-------|------|
| NIRD dataset | `data/NIRD 20230130 Database_Hackathon.csv` |
| State boundaries (TIGER) | `data/external/cb_2023_us_state_20m/` |
| Census population | `data/external/state_population_2012.csv` |
| Pipeline script | `src/challenge_pipeline.py` |
| Output CSV | `outputs/referral_network_recommendations.csv` |
| Figure generation | `scripts/generate_narrative_figures.py` |
| All figures | `docs/figures/narr_rn_*.png` |
| Datasets needed | `docs/datasets_to_add_manually.md` |

```bash
python src/challenge_pipeline.py               # regenerates CSVs
python scripts/generate_narrative_figures.py    # regenerates all figures
```
