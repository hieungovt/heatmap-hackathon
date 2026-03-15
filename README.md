## HeatMap Hackathon – Equitable Access to Trauma & Burn Care

This repository supports a HeatMap Hackathon project using a national hospital dataset to explore **where trauma and burn care capacity exists, who can realistically access it, and where gaps or inequities may be present**.

The work is structured using the **CRISP-DM** framework and evaluated against the official **HeatMap Hackathon Team Evaluation Form** in `additional_resources/Judge_Evaluation_Form.pdf`.

**Primary use case (for judging form): _Equitable Access_**

### 1. Repository structure

- **Root**
  - `README.md`: This file – environment setup, project overview, and how to run analyses.
  - `overview.md`: High-level description of the main hospital dataset and key columns.
  - `environment.yml`: Conda environment specification for analysis and visualization.
  - `requirements.txt`: Optional `pip`-based dependency list mirroring `environment.yml`.
- **Data**
  - `data/NIRD 20230130 Database_Hackathon.csv`: Main hospital trauma/burn dataset (one row per facility).
  - `data/external/` (to be created): Additional public datasets (population, geography, urban–rural, etc.).
- **Analysis code**
  - `src/data_loading.py`: Functions to load and clean the main dataset (and later, external data).
  - `src/features.py`: Feature engineering utilities (per-capita metrics, access proxies, etc.).
  - `src/visualization.py`: Common plotting and mapping helpers for consistent visuals.
- **Notebooks**
  - `notebooks/01_data_understanding.ipynb`: Data understanding & cleaning decisions (CRISP-DM: Data Understanding & Preparation).
  - `notebooks/02_access_coverage_analysis.ipynb`: Access & coverage lens – where trauma/burn care is available.
  - `notebooks/03_capacity_resilience_analysis.ipynb`: Capacity & resilience lens – concentration and fragility of capacity.
  - `notebooks/04_equity_fairness_analysis.ipynb`: Equity lens – differences across regions and populations.
  - `notebooks/05_summary_and_story.ipynb`: Synthesis of findings, story, and judge-aligned highlights.
- **Docs & evaluation**
  - `docs/judge_alignment.md`: Mapping from the official judging criteria to specific analyses and visuals in this repo.
  - `additional_resources/Judge_Evaluation_Form.pdf`: Official evaluation form used as the scoring baseline.

### 2. Environment setup (Conda)

- **Prerequisites**
  - Miniconda or Anaconda installed
  - `git` (optional but useful)

- **Create and activate the Conda environment (recommended)**

From the project root (`f:\heatmap_hackathon`):

```bash
conda env create -f environment.yml
conda activate heatmap-hackathon
```

If you change the environment name in `environment.yml`, update the `conda activate` command accordingly.

- **Register the kernel for Jupyter (first time only)**

With the Conda environment active:

```bash
python -m ipykernel install --user --name heatmap-hackathon
```

- **Alternative: pip/virtualenv (optional)**

If you prefer not to use Conda, you can still create a virtualenv and install from `requirements.txt`:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # on Windows
pip install -r requirements.txt
```

### 3. Running the notebooks

1. **Start Jupyter Lab or Notebook** from the project root:

   ```bash
   jupyter lab
   ```

   or

   ```bash
   jupyter notebook
   ```

2. In the Jupyter interface, select the **`heatmap-hackathon`** kernel if prompted.

3. Open and run notebooks in this order (top to bottom, all cells in each notebook):
   1. `notebooks/01_data_understanding.ipynb`
   2. `notebooks/02_access_coverage_analysis.ipynb`
   3. `notebooks/03_capacity_resilience_analysis.ipynb`
   4. `notebooks/04_equity_fairness_analysis.ipynb`
   5. `notebooks/05_summary_and_story.ipynb`

Each notebook will build on cleaned and enriched data prepared in earlier steps.

### 4. Data sources and CRISP-DM mapping

- **Main dataset**
  - `data/NIRD 20230130 Database_Hackathon.csv`: Hospital-level fields such as location (state, county, city, ZIP), capacity (`TOTAL_BEDS`, `BURN_BEDS`), and trauma/burn designations and verification.

- **Planned external datasets (to be stored under `data/external/`)**
  - Population and demographic data (e.g., census/ACS) at county or ZIP level.
  - Geographic boundaries (state/county shapefiles, ZIP polygons).
  - Urban–rural classifications.

- **CRISP-DM stages in this repo**
  - **Business understanding**: Framed in terms of **equitable access** to trauma and burn care.
  - **Data understanding**: `01_data_understanding.ipynb`.
  - **Data preparation**: Cleaning and feature engineering split between `01_data_understanding.ipynb` and `src/` utilities.
  - **Modeling / analysis**: `02_*`, `03_*`, `04_*` notebooks (access, capacity, equity lenses).
  - **Evaluation & deployment**: `05_summary_and_story.ipynb`, `docs/judge_alignment.md`, and slide-ready visuals.

### 5. Judging criteria alignment

The repository is designed with the **HeatMap Hackathon Team Evaluation Form** as a baseline:

- **Clinical / Business Use Case**
  - We explicitly select **Equitable Access** as the primary use case and frame all major findings in that context.
  - Notebooks highlight real-world implications for **patients, providers, and systems**.

- **Analytic / Methodologic Quality**
  - Methods, assumptions, and limitations are documented in markdown cells.
  - External datasets are integrated to strengthen insights and per-capita/equity calculations.

- **Presentation & Communication**
  - `05_summary_and_story.ipynb` provides a clear narrative from **problem → analysis → insights → action**.
  - `docs/judge_alignment.md` maps specific analyses and figures to each scoring criterion.

### 6. Next steps

- Fill `data/external/` with chosen public datasets and update `src/data_loading.py` joins.
- Implement feature engineering in `src/features.py` and mapping utilities in `src/visualization.py`.
- Flesh out each notebook with progressively deeper analyses and presentation-ready visuals.

### 7. Run full challenge pipeline and reports

To regenerate all challenge outputs, figures, and report visualizations:

```bash
python src/challenge_pipeline.py
python scripts/generate_report_visualizations.py
```

Generated artifacts:

- `outputs/equitable_access_state_metrics.csv`
- `outputs/referral_network_recommendations.csv`
- `outputs/telemedicine_priority_state_scores.csv`
- `docs/figures/*.png` (including `report_*` visualizations)
- Full reports in `docs/reports/report_*.md`
- Challenge summaries in `docs/challenge_area_*.md`
