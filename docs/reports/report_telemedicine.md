# Challenge Area 3: Telemedicine for Trauma and Burn Care Access

## 1. Understanding the Problem

Telemedicine -- the delivery of clinical expertise via video, imaging, and communication technology -- has the potential to fundamentally change how trauma and burn patients receive specialist support. In regions where the nearest burn centre is hundreds of kilometres away, a telemedicine consult can bring a specialist's eyes and judgment to the bedside within minutes, guiding local providers through stabilisation, assessing burn severity, and determining whether a costly transfer is actually necessary.

But telemedicine impact is not uniform. In states with abundant local trauma and burn capacity, telemedicine adds convenience rather than critical capability. In states with both a severe access gap *and* the digital infrastructure to support remote consults, telemedicine becomes a lifeline. The challenge is to identify **where telemedicine deployment will have the greatest clinical impact**, considering not just one dimension of need but the full constellation of factors -- access gaps, system fragility, rurality, broadband readiness, provider supply, and social vulnerability.

This analysis builds a composite **Telemedicine Priority Score** that ranks all 50 US states plus DC by deployment urgency. It begins with findings from the NIRD dataset, then systematically integrates six external datasets to produce a multi-dimensional score that enables tailored, state-specific deployment strategies.

---

## 2. The NIRD Dataset: What It Contains and What It Reveals

### 2.1 Dataset Overview -- Through the Lens of Telemedicine Need

For the telemedicine challenge, the NIRD dataset provides the demand-side foundation: where is in-person specialist capacity weakest, and therefore where would virtual specialist access add the most value? The relevant fields are `TOTAL_BEDS`, `BURN_ADULT`, `TRAUMA_ADULT`, and the derived per-capita and fragility metrics from Challenge 1.

The core insight is straightforward: telemedicine is most valuable where in-person access is least available. The NIRD data lets us identify those states, characterise the severity of their gaps, and understand the structural reasons (low facility count, high concentration, absence of burn capability) that telemedicine could partially address.

### 2.2 Initial Findings from the NIRD Data Alone

**Low-access states also tend to be high-fragility states.** The dual-axis chart below plots per-capita bed capacity (blue bars) against capacity fragility (red line) for the bottom 20 states by beds per 100k. The pattern is striking: the states with the fewest beds per capita (NM, OK, WA, MD, KY) also tend to have high fragility percentages. This is not a coincidence -- in states with few facilities, each individual facility carries a disproportionate share of the load. This creates a compounding problem: these states have both the smallest safety margin and the highest consequence of any capacity disruption. Telemedicine can partially mitigate this by providing virtual specialist support that extends the reach of existing facilities.

![Access vs fragility](figures/narr_tm_access_fragility.png)

**Most facilities are trauma-only; dual-capable centres are rare.** The stacked bar chart below breaks facilities into three categories: trauma-only (blue), dual trauma+burn capability (green), and burn-only (red). Even in the most facility-rich states, the overwhelming majority of centres provide trauma care but not burn care. This gap is precisely the opportunity for telemedicine: a local trauma centre that receives a burn patient can, with telemedicine guidance, provide initial stabilisation and assessment that may reduce unnecessary transfers or improve patient outcomes during the transfer window.

![Trauma-burn gap](figures/narr_tm_trauma_burn_gap.png)

These NIRD-based findings establish that telemedicine need correlates strongly with existing access gaps. But need alone is insufficient for deployment planning. A state may desperately need telemedicine but lack the broadband infrastructure to support it. Another may have strong digital infrastructure but also strong in-person access, making telemedicine less impactful. To build a deployment roadmap, we need to integrate need with readiness, provider supply, and social context.

---

## 3. Expanding with External Data: The Multi-Dimensional Priority Score

### 3.1 The Approach

The telemedicine priority score is constructed from six weighted components, each drawn from a distinct data source. This multi-source integration is the analytical heart of this challenge:

| Component | Weight | Data Source | What It Captures |
|-----------|--------|------------|------------------|
| **Access gap** | 25% | NIRD + Census population | Inverse of beds per 100k: states with the least per-capita capacity get the highest score |
| **Capacity fragility** | 15% | NIRD (single-facility concentration) | States where one facility failure = catastrophic capacity loss |
| **Rurality** | 15% | USDA RUCC 2023 county classification | Share of counties classified as rural; higher rurality = longer travel times and greater telemedicine value |
| **Digital gap** | 15% | FCC BDC 5G mobile broadband data (Mar 2026) | 100 minus 5G coverage percentage; captures infrastructure constraint (not just need) |
| **Provider shortage** | 15% | AHRF primary care physician density (2024-2025) | Inverse of physicians per 100k; in provider-poor regions, telemedicine extends the specialist-to-patient ratio |
| **Social vulnerability** | 15% | CDC SVI county-level data (2022), population-weighted | Social vulnerability compounds all other barriers; high-SVI populations benefit most from any access expansion |

Each component is **min-max normalised** to [0, 1] across all states, then multiplied by its weight and summed to produce a score between 0 and 100. The result ranks states not by any single dimension of need, but by the composite picture of need, readiness, and context.

The access gap component (25%) is intentionally weighted more heavily because it represents the most direct measure of telemedicine impact: extending specialist expertise to patients who currently have the least access.

### 3.2 Assumptions and Limitations

This scoring approach has several important assumptions:

**Min-max normalisation makes scores relative, not absolute.** A state's score depends on where it falls within the current range of all states. If a new state entered the dataset or an existing state dramatically changed, all scores would shift. Interpret the ranking as relative priority, not a fixed threshold.

**FCC 5G broadband coverage is used as a proxy for telemedicine readiness.** In practice, telemedicine can function on lower-bandwidth connections (standard broadband or even 4G LTE is often sufficient). The digital gap component may overstate the barrier in states with low 5G but adequate 4G/broadband. When FCC data was unavailable, the pipeline falls back to ACS broadband subscription data.

**Equal sub-weights (15% each) for five of six components.** Sensitivity analysis with alternate weight schemes could shift rankings somewhat, but the top states (NM, AK, MS, OK) are robust to moderate weight changes because they rank high on multiple components simultaneously.

### 3.3 What the Enriched Data Reveals

**New Mexico is the highest-priority state for telemedicine deployment (Score: 80.1).** New Mexico leads the national ranking with a score driven by the most extreme access gap in the country (single facility, 26.7 beds/100k), 100% capacity fragility, 79% rural county share, and an SVI percentile of 0.81. Every component except the digital gap pushes NM toward the top. This makes it the strongest single candidate for a statewide trauma/burn telemedicine pilot.

**Different states rank high for different reasons.** The component breakdown chart below is the analytical centerpiece of this report. Each state's total score is decomposed into its six contributing components, revealing *why* each state ranks high and therefore *what kind of intervention* is most appropriate. New Mexico's score is dominated by the access gap and fragility components (red and orange), indicating that capacity expansion alongside telemedicine is the right strategy. Alaska's score is driven heavily by rurality and digital gap (yellow and blue), suggesting that broadband infrastructure investment is a prerequisite for effective telemedicine. Mississippi's profile is dominated by provider shortage and social vulnerability (purple and teal), indicating that telemedicine must be paired with workforce development programs.

![Component breakdown](figures/narr_tm_priority_components.png)

**The top 15 states form a clear deployment queue.** The priority ranking chart below provides the policy-ready deployment order with exact score values. States above score 50 represent the highest-urgency tier; those between 35 and 50 are secondary targets.

![Priority ranking](figures/narr_tm_priority_ranking.png)

**Geographic clusters of high priority are visible on the map.** The US choropleth below shades states by telemedicine priority score. Three regional clusters emerge: the **Southwest** (NM, OK), the **Southeast** (MS, AL, LA), and parts of **northern New England** (VT, ME). These clusters suggest opportunities for regional telemedicine consortia rather than state-by-state deployment.

![Telemedicine US map](figures/narr_tm_us_map.png)

---

## 4. Cross-Challenge Synthesis

The telemedicine challenge is not independent of the other two. The cross-challenge vulnerability heatmap confirms that the highest telemedicine priority states are the same ones identified as having critical access gaps and referral dependency in Challenges 1 and 2. This convergence is important: it means that telemedicine, referral agreements, and capacity investment are not competing strategies -- they are complementary layers of the same solution. A state like Alaska needs all three: expanded in-state capacity (Challenge 1), a formalised air referral agreement with Washington (Challenge 2), and a pre-transfer telemedicine consult service (Challenge 3).

![Cross-challenge heatmap](figures/narr_cross_challenge_heatmap.png)

---

## 5. Recommendations and Practical Impact

**Deploy telemedicine pilots in the top 5 states (NM, AK, OK, MS, VT).** For New Mexico, this means partnering with UNM Hospital (the state's sole NIRD facility) to establish ER triage and pre-transfer burn consult coverage for rural clinics across the state. The estimated impact: even covering 20% of NM's referral volume could save an estimated 40-80 unnecessary air transports per year at $15,000-$50,000 per transport, producing both clinical benefit and cost savings in the first year.

**Tailor the intervention to the state's dominant driver.** For Alaska and Vermont (rurality + digital gap dominant), adopt low-bandwidth video and asynchronous store-and-forward burn image review, which work on existing infrastructure and do not require high-speed 5G. For Mississippi and Kentucky (provider shortage + vulnerability dominant), pair telemedicine with community health worker programs and embed tele-consult into rural FQHC workflows. A one-size-fits-all rollout would waste resources in states where the binding constraint is not technology but provider capacity or social access barriers.

**Track transfer avoidance rate and time-to-specialist as primary success metrics.** These two metrics are the clearest measures of telemedicine impact for trauma and burn care. Transfer avoidance measures how often a telemedicine consult prevents an unnecessary long-distance transfer. Time-to-specialist measures how quickly a patient receives specialist input, whether virtually or in person. Both metrics are extractable from EHR and claims data, making program evaluation feasible from day one.

**Use the priority ranking for grant applications.** The composite score and component breakdown provide the kind of quantitative, multi-source evidence that HRSA Federal Office of Rural Health Policy grants, FCC Healthcare Connect Fund awards, and CMMI innovation grants require. State health departments in top-ranked states can reference this analysis directly in their funding applications.

---

## 6. The Human Cost: Years of Potential Life Lost (CDC WISQARS 2023)

With CDC WISQARS 2023 fatal fire/burn data now integrated, we can quantify not just where telemedicine is needed but **the cost of inaction** in terms of premature death. The Years of Potential Life Lost (YPLL) metric counts every year of life lost before age 65 for each burn fatality -- a measure that amplifies the impact of deaths among younger patients, who have the most years of productive life ahead.

The chart below ranks the top 20 states by burn-related YPLL. Texas leads with 3,417 years of potential life lost, followed by California (3,079), Arizona (1,451), Tennessee (2,136), and Pennsylvania (2,082). But the most revealing comparisons are per-capita: Oklahoma (1,327 YPLL from only 107 deaths), Alabama (1,406 YPLL from 116 deaths), and Mississippi (1,002 YPLL from 83 deaths) all show disproportionately high YPLL-to-death ratios, indicating that their burn fatalities skew younger. These are precisely the states where telemedicine-enabled early specialist intervention could prevent the most years of life lost.

![YPLL ranking](figures/narr_fatal_ypll_ranking.png)

The convergence is clear: the states with the highest YPLL burden are largely the same states that rank highest on the telemedicine priority score. Oklahoma, Mississippi, Alabama, and Kentucky appear in both the top YPLL and top priority rankings -- confirming that the composite score effectively identifies where premature death from burns is most concentrated and where telemedicine could have the most life-saving impact.

---

## 7. Data and Reproducibility

| Asset | Path |
|-------|------|
| NIRD dataset | `data/NIRD 20230130 Database_Hackathon.csv` |
| CDC WISQARS Fatal Burn Data (2023) | `data/external/fatal_report_per_state.csv` |
| FCC Mobile Broadband (5G) | `data/external/bdc_us_mobile_broadband_summary_by_geography_J25_03mar2026/` |
| ACS Broadband (fallback) | `data/external/state_broadband_acs2022.csv` |
| Provider supply (AHRF) | `data/external/AHRF_2024-2025_CSV/` |
| Rurality (USDA RUCC) | `data/external/rucc_2023_county.csv` |
| Social Vulnerability (CDC SVI) | `data/external/SVI_2022_US_county.csv` |
| Census population | `data/external/state_population_2012.csv` |
| Pipeline script | `src/challenge_pipeline.py` |
| Output CSV | `outputs/telemedicine_priority_state_scores.csv` |
| Figure generation | `scripts/generate_narrative_figures.py` |
| All figures | `docs/figures/narr_tm_*.png`, `docs/figures/narr_fatal_*.png` |

```bash
python src/challenge_pipeline.py               # regenerates CSVs
python scripts/generate_narrative_figures.py    # regenerates all figures
```

