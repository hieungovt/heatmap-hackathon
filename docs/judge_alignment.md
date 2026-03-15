## Judge Alignment – HeatMap Hackathon

This document links the **HeatMap Hackathon Team Evaluation Form** criteria to specific assets in this repository.

**Primary use case:** Equitable Access

### I. Clinical / Business Use Case (15 points)

- **1. Primary Use Case Identification & Alignment (1–5)**
  - Clearly state the primary use case (Equitable Access) in:
    - `README.md` (top of file)
    - `notebooks/05_summary_and_story.ipynb` (introduction section)
  - Show how each major analysis (access, capacity, equity) ties back to equitable access questions.

- **2. Use Case–Driven Insights (1–5)**
  - `notebooks/02_access_coverage_analysis.ipynb`:
    - Maps of where trauma and burn centers exist and where service deserts appear.
  - `notebooks/04_equity_fairness_analysis.ipynb`:
    - Comparisons of access and per-capita capacity across regions and populations.
  - `notebooks/05_summary_and_story.ipynb`:
    - Bullet-pointed, evidence-backed insights with short explanations of why they matter.

- **3. Patient, Provider, or System Impact (1–5)**
  - In `05_summary_and_story.ipynb`, dedicate a section to:
    - \"Implications for patients\" (e.g., travel distance or limited access in certain regions).
    - \"Implications for providers/systems\" (e.g., reliance on single centers, surge vulnerability).

### II. Analytic / Methodologic Quality (15 points)

- **4. Methodological Soundness (1–5)**
  - Each notebook includes markdown sections describing:
    - Data sources and joins (especially in `01_data_understanding.ipynb` and `04_equity_fairness_analysis.ipynb`).
    - Assumptions (e.g., using ZIP centroids as access proxies).
    - Limitations and potential biases.

- **5. Innovation & Creativity (1–5)**
  - Highlight at least one non-trivial or novel element, such as:
    - Scenario analysis of capacity loss (`03_capacity_resilience_analysis.ipynb`).
    - An interactive or particularly insightful map/visual in `02_*` or `04_*`.
  - Call these out in `05_summary_and_story.ipynb` under a \"What makes this approach different\" section.

- **6. Data Integration & Insight Generation (1–5)**
  - Use `data/external/` sources (population, geography, urban–rural) joined via helpers in `src/data_loading.py`.
  - Show how enriched features (e.g., per-capita beds, urban vs. rural splits) change or sharpen insights.

### III. Presentation & Communication (15 points)

- **7. Clarity & Storytelling (1–5)**
  - `05_summary_and_story.ipynb` organized as:
    1. Problem and primary use case.
    2. Approach (CRISP-DM steps in brief).
    3. Key findings (grouped by lens).
    4. Implications and recommendations.

- **8. Visual & Verbal Quality (1–5)**
  - Ensure that:
    - Plots from `src/visualization.py` are labeled and readable.
    - Map legends and color scales are intuitive.
  - Select a small set of \"presentation-ready\" figures and reference them in this document for easy inclusion in slides.

- **9. Actionability, Feasibility & Impact (1–5)**
  - In `05_summary_and_story.ipynb`, add a final section:
    - \"Next steps\" – concrete follow-on analyses or data collection.
    - \"Feasibility\" – brief notes on how the insights could be operationalized (e.g., prioritizing regions for telemedicine or referral network strengthening).

### Total Score and Self-Evaluation

- Use `additional_resources/Judge_Evaluation_Form.pdf` to perform a self-score once analyses are in place.
- Record key strengths and opportunities for improvement at the bottom of `05_summary_and_story.ipynb` or in this file as a short retrospective.
