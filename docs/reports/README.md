# Challenge Area Reports

This folder contains full reports for each of the three HeatMap Hackathon challenge areas. Each report:

- **Explains the problem** in real-world terms
- **Describes our strategy** and why we chose it
- **Highlights key findings** with evidence
- **Aligns findings with visualizations** (figures in `docs/figures/`)
- **Provides practical recommendations** for stakeholders

## Reports

| Challenge Area | Report | Key Output |
|----------------|--------|------------|
| **Equitable Access** | [report_equitable_access.md](report_equitable_access.md) | State-level per-capita capacity, fragility, priority ranking |
| **Referral Networks** | [report_referral_networks.md](report_referral_networks.md) | States without burn centers, nearest hub, transfer distance (km) |
| **Telemedicine** | [report_telemedicine.md](report_telemedicine.md) | Telemedicine priority score, component breakdown, deployment ranking |

## Regenerating Reports and Figures

1. Run the challenge pipeline: `python src/challenge_pipeline.py`
2. Generate report visualizations: `python scripts/generate_report_visualizations.py`

Figures are saved to `docs/figures/` with the `report_*` prefix.
