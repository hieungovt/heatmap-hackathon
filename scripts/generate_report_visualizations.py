"""
Generate robust visualizations for the three challenge area reports.
Run from project root: python scripts/generate_report_visualizations.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd

try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False

DATA_EXTERNAL = ROOT / "data" / "external"
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "docs" / "figures"

# ── Shared plot style ──────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "--",
})


def load_data():
    """Load all challenge outputs."""
    access = pd.read_csv(OUTPUTS / "equitable_access_state_metrics.csv")
    referral = pd.read_csv(OUTPUTS / "referral_network_recommendations.csv")
    tele = pd.read_csv(OUTPUTS / "telemedicine_priority_state_scores.csv")
    return access, referral, tele


# ── Original figures (preserved + stylistically tightened) ───────────────────

def fig_equitable_access_disparity(access: pd.DataFrame) -> None:
    """Scatter: total beds per 100k vs capacity fragility, sized by population."""
    fig, ax = plt.subplots(figsize=(12, 7))
    access = access.dropna(subset=["total_beds_per_100k", "capacity_loss_pct", "population"])
    access["pop_millions"] = access["population"] / 1e6
    scatter = ax.scatter(
        access["total_beds_per_100k"],
        access["capacity_loss_pct"],
        s=access["pop_millions"] * 8,
        c=access["adult_burn_centers"],
        cmap="YlOrRd",
        alpha=0.75,
        edgecolors="gray",
        linewidths=0.5,
    )
    ax.set_xlabel("Total Beds per 100,000 Population", fontsize=11)
    ax.set_ylabel("Capacity Fragility (% loss if largest facility unavailable)", fontsize=11)
    ax.set_title(
        "Equitable Access: Per-Capita Capacity vs System Fragility\n"
        "(Bubble size = population; Color = adult burn centers)",
        fontsize=12,
    )
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Adult Burn Centers", fontsize=10)
    for _, row in access.nlargest(6, "pop_millions").iterrows():
        ax.annotate(row["STATE"], (row["total_beds_per_100k"], row["capacity_loss_pct"]),
                    fontsize=8, alpha=0.9)
    ax.axvline(x=access["total_beds_per_100k"].median(), color="gray", linestyle="--", alpha=0.5,
               label=f"Median ({access['total_beds_per_100k'].median():.0f} beds/100k)")
    ax.axhline(y=50, color="gray", linestyle="--", alpha=0.5, label="50% fragility threshold")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "report_equitable_access_disparity_scatter.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_equitable_access_ranked(access: pd.DataFrame) -> None:
    """Ranked bar: all states by beds per 100k with tier colour-coding."""
    access = access.sort_values("total_beds_per_100k", ascending=True)
    fig, ax = plt.subplots(figsize=(10, 10))
    colors = ["#e74c3c" if x < 50 else "#3498db" if x < 100 else "#2ecc71"
              for x in access["total_beds_per_100k"]]
    ax.barh(access["STATE"], access["total_beds_per_100k"], color=colors, edgecolor="white", linewidth=0.3)
    ax.axvline(x=100, color="black", linestyle="--", linewidth=1, label="100 beds/100k reference")
    ax.set_xlabel("Total Beds per 100,000 Population", fontsize=11)
    ax.set_ylabel("State", fontsize=11)
    ax.set_title("Equitable Access: State-Level Capacity Ranking\n(Red <50 | Blue 50–100 | Green >100 beds/100k)", fontsize=12)
    red_p = mpatches.Patch(color="#e74c3c", label="< 50 beds/100k (critical)")
    blue_p = mpatches.Patch(color="#3498db", label="50–100 beds/100k (moderate)")
    green_p = mpatches.Patch(color="#2ecc71", label="> 100 beds/100k (adequate)")
    ax.legend(handles=[red_p, blue_p, green_p], loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "report_equitable_access_ranked_bars.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_referral_distance_burden(referral: pd.DataFrame) -> None:
    """Horizontal bar: referral distance burden for states without burn centers."""
    if referral.empty:
        return
    fig, ax = plt.subplots(figsize=(10, 5))
    ref = referral.sort_values("estimated_distance_km", ascending=True)
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.9, len(ref)))
    ax.barh(ref["origin_state"], ref["estimated_distance_km"], color=colors, edgecolor="white")
    ax.set_xlabel("Estimated Distance to Nearest Adult Burn Hub (km)", fontsize=11)
    ax.set_ylabel("Origin State (no burn center)", fontsize=11)
    ax.set_title(
        "Referral Networks: Transfer Burden for States Without Burn Centers\n"
        "(Higher distance = longer transport time, higher risk)",
        fontsize=12,
    )
    for i, (_, r) in enumerate(ref.iterrows()):
        ax.text(r["estimated_distance_km"] + 30, i, f"→ {r['recommended_hub_state']}", fontsize=9, va="center")
    fig.tight_layout()
    fig.savefig(FIGURES / "report_referral_distance_burden.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_telemedicine_components(tele: pd.DataFrame) -> None:
    """Stacked bar: top 12 telemedicine priority states with component breakdown."""
    top = tele.dropna(subset=["telemedicine_priority_score"]).head(12).sort_values(
        "telemedicine_priority_score", ascending=True
    )
    components = ["access_gap_component", "fragility_component", "rurality_component",
                  "digital_gap_component", "provider_shortage_component", "vulnerability_component"]
    labels = ["Access Gap (25%)", "Fragility (15%)", "Rurality (15%)",
              "Digital Gap (15%)", "Provider Shortage (15%)", "Vulnerability (15%)"]
    weights = [0.25, 0.15, 0.15, 0.15, 0.15, 0.15]
    contrib = top[components].fillna(0) * np.array(weights) * 100
    fig, ax = plt.subplots(figsize=(12, 6))
    bottom = np.zeros(len(top))
    colors = ["#e74c3c", "#e67e22", "#f39c12", "#3498db", "#9b59b6", "#1abc9c"]
    for i, (col, lbl) in enumerate(zip(components, labels)):
        ax.barh(top["STATE"], contrib[col], left=bottom, label=lbl, color=colors[i])
        bottom += contrib[col].values
    ax.set_xlabel("Telemedicine Priority Score (weighted components)", fontsize=11)
    ax.set_ylabel("State", fontsize=11)
    ax.set_title(
        "Telemedicine: Priority Score Breakdown for Top 12 States\n"
        "(Higher = greater need for telemedicine deployment)",
        fontsize=12,
    )
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "report_telemedicine_component_breakdown.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_telemedicine_priority_ranking(tele: pd.DataFrame) -> None:
    """Ranked horizontal bar: telemedicine priority score."""
    top = tele.dropna(subset=["telemedicine_priority_score"]).head(15).sort_values(
        "telemedicine_priority_score", ascending=True
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.YlOrRd(np.linspace(0.3, 0.95, len(top)))
    bars = ax.barh(top["STATE"], top["telemedicine_priority_score"], color=colors, edgecolor="white")
    for bar, (_, row) in zip(bars, top.iterrows()):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{row['telemedicine_priority_score']:.1f}", va="center", fontsize=8)
    ax.set_xlabel("Telemedicine Priority Score (0–100)", fontsize=11)
    ax.set_ylabel("State", fontsize=11)
    ax.set_title(
        "Telemedicine: Deployment Priority Ranking\n"
        "(Top states = highest expected impact from virtual specialist support)",
        fontsize=12,
    )
    fig.tight_layout()
    fig.savefig(FIGURES / "report_telemedicine_priority_ranking.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_capacity_fragility_heatmap(access: pd.DataFrame) -> None:
    """Heatmap-style: states with high fragility (single point of failure)."""
    fragile = access.nlargest(15, "capacity_loss_pct")[["STATE", "capacity_loss_pct", "total_beds_per_100k"]]
    fragile = fragile.sort_values("capacity_loss_pct", ascending=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(fragile))
    width = 0.35
    ax.barh(x - width / 2, fragile["capacity_loss_pct"], width, label="Capacity Fragility (%)", color="#e74c3c", alpha=0.8)
    ax.barh(x + width / 2, fragile["total_beds_per_100k"], width, label="Beds per 100k", color="#3498db", alpha=0.8)
    ax.set_yticks(x)
    ax.set_yticklabels(fragile["STATE"])
    ax.set_xlabel("Value", fontsize=11)
    ax.set_ylabel("State", fontsize=11)
    ax.set_title(
        "Equitable Access: High-Fragility States\n"
        "(Red = % capacity lost if largest facility fails; Blue = per-capita beds)",
        fontsize=12,
    )
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(FIGURES / "report_capacity_fragility_comparison.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# ── NEW Figure 1: Cross-Challenge Heatmap ────────────────────────────────────

def fig_cross_challenge_heatmap(access: pd.DataFrame, referral: pd.DataFrame, tele: pd.DataFrame) -> None:
    """
    Novel figure: Normalised heatmap of all states across all 3 challenge dimensions.
    Shows at a glance which states have compounding vulnerability across challenges.
    """
    # Build combined table
    df = access[["STATE", "total_beds_per_100k", "capacity_loss_pct"]].copy()

    # Access risk: lower beds → higher risk (min-max normalise, invert)
    df["access_risk"] = 1 - (df["total_beds_per_100k"] - df["total_beds_per_100k"].min()) / (
        df["total_beds_per_100k"].max() - df["total_beds_per_100k"].min()
    )

    # Fragility risk: already a 0-100 percent
    df["fragility_risk"] = df["capacity_loss_pct"] / 100.0

    # Referral dependency: 1 if state is referral-dependent, 0 otherwise
    referral_states = set(referral["origin_state"].tolist())
    df["referral_dependency"] = df["STATE"].apply(lambda s: 1.0 if s in referral_states else 0.0)

    # Telemedicine priority (normalised 0-1)
    tele_scores = tele.dropna(subset=["telemedicine_priority_score"])[["STATE", "telemedicine_priority_score"]].copy()
    tele_scores["tele_norm"] = tele_scores["telemedicine_priority_score"] / 100.0
    df = df.merge(tele_scores[["STATE", "tele_norm"]], on="STATE", how="left")
    df["tele_norm"] = df["tele_norm"].fillna(0)

    # Composite vulnerability (simple equal-weight average of 4 dimensions)
    df["composite"] = (df["access_risk"] + df["fragility_risk"] + df["referral_dependency"] + df["tele_norm"]) / 4.0
    df = df.sort_values("composite", ascending=False).head(20)

    heat_cols = ["access_risk", "fragility_risk", "referral_dependency", "tele_norm"]
    col_labels = ["Access\nRisk", "Capacity\nFragility", "Referral\nDependency", "Tele-\nPriority"]
    heat_data = df[heat_cols].values

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(heat_data, aspect="auto", cmap="RdYlGn_r", vmin=0, vmax=1)

    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_xticklabels(col_labels, fontsize=10, fontweight="bold")
    ax.set_yticks(np.arange(len(df)))
    ax.set_yticklabels(df["STATE"], fontsize=9)

    # Annotate cells
    for i in range(len(df)):
        for j in range(len(heat_cols)):
            v = heat_data[i, j]
            text_color = "white" if v > 0.65 else "black"
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    fontsize=8, color=text_color)

    cbar = plt.colorbar(im, ax=ax, shrink=0.6)
    cbar.set_label("Normalised Risk / Priority (0=low, 1=high)", fontsize=9)
    ax.set_title(
        "Cross-Challenge Vulnerability Heatmap: Top 20 States\n"
        "(States with red across all columns face compounding healthcare access challenges)",
        fontsize=12,
    )
    fig.tight_layout()
    fig.savefig(FIGURES / "report_cross_challenge_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  [OK] Cross-challenge heatmap saved.")


# ── NEW Figure 2: Population Exposure Bar ────────────────────────────────────

def fig_population_exposure(access: pd.DataFrame) -> None:
    """
    Shows the estimated population living in states at each access-tier level.
    Criterion 3: quantifies patient/population impact.
    """
    df = access.dropna(subset=["total_beds_per_100k", "population"]).copy()
    df["tier"] = pd.cut(
        df["total_beds_per_100k"],
        bins=[-np.inf, 50, 100, np.inf],
        labels=["Critical (<50 beds/100k)", "Moderate (50–100 beds/100k)", "Adequate (>100 beds/100k)"]
    )
    tier_pop = df.groupby("tier", observed=True)["population"].sum() / 1e6

    fig, ax = plt.subplots(figsize=(9, 5))
    tier_colors = {"Critical (<50 beds/100k)": "#e74c3c",
                   "Moderate (50–100 beds/100k)": "#e67e22",
                   "Adequate (>100 beds/100k)": "#2ecc71"}
    bars = ax.bar(tier_pop.index, tier_pop.values,
                  color=[tier_colors.get(str(t), "#aaa") for t in tier_pop.index],
                  edgecolor="white", width=0.5)
    for bar, val in zip(bars, tier_pop.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{val:.1f}M people", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_ylabel("Population (millions)", fontsize=11)
    ax.set_xlabel("Access Tier", fontsize=11)
    ax.set_title(
        "Equitable Access: Estimated Population by Capacity Tier\n"
        "(People living in states with critical, moderate, or adequate trauma/burn access)",
        fontsize=12,
    )
    ax.set_ylim(0, tier_pop.max() * 1.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "report_population_exposure.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  [OK] Population exposure figure saved.")


# ── NEW Figure 3: Referral Urgency Tiers ─────────────────────────────────────

def fig_referral_urgency_tiers(referral: pd.DataFrame, access: pd.DataFrame) -> None:
    """
    Enhanced referral chart with urgency tier colour bands and population labels.
    Criterion 3 + 8: quantified and polished.
    """
    if referral.empty:
        return

    # Join population for at-risk annotation
    pop_map = access.set_index("STATE")["population"].to_dict()
    ref = referral.copy()
    ref["population"] = ref["origin_state"].map(pop_map)
    ref = ref.sort_values("estimated_distance_km", ascending=True)

    def urgency(km):
        if km >= 1000:
            return "Immediate (>1,000 km)"
        elif km >= 200:
            return "Short-term (200–1,000 km)"
        else:
            return "Quick-win (<200 km)"

    ref["urgency"] = ref["estimated_distance_km"].apply(urgency)
    urgency_colors = {
        "Immediate (>1,000 km)": "#c0392b",
        "Short-term (200–1,000 km)": "#e67e22",
        "Quick-win (<200 km)": "#27ae60",
    }
    bar_colors = ref["urgency"].map(urgency_colors)

    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.barh(ref["origin_state"], ref["estimated_distance_km"],
                   color=bar_colors, edgecolor="white", height=0.6)

    for bar, (_, row) in zip(bars, ref.iterrows()):
        pop_str = f"{row['population'] / 1e6:.2f}M people" if pd.notna(row["population"]) else ""
        ax.text(bar.get_width() + 40, bar.get_y() + bar.get_height() / 2,
                f"→ {row['recommended_hub_state']}  {pop_str}",
                va="center", fontsize=9)

    # Urgency band lines
    ax.axvline(200, color="#27ae60", linestyle=":", linewidth=1.2, alpha=0.7)
    ax.axvline(1000, color="#c0392b", linestyle=":", linewidth=1.2, alpha=0.7)
    ax.text(210, -0.5, "200 km", fontsize=7, color="#27ae60", alpha=0.8)
    ax.text(1010, -0.5, "1,000 km", fontsize=7, color="#c0392b", alpha=0.8)

    patches = [mpatches.Patch(color=c, label=l) for l, c in urgency_colors.items()]
    ax.legend(handles=patches, loc="lower right", fontsize=8)
    ax.set_xlabel("Estimated Distance to Nearest Adult Burn Hub (km)", fontsize=11)
    ax.set_ylabel("Origin State (no adult burn center)", fontsize=11)
    ax.set_title(
        "Referral Networks: Transfer Burden by Urgency Tier\n"
        "(Color = protocol urgency; Labels show nearest hub state and at-risk population)",
        fontsize=12,
    )
    fig.tight_layout()
    fig.savefig(FIGURES / "report_referral_urgency_tiers.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  [OK] Referral urgency tiers figure saved.")


# ── Geographic map helpers ────────────────────────────────────────────────────

def _load_state_geometry():
    """Load US state boundaries. Returns None if unavailable."""
    if not HAS_GEOPANDAS:
        return None
    shp_path = DATA_EXTERNAL / "cb_2023_us_state_20m" / "cb_2023_us_state_20m.shp"
    zip_path = DATA_EXTERNAL / "cb_2023_us_state_20m.zip"
    try:
        if shp_path.exists():
            gdf = gpd.read_file(shp_path)
        elif zip_path.exists():
            gdf = gpd.read_file(f"zip://{zip_path}")
        else:
            return None
        gdf = gdf[["STUSPS", "geometry"]].rename(columns={"STUSPS": "STATE"})
        gdf = gdf[~gdf["STATE"].isin(["PR", "VI", "GU", "AS", "MP"])]
        return gdf
    except Exception:
        return None


def fig_equitable_access_map(access: pd.DataFrame) -> None:
    """US choropleth: beds per 100k by state."""
    gdf = _load_state_geometry()
    if gdf is None:
        return
    merged = gdf.merge(access[["STATE", "total_beds_per_100k"]], on="STATE", how="left")
    fig, ax = plt.subplots(figsize=(14, 8))
    merged.plot(ax=ax, column="total_beds_per_100k", cmap="YlGnBu", legend=True,
                legend_kwds={"label": "Beds per 100,000 Population", "shrink": 0.6},
                edgecolor="white", linewidth=0.3,
                missing_kwds={"color": "lightgray", "label": "No data"})
    ax.set_title("Equitable Access: Per-Capita Trauma/Burn Capacity by State\n"
                 "(Darker = higher capacity; Light = access gaps)", fontsize=12)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(FIGURES / "report_equitable_access_us_map.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_telemedicine_map(tele: pd.DataFrame) -> None:
    """US choropleth: telemedicine priority score by state."""
    gdf = _load_state_geometry()
    if gdf is None:
        return
    merged = gdf.merge(tele[["STATE", "telemedicine_priority_score"]], on="STATE", how="left")
    fig, ax = plt.subplots(figsize=(14, 8))
    merged.plot(ax=ax, column="telemedicine_priority_score", cmap="YlOrRd", legend=True,
                legend_kwds={"label": "Telemedicine Priority Score (0–100)", "shrink": 0.6},
                edgecolor="white", linewidth=0.3,
                missing_kwds={"color": "lightgray", "label": "No data"})
    ax.set_title("Telemedicine: Deployment Priority by State\n"
                 "(Darker = higher priority; Top states for virtual specialist pilots)", fontsize=12)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(FIGURES / "report_telemedicine_us_map.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_referral_map(referral: pd.DataFrame) -> None:
    """US map: origin states (no burn center) highlighted with hub labels."""
    gdf = _load_state_geometry()
    if gdf is None or referral.empty:
        return
    gdf = gdf.merge(referral[["origin_state", "recommended_hub_state", "estimated_distance_km"]],
                    left_on="STATE", right_on="origin_state", how="left")
    gdf["is_referral_origin"] = gdf["origin_state"].notna()
    fig, ax = plt.subplots(figsize=(14, 8))
    gdf.plot(ax=ax, color="lightgray", edgecolor="white", linewidth=0.3)
    gdf[gdf["is_referral_origin"]].plot(ax=ax, color="#e74c3c", edgecolor="darkred",
                                         linewidth=0.8, alpha=0.7,
                                         label="Referral-dependent (no burn center)")
    for _, row in gdf[gdf["is_referral_origin"]].iterrows():
        centroid = row["geometry"].centroid
        ax.annotate(
            f"{row['STATE']}→{row['recommended_hub_state']}\n{int(row['estimated_distance_km'])} km",
            xy=(centroid.x, centroid.y), fontsize=8, ha="center", va="center",
        )
    ax.set_title("Referral Networks: States Without Burn Centers and Nearest Hub\n"
                 "(Red = referral-dependent; Label = destination state and distance)", fontsize=12)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(FIGURES / "report_referral_us_map.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    access, referral, tele = load_data()

    print("Generating original figures...")
    fig_equitable_access_disparity(access)
    fig_equitable_access_ranked(access)
    fig_capacity_fragility_heatmap(access)
    fig_equitable_access_map(access)
    fig_referral_distance_burden(referral)
    fig_referral_map(referral)
    fig_telemedicine_components(tele)
    fig_telemedicine_priority_ranking(tele)
    fig_telemedicine_map(tele)

    print("Generating new judge-targeted figures...")
    fig_cross_challenge_heatmap(access, referral, tele)
    fig_population_exposure(access)
    fig_referral_urgency_tiers(referral, access)

    print("\nAll figures written to docs/figures/")


if __name__ == "__main__":
    main()
