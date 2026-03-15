"""
Generate all visualizations for the three narrative challenge-area reports.

The figures follow a two-phase structure per challenge:
  Phase A  -- Foundation figures from the NIRD dataset alone.
  Phase B  -- Enriched figures after joining external datasets.

Run from project root:
    python scripts/generate_narrative_figures.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

try:
    import geopandas as gpd
    HAS_GEO = True
except ImportError:
    HAS_GEO = False

from src.data_loading import load_clean_hospital_data

DATA_EXT = ROOT / "data" / "external"
OUTPUTS  = ROOT / "outputs"
FIG_DIR  = ROOT / "docs" / "figures"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.20,
    "grid.linestyle": "--",
    "figure.dpi": 150,
})

def _state_gdf():
    if not HAS_GEO:
        return None
    shp = DATA_EXT / "cb_2023_us_state_20m" / "cb_2023_us_state_20m.shp"
    zp  = DATA_EXT / "cb_2023_us_state_20m.zip"
    try:
        if shp.exists():
            g = gpd.read_file(shp)
        elif zp.exists():
            g = gpd.read_file(f"zip://{zp}")
        else:
            return None
        g = g[["STUSPS","NAME","geometry"]].rename(columns={"STUSPS":"STATE"})
        g = g[~g["STATE"].isin(["PR","VI","GU","AS","MP"])]
        return g
    except Exception:
        return None


# ── EQUITABLE ACCESS -- Foundation ───────────────────────────────────
def ea_fig1_facility_distribution(df):
    cnt = df.groupby("STATE").size().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(10, 11))
    ax.barh(cnt.index, cnt.values, color="#2980b9", edgecolor="white", linewidth=0.3)
    ax.set_xlabel("Number of NIRD Facilities", fontsize=11)
    ax.set_title("NIRD Dataset: Trauma & Burn Facility Count by State", fontsize=13, fontweight="bold")
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_ea_facility_count.png", bbox_inches="tight"); plt.close(fig)

def ea_fig2_bed_distribution(df):
    beds = df["TOTAL_BEDS"].dropna()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
    ax1.hist(beds, bins=40, color="#2980b9", edgecolor="white", alpha=0.85)
    ax1.set_ylabel("Number of Facilities")
    ax1.set_title("NIRD Dataset: Distribution of Total Beds per Facility", fontsize=13, fontweight="bold")
    ax2.boxplot(beds, vert=False, widths=0.6, boxprops=dict(color="#2980b9"), medianprops=dict(color="#e74c3c", linewidth=2))
    ax2.set_xlabel("Total Beds")
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_ea_bed_distribution.png", bbox_inches="tight"); plt.close(fig)

def ea_fig3_capability_matrix(df):
    by_st = df.groupby("STATE").agg(
        trauma_adult=("TRAUMA_ADULT", lambda s: (s == True).sum()),
        burn_adult=("BURN_ADULT", lambda s: (s == True).sum()),
        facilities=("STATE", "size"),
    ).reset_index()
    by_st = by_st.nlargest(20, "facilities").sort_values("facilities", ascending=True)
    x = np.arange(len(by_st)); w = 0.35
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(x - w/2, by_st["trauma_adult"], w, label="Adult Trauma Centers", color="#2980b9")
    ax.barh(x + w/2, by_st["burn_adult"], w, label="Adult Burn Centers", color="#e74c3c")
    ax.set_yticks(x); ax.set_yticklabels(by_st["STATE"])
    ax.set_xlabel("Number of Centers", fontsize=11)
    ax.set_title("NIRD Dataset: Trauma vs Burn Capability (Top 20 States)", fontsize=12, fontweight="bold")
    ax.legend(loc="lower right")
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_ea_capability_matrix.png", bbox_inches="tight"); plt.close(fig)

def ea_fig4_burn_gap(df):
    by_st = df.groupby("STATE")["BURN_ADULT"].apply(lambda s: (s == True).sum()).reset_index()
    by_st.columns = ["STATE", "burn_count"]
    has_b = (by_st["burn_count"] > 0).sum(); no_b = (by_st["burn_count"] == 0).sum()
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie([has_b, no_b], labels=[f"Has Burn Center ({has_b})", f"No Burn Center ({no_b})"],
           colors=["#2ecc71", "#e74c3c"], autopct="%1.0f%%", startangle=140, textprops={"fontsize": 12})
    ax.set_title("NIRD Initial Finding:\nStates With vs Without Adult Burn Centers", fontsize=13, fontweight="bold")
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_ea_burn_gap_pie.png", bbox_inches="tight"); plt.close(fig)


# ── EQUITABLE ACCESS -- Enriched ─────────────────────────────────────
def ea_fig5_percapita_ranked(access):
    acc = access.sort_values("total_beds_per_100k", ascending=True)
    colors = ["#e74c3c" if x < 50 else "#e67e22" if x < 100 else "#2ecc71" for x in acc["total_beds_per_100k"]]
    fig, ax = plt.subplots(figsize=(10, 11))
    ax.barh(acc["STATE"], acc["total_beds_per_100k"], color=colors, edgecolor="white", linewidth=0.3)
    ax.axvline(100, color="black", ls="--", lw=1)
    ax.set_xlabel("Total Beds per 100,000 Population", fontsize=11)
    ax.set_title("Enriched Finding: Per-Capita Capacity Ranking\n(Red <50 | Orange 50-100 | Green >100)", fontsize=12, fontweight="bold")
    patches = [mpatches.Patch(color=c, label=l) for c, l in [("#e74c3c","Critical (<50)"),("#e67e22","Moderate (50-100)"),("#2ecc71","Adequate (>100)")]]
    ax.legend(handles=patches, loc="lower right", fontsize=9)
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_ea_percapita_ranked.png", bbox_inches="tight"); plt.close(fig)

def ea_fig6_fragility_scatter(access):
    acc = access.dropna(subset=["total_beds_per_100k","capacity_loss_pct","population"]).copy()
    acc["pop_m"] = acc["population"] / 1e6
    fig, ax = plt.subplots(figsize=(11, 7))
    sc = ax.scatter(acc["total_beds_per_100k"], acc["capacity_loss_pct"], s=acc["pop_m"]*8, c=acc["adult_burn_centers"], cmap="YlOrRd", alpha=0.75, edgecolors="gray", linewidths=0.5)
    cb = plt.colorbar(sc, ax=ax, shrink=0.7); cb.set_label("Adult Burn Centers")
    med = acc["total_beds_per_100k"].median()
    ax.axvline(med, color="gray", ls="--", alpha=0.5, label=f"Median ({med:.0f})")
    ax.axhline(50, color="gray", ls="--", alpha=0.5, label="50% fragility line")
    for _, r in acc.nlargest(8, "capacity_loss_pct").iterrows():
        ax.annotate(r["STATE"], (r["total_beds_per_100k"], r["capacity_loss_pct"]), fontsize=8, fontweight="bold")
    ax.set_xlabel("Total Beds per 100k Population"); ax.set_ylabel("Capacity Fragility (%)")
    ax.set_title("Enriched Finding: Access vs Fragility\n(bubble=population, color=burn centers)", fontsize=12, fontweight="bold")
    ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_ea_fragility_scatter.png", bbox_inches="tight"); plt.close(fig)

def ea_fig7_population_exposure(access):
    acc = access.dropna(subset=["total_beds_per_100k","population"]).copy()
    acc["tier"] = pd.cut(acc["total_beds_per_100k"], bins=[-np.inf, 50, 100, np.inf], labels=["Critical (<50)", "Moderate (50-100)", "Adequate (>100)"])
    tp = acc.groupby("tier", observed=True)["population"].sum() / 1e6
    colors = {"Critical (<50)":"#e74c3c","Moderate (50-100)":"#e67e22","Adequate (>100)":"#2ecc71"}
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(tp.index, tp.values, color=[colors.get(str(t),"#aaa") for t in tp.index], edgecolor="white", width=0.5)
    for b, v in zip(bars, tp.values):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.5, f"{v:.1f}M", ha="center", fontsize=11, fontweight="bold")
    ax.set_ylabel("Population (millions)")
    ax.set_title("Enriched Finding: Population Exposure by Access Tier", fontsize=12, fontweight="bold")
    ax.set_ylim(0, tp.max()*1.25)
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_ea_population_tier.png", bbox_inches="tight"); plt.close(fig)

def ea_fig8_map(access):
    gdf = _state_gdf()
    if gdf is None: return
    m = gdf.merge(access[["STATE","total_beds_per_100k"]], on="STATE", how="left")
    fig, ax = plt.subplots(figsize=(14, 8))
    m.plot(ax=ax, column="total_beds_per_100k", cmap="YlGnBu", legend=True, legend_kwds={"label":"Beds per 100k","shrink":0.55}, edgecolor="white", linewidth=0.3, missing_kwds={"color":"lightgray"})
    ax.set_title("Enriched Finding: Per-Capita Trauma/Burn Capacity by State", fontsize=13, fontweight="bold")
    ax.axis("off")
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_ea_us_map.png", bbox_inches="tight"); plt.close(fig)


# ── REFERRAL NETWORKS -- In-State Burn Center Mapping ────────────────
def rn_fig0a_instate_detail(df):
    """Per-state: burn centres count (left) and burn beds (right) -- map the in-state picture first."""
    by_st = df.groupby("STATE").agg(
        burn_centers=("BURN_ADULT", lambda s: (s == True).sum()),
        burn_beds=("BURN_BEDS", "sum"),
        total_beds=("TOTAL_BEDS", "sum"),
    ).reset_index()
    by_st = by_st.sort_values("burn_centers", ascending=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 11), sharey=True)
    c1 = ["#e74c3c" if x == 0 else "#e67e22" if x <= 2 else "#2ecc71" for x in by_st["burn_centers"]]
    ax1.barh(by_st["STATE"], by_st["burn_centers"], color=c1, edgecolor="white")
    ax1.set_xlabel("Adult Burn Centers", fontsize=11)
    ax1.set_title("In-State Burn Centers", fontsize=12, fontweight="bold")
    for i, (_, r) in enumerate(by_st.iterrows()):
        if r["burn_centers"] > 0:
            ax1.text(r["burn_centers"]+0.1, i, str(int(r["burn_centers"])), va="center", fontsize=7)
    c2 = ["#e74c3c" if x == 0 else "#3498db" for x in by_st["burn_beds"]]
    ax2.barh(by_st["STATE"], by_st["burn_beds"], color=c2, edgecolor="white")
    ax2.set_xlabel("Dedicated Burn Beds", fontsize=11)
    ax2.set_title("In-State Burn Beds", fontsize=12, fontweight="bold")
    for i, (_, r) in enumerate(by_st.iterrows()):
        if r["burn_beds"] > 0:
            ax2.text(r["burn_beds"]+0.5, i, str(int(r["burn_beds"])), va="center", fontsize=7)
    fig.suptitle("NIRD Dataset: In-State Burn Care Infrastructure\n"
                 "(Map what exists locally BEFORE considering out-of-state referrals)",
                 fontsize=13, fontweight="bold", y=1.01)
    patches = [mpatches.Patch(color="#e74c3c", label="Zero (referral-dependent)"),
               mpatches.Patch(color="#e67e22", label="1-2 centres (fragile)"),
               mpatches.Patch(color="#2ecc71", label="3+ centres")]
    ax1.legend(handles=patches, loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "narr_rn_instate_detail.png", bbox_inches="tight"); plt.close(fig)

def rn_fig0b_burn_specialisation(df):
    """Burn beds as % of total beds -- measures how specialised each state's system is."""
    by_st = df.groupby("STATE").agg(burn_beds=("BURN_BEDS", "sum"), total_beds=("TOTAL_BEDS", "sum"),
                                     burn_centers=("BURN_ADULT", lambda s: (s == True).sum())).reset_index()
    by_st = by_st[by_st["burn_centers"] > 0].copy()
    by_st["burn_pct"] = (by_st["burn_beds"] / by_st["total_beds"]) * 100
    by_st = by_st.sort_values("burn_pct", ascending=True)
    fig, ax = plt.subplots(figsize=(10, 9))
    colors = plt.cm.YlOrRd(np.linspace(0.2, 0.9, len(by_st)))
    ax.barh(by_st["STATE"], by_st["burn_pct"], color=colors, edgecolor="white")
    for i, (_, r) in enumerate(by_st.iterrows()):
        ax.text(r["burn_pct"]+0.05, i, f'{r["burn_pct"]:.1f}%  ({int(r["burn_beds"])} beds)', va="center", fontsize=7)
    ax.set_xlabel("Burn Beds as % of Total State Beds", fontsize=11)
    ax.set_title("NIRD Initial Finding: Burn Specialisation Ratio by State\n"
                 "(Higher % = more dedicated burn infrastructure relative to total capacity)",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_rn_burn_specialisation.png", bbox_inches="tight"); plt.close(fig)

def rn_fig0c_largest_burn_facility(df):
    """Largest burn facility per state -- the anchor institution for in-state burn care."""
    burn_fac = df[df["BURN_ADULT"] == True].copy()
    if burn_fac.empty: return
    burn_fac["BURN_BEDS"] = pd.to_numeric(burn_fac["BURN_BEDS"], errors="coerce").fillna(0)
    idx = burn_fac.groupby("STATE")["BURN_BEDS"].idxmax()
    largest = burn_fac.loc[idx, ["STATE", "HOSPITAL_NAME", "BURN_BEDS", "CITY"]].copy()
    largest["label"] = largest["HOSPITAL_NAME"].str[:40] + " (" + largest["CITY"].str.strip() + ")"
    largest = largest.sort_values("BURN_BEDS", ascending=True)
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.barh(largest["STATE"], largest["BURN_BEDS"], color="#e67e22", edgecolor="white")
    for i, (_, r) in enumerate(largest.iterrows()):
        ax.text(r["BURN_BEDS"]+0.5, i, r["label"], va="center", fontsize=6.5)
    ax.set_xlabel("Burn Beds at Largest Facility", fontsize=11)
    ax.set_title("NIRD Initial Finding: Largest Burn Facility per State\n"
                 "(Anchor institution for in-state burn care)", fontsize=12, fontweight="bold")
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_rn_largest_burn_facility.png", bbox_inches="tight"); plt.close(fig)


# ── REFERRAL NETWORKS -- Foundation: Coverage Gaps ───────────────────
def rn_fig1_burn_state_map(df):
    by_st = df.groupby("STATE")["BURN_ADULT"].apply(lambda s: (s == True).sum()).reset_index()
    by_st.columns = ["STATE","count"]; by_st["has_burn"] = by_st["count"] > 0
    gdf = _state_gdf()
    if gdf is None: return
    m = gdf.merge(by_st, on="STATE", how="left")
    m["has_burn"] = m["has_burn"].fillna(False)
    fig, ax = plt.subplots(figsize=(14, 8))
    m[m["has_burn"]==False].plot(ax=ax, color="#e74c3c", edgecolor="darkred", linewidth=0.8, alpha=0.7)
    m[m["has_burn"]==True].plot(ax=ax, color="#2ecc71", edgecolor="white", linewidth=0.3, alpha=0.6)
    patches = [mpatches.Patch(color="#e74c3c", label="No Adult Burn Center"), mpatches.Patch(color="#2ecc71", label="Has Adult Burn Center")]
    ax.legend(handles=patches, fontsize=10, loc="lower left")
    ax.set_title("NIRD Initial Finding: Burn Center Coverage Gaps Across the US", fontsize=13, fontweight="bold")
    ax.axis("off")
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_rn_burn_coverage_map.png", bbox_inches="tight"); plt.close(fig)

def rn_fig2_burn_beds_concentration(df):
    by_st = df.groupby("STATE")["BURN_BEDS"].sum().sort_values(ascending=True)
    by_st = by_st[by_st > 0]
    fig, ax = plt.subplots(figsize=(10, 9))
    ax.barh(by_st.index, by_st.values, color="#e67e22", edgecolor="white")
    ax.set_xlabel("Total Burn Beds", fontsize=11)
    ax.set_title("NIRD Initial Finding: Burn Bed Concentration by State\n(States with zero burn beds not shown)", fontsize=12, fontweight="bold")
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_rn_burn_beds_concentration.png", bbox_inches="tight"); plt.close(fig)


# ── REFERRAL NETWORKS -- Enriched ────────────────────────────────────
def rn_fig3_referral_urgency(referral, access):
    if referral.empty: return
    pop_map = access.set_index("STATE")["population"].to_dict()
    ref = referral.copy(); ref["population"] = ref["origin_state"].map(pop_map)
    ref = ref.sort_values("estimated_distance_km", ascending=True)
    def urg(km):
        if km >= 1000: return "Immediate (>1000 km)"
        if km >= 200:  return "Short-term (200-1000 km)"
        return "Quick-win (<200 km)"
    ref["urgency"] = ref["estimated_distance_km"].apply(urg)
    uc = {"Immediate (>1000 km)":"#c0392b","Short-term (200-1000 km)":"#e67e22","Quick-win (<200 km)":"#27ae60"}
    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.barh(ref["origin_state"], ref["estimated_distance_km"], color=ref["urgency"].map(uc), edgecolor="white", height=0.6)
    for bar, (_, row) in zip(bars, ref.iterrows()):
        pop_s = f"{row['population']/1e6:.2f}M" if pd.notna(row["population"]) else ""
        ax.text(bar.get_width()+40, bar.get_y()+bar.get_height()/2, f"-> {row['recommended_hub_state']}  {pop_s}", va="center", fontsize=9)
    ax.axvline(200, color="#27ae60", ls=":", lw=1.2, alpha=0.7); ax.axvline(1000, color="#c0392b", ls=":", lw=1.2, alpha=0.7)
    patches = [mpatches.Patch(color=c, label=l) for l, c in uc.items()]
    ax.legend(handles=patches, loc="lower right", fontsize=8)
    ax.set_xlabel("Distance to Nearest Hub (km)")
    ax.set_title("Enriched Finding: Referral Burden by Urgency Tier\n(labels = nearest hub + at-risk population)", fontsize=12, fontweight="bold")
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_rn_urgency_tiers.png", bbox_inches="tight"); plt.close(fig)

def rn_fig4_referral_map(referral):
    gdf = _state_gdf()
    if gdf is None or referral.empty: return
    m = gdf.merge(referral[["origin_state","recommended_hub_state","estimated_distance_km"]], left_on="STATE", right_on="origin_state", how="left")
    m["is_dep"] = m["origin_state"].notna()
    fig, ax = plt.subplots(figsize=(14, 8))
    m.plot(ax=ax, color="lightgray", edgecolor="white", linewidth=0.3)
    m[m["is_dep"]].plot(ax=ax, color="#e74c3c", edgecolor="darkred", linewidth=0.8, alpha=0.7)
    for _, r in m[m["is_dep"]].iterrows():
        c = r["geometry"].centroid
        ax.annotate(f"{r['STATE']}->{r['recommended_hub_state']}\n{int(r['estimated_distance_km'])} km",
                    xy=(c.x, c.y), fontsize=8, ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7))
    ax.set_title("Enriched Finding: Referral-Dependent States and Nearest Hub Assignments", fontsize=13, fontweight="bold")
    ax.axis("off")
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_rn_referral_map.png", bbox_inches="tight"); plt.close(fig)


# ── TELEMEDICINE -- Foundation ───────────────────────────────────────
def tm_fig1_access_vs_fragility(access):
    acc = access.sort_values("total_beds_per_100k", ascending=True).head(20)
    fig, ax1 = plt.subplots(figsize=(10, 7)); x = np.arange(len(acc))
    ax1.bar(x, acc["total_beds_per_100k"], color="#3498db", alpha=0.8, label="Beds per 100k")
    ax1.set_ylabel("Beds per 100k", color="#3498db"); ax1.set_xticks(x); ax1.set_xticklabels(acc["STATE"], rotation=45, ha="right")
    ax2 = ax1.twinx()
    ax2.plot(x, acc["capacity_loss_pct"], "o-", color="#e74c3c", lw=2, label="Fragility %")
    ax2.set_ylabel("Capacity Fragility (%)", color="#e74c3c")
    ax1.set_title("NIRD Initial Finding: Low-Access States Often Have High Fragility\n(Bottom 20 states by per-capita beds)", fontsize=12, fontweight="bold")
    lines1, labels1 = ax1.get_legend_handles_labels(); lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1+lines2, labels1+labels2, loc="upper left", fontsize=9)
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_tm_access_fragility.png", bbox_inches="tight"); plt.close(fig)

def tm_fig2_burn_trauma_gap(df):
    by_st = df.groupby("STATE").apply(
        lambda g: pd.Series({
            "trauma_only": ((g["TRAUMA_ADULT"]==True) & (g["BURN_ADULT"]!=True)).sum(),
            "both": ((g["TRAUMA_ADULT"]==True) & (g["BURN_ADULT"]==True)).sum(),
            "burn_only": ((g["TRAUMA_ADULT"]!=True) & (g["BURN_ADULT"]==True)).sum(),
        }), include_groups=False
    ).reset_index()
    by_st = by_st.sort_values("both", ascending=True).tail(20); x = np.arange(len(by_st))
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(x, by_st["trauma_only"], label="Trauma Only", color="#3498db")
    ax.barh(x, by_st["both"], left=by_st["trauma_only"], label="Trauma + Burn", color="#2ecc71")
    ax.barh(x, by_st["burn_only"], left=by_st["trauma_only"]+by_st["both"], label="Burn Only", color="#e74c3c")
    ax.set_yticks(x); ax.set_yticklabels(by_st["STATE"]); ax.set_xlabel("Facilities")
    ax.set_title("NIRD Initial Finding: Trauma-Only vs Dual-Capable Facilities\n(Top 20 states)", fontsize=12, fontweight="bold")
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_tm_trauma_burn_gap.png", bbox_inches="tight"); plt.close(fig)


# ── TELEMEDICINE -- Enriched ─────────────────────────────────────────
def tm_fig3_priority_components(tele):
    top = tele.dropna(subset=["telemedicine_priority_score"]).head(12).sort_values("telemedicine_priority_score", ascending=True)
    comps = ["access_gap_component","fragility_component","rurality_component","digital_gap_component","provider_shortage_component","vulnerability_component"]
    labels = ["Access Gap (25%)","Fragility (15%)","Rurality (15%)","Digital Gap (15%)","Provider Shortage (15%)","Vulnerability (15%)"]
    wts = [0.25,0.15,0.15,0.15,0.15,0.15]
    contrib = top[comps].fillna(0) * np.array(wts) * 100
    cs = ["#e74c3c","#e67e22","#f39c12","#3498db","#9b59b6","#1abc9c"]
    fig, ax = plt.subplots(figsize=(12, 6)); bottom = np.zeros(len(top))
    for i, (col, lbl) in enumerate(zip(comps, labels)):
        ax.barh(top["STATE"], contrib[col], left=bottom, label=lbl, color=cs[i]); bottom += contrib[col].values
    ax.set_xlabel("Telemedicine Priority Score (weighted components)")
    ax.set_title("Enriched Finding: Telemedicine Priority -- Component Breakdown\n(6 external data sources combined)", fontsize=12, fontweight="bold")
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_tm_priority_components.png", bbox_inches="tight"); plt.close(fig)

def tm_fig4_priority_ranking(tele):
    top = tele.dropna(subset=["telemedicine_priority_score"]).head(15).sort_values("telemedicine_priority_score", ascending=True)
    colors = plt.cm.YlOrRd(np.linspace(0.3, 0.95, len(top)))
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(top["STATE"], top["telemedicine_priority_score"], color=colors, edgecolor="white")
    for b, (_, r) in zip(bars, top.iterrows()):
        ax.text(b.get_width()+0.5, b.get_y()+b.get_height()/2, f"{r['telemedicine_priority_score']:.1f}", va="center", fontsize=8)
    ax.set_xlabel("Telemedicine Priority Score (0-100)")
    ax.set_title("Enriched Finding: Telemedicine Deployment Priority Ranking", fontsize=12, fontweight="bold")
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_tm_priority_ranking.png", bbox_inches="tight"); plt.close(fig)

def tm_fig5_tele_map(tele):
    gdf = _state_gdf()
    if gdf is None: return
    m = gdf.merge(tele[["STATE","telemedicine_priority_score"]], on="STATE", how="left")
    fig, ax = plt.subplots(figsize=(14, 8))
    m.plot(ax=ax, column="telemedicine_priority_score", cmap="YlOrRd", legend=True, legend_kwds={"label":"Telemedicine Priority Score","shrink":0.55}, edgecolor="white", linewidth=0.3, missing_kwds={"color":"lightgray"})
    ax.set_title("Enriched Finding: Telemedicine Deployment Priority by State", fontsize=13, fontweight="bold")
    ax.axis("off")
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_tm_us_map.png", bbox_inches="tight"); plt.close(fig)


# ── CROSS-CHALLENGE heatmap ──────────────────────────────────────────
def cross_fig_heatmap(access, referral, tele):
    df = access[["STATE","total_beds_per_100k","capacity_loss_pct"]].copy()
    rng = df["total_beds_per_100k"].max() - df["total_beds_per_100k"].min()
    if rng == 0: rng = 1
    df["access_risk"] = 1-(df["total_beds_per_100k"]-df["total_beds_per_100k"].min())/rng
    df["fragility_risk"] = df["capacity_loss_pct"]/100.0
    ref_set = set(referral["origin_state"].tolist()) if not referral.empty else set()
    df["referral_dep"] = df["STATE"].apply(lambda s: 1.0 if s in ref_set else 0.0)
    ts = tele.dropna(subset=["telemedicine_priority_score"])[["STATE","telemedicine_priority_score"]].copy()
    ts["tele_norm"] = ts["telemedicine_priority_score"]/100.0
    df = df.merge(ts[["STATE","tele_norm"]], on="STATE", how="left").fillna(0)
    df["composite"] = (df["access_risk"]+df["fragility_risk"]+df["referral_dep"]+df["tele_norm"])/4
    df = df.sort_values("composite", ascending=False).head(20)
    cols = ["access_risk","fragility_risk","referral_dep","tele_norm"]
    labs = ["Access\nRisk","Capacity\nFragility","Referral\nDependency","Tele-\nPriority"]
    data = df[cols].values
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(data, aspect="auto", cmap="RdYlGn_r", vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(labs))); ax.set_xticklabels(labs, fontsize=10, fontweight="bold")
    ax.set_yticks(np.arange(len(df))); ax.set_yticklabels(df["STATE"], fontsize=9)
    for i in range(len(df)):
        for j in range(len(cols)):
            v = data[i,j]; ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8, color="white" if v > 0.65 else "black")
    cb = plt.colorbar(im, ax=ax, shrink=0.6); cb.set_label("Normalised Risk (0=low, 1=high)")
    ax.set_title("Cross-Challenge Vulnerability Heatmap: Top 20 States\n(Red across all columns = compounding challenges)", fontsize=12, fontweight="bold")
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_cross_challenge_heatmap.png", bbox_inches="tight"); plt.close(fig)


# ── BURN FATALITY DATA (CDC WISQARS 2023) ────────────────────────────
_STATE_ABBREV = {
    "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA",
    "Colorado":"CO","Connecticut":"CT","Delaware":"DE","District of Columbia":"DC",
    "Florida":"FL","Georgia":"GA","Hawaii":"HI","Idaho":"ID","Illinois":"IL",
    "Indiana":"IN","Iowa":"IA","Kansas":"KS","Kentucky":"KY","Louisiana":"LA",
    "Maine":"ME","Maryland":"MD","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN",
    "Mississippi":"MS","Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV",
    "New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM","New York":"NY",
    "North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK","Oregon":"OR",
    "Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC","South Dakota":"SD",
    "Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA",
    "Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY",
}

def _load_fatal_data():
    """Load and clean CDC WISQARS fatal burn data."""
    fp = DATA_EXT / "fatal_report_per_state.csv"
    if not fp.exists():
        return None
    df = pd.read_csv(fp)
    # Keep only state rows (exclude Total and metadata)
    df = df[df["State"].isin(_STATE_ABBREV.keys())].copy()
    df["STATE"] = df["State"].map(_STATE_ABBREV)
    # Clean numeric columns -- remove ** markers and commas, convert --
    for col in ["Deaths", "Population", "Crude Rate", "Age-Adjusted Rate", "Years of Potential Life Lost"]:
        df[col] = df[col].astype(str).str.replace("**", "", regex=False).str.replace(",", "", regex=False)
        df[col] = df[col].replace("--", np.nan)
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.rename(columns={
        "Deaths": "burn_deaths",
        "Population": "fatal_pop",
        "Crude Rate": "burn_death_rate",
        "Age-Adjusted Rate": "burn_death_rate_adj",
        "Years of Potential Life Lost": "burn_ypll",
    })
    return df[["STATE","burn_deaths","fatal_pop","burn_death_rate","burn_death_rate_adj","burn_ypll"]].dropna(subset=["STATE"])


# ── EA: Fatality Rate Ranking ────────────────────────────────────────
def fatal_fig1_rate_ranking(fatal):
    """Horizontal bar: burn fatality crude rate per state, colour-coded by severity."""
    df = fatal.dropna(subset=["burn_death_rate"]).sort_values("burn_death_rate", ascending=True)
    colors = ["#e74c3c" if r >= 2.0 else "#e67e22" if r >= 1.0 else "#2ecc71" for r in df["burn_death_rate"]]
    fig, ax = plt.subplots(figsize=(10, 11))
    ax.barh(df["STATE"], df["burn_death_rate"], color=colors, edgecolor="white", linewidth=0.3)
    ax.axvline(1.19, color="black", ls="--", lw=1, alpha=0.6)
    ax.set_xlabel("Fire/Burn Deaths per 100,000 Population (2023)", fontsize=11)
    ax.set_title("CDC WISQARS: Burn Fatality Rate by State\n(Dashed line = national average 1.19 | Red >= 2.0 | Orange >= 1.0)",
                 fontsize=12, fontweight="bold")
    patches = [mpatches.Patch(color=c, label=l) for c, l in
               [("#e74c3c","High (>=2.0)"),("#e67e22","Moderate (1.0-2.0)"),("#2ecc71","Low (<1.0)")]]
    ax.legend(handles=patches, loc="lower right", fontsize=9)
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_fatal_rate_ranking.png", bbox_inches="tight"); plt.close(fig)


# ── EA: Demand vs Supply Scatter ─────────────────────────────────────
def fatal_fig2_demand_supply(fatal, access):
    """Scatter: burn fatality rate (demand proxy) vs beds per 100k (supply).
       States in upper-left quadrant = high demand, low supply = most underserved."""
    merged = access.merge(fatal[["STATE","burn_death_rate","burn_deaths"]], on="STATE", how="inner")
    merged = merged.dropna(subset=["burn_death_rate","total_beds_per_100k"])
    fig, ax = plt.subplots(figsize=(11, 8))
    sc = ax.scatter(merged["total_beds_per_100k"], merged["burn_death_rate"],
                    s=merged["burn_deaths"].fillna(0)*1.5, alpha=0.7,
                    c=merged["adult_burn_centers"], cmap="YlOrRd",
                    edgecolors="gray", linewidths=0.5)
    cb = plt.colorbar(sc, ax=ax, shrink=0.6); cb.set_label("Adult Burn Centers")
    # Quadrant lines
    med_x = merged["total_beds_per_100k"].median()
    med_y = merged["burn_death_rate"].median()
    ax.axvline(med_x, color="gray", ls="--", alpha=0.4)
    ax.axhline(med_y, color="gray", ls="--", alpha=0.4)
    ax.text(med_x*0.15, merged["burn_death_rate"].max()*0.95,
            "CRITICAL\nHigh Demand\nLow Supply", ha="center", fontsize=9,
            color="#c0392b", fontweight="bold",
            bbox=dict(fc="white", alpha=0.7, boxstyle="round"))
    # Label extreme states
    extreme = merged.nlargest(8, "burn_death_rate")
    for _, r in extreme.iterrows():
        ax.annotate(r["STATE"], (r["total_beds_per_100k"], r["burn_death_rate"]),
                    fontsize=8, fontweight="bold",
                    xytext=(5, 5), textcoords="offset points")
    ax.set_xlabel("Beds per 100k Population (Supply)", fontsize=11)
    ax.set_ylabel("Burn Deaths per 100k (Demand Proxy)", fontsize=11)
    ax.set_title("Demand vs Supply: Burn Fatality Rate vs Per-Capita Capacity\n"
                 "(Bubble size = total deaths | Upper-left = most underserved)",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_fatal_demand_supply.png", bbox_inches="tight"); plt.close(fig)


# ── RN: Referral-Dependent State Fatality Burden ─────────────────────
def fatal_fig3_referral_burden(fatal, referral):
    """Bar chart: burn fatalities in referral-dependent states --
       these deaths occur in states with NO in-state burn centre."""
    if referral.empty:
        return
    dep_states = set(referral["origin_state"].tolist())
    dep_fatal = fatal[fatal["STATE"].isin(dep_states)].dropna(subset=["burn_deaths"]).copy()
    dep_fatal = dep_fatal.sort_values("burn_deaths", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(dep_fatal["STATE"], dep_fatal["burn_deaths"], color="#c0392b", edgecolor="white")
    for b, (_, r) in zip(bars, dep_fatal.iterrows()):
        rate_str = f" (rate: {r['burn_death_rate']:.1f})" if pd.notna(r["burn_death_rate"]) else ""
        ax.text(b.get_width()+1, b.get_y()+b.get_height()/2, f"{int(r['burn_deaths'])}{rate_str}",
                va="center", fontsize=9)
    ax.set_xlabel("Burn Deaths (2023)", fontsize=11)
    ax.set_title("Burn Fatalities in Referral-Dependent States\n"
                 "(These patients had NO in-state burn centre)", fontsize=12, fontweight="bold")
    total = dep_fatal["burn_deaths"].sum()
    ax.text(0.95, 0.05, f"Total: {int(total)} deaths", transform=ax.transAxes,
            ha="right", fontsize=11, fontweight="bold",
            bbox=dict(fc="white", alpha=0.8, boxstyle="round"))
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_fatal_referral_burden.png", bbox_inches="tight"); plt.close(fig)


# ── TM: YPLL Bar -- years of life lost highlights telemedicine urgency
def fatal_fig4_ypll_ranking(fatal):
    """Top 20 states by Years of Potential Life Lost -- shows the
       premature death burden that telemedicine could partially address."""
    df = fatal.dropna(subset=["burn_ypll"]).nlargest(20, "burn_ypll").sort_values("burn_ypll", ascending=True)
    colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(df)))
    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(df["STATE"], df["burn_ypll"], color=colors, edgecolor="white")
    for b, (_, r) in zip(bars, df.iterrows()):
        ax.text(b.get_width()+30, b.get_y()+b.get_height()/2,
                f"{int(r['burn_ypll']):,}", va="center", fontsize=8)
    ax.set_xlabel("Years of Potential Life Lost (YPLL before age 65)", fontsize=11)
    ax.set_title("CDC WISQARS: Burn-Related YPLL by State (Top 20)\n"
                 "(Premature death burden -- each year represents preventable loss)",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_fatal_ypll_ranking.png", bbox_inches="tight"); plt.close(fig)


# ── Fatality Choropleth Map ──────────────────────────────────────────
def fatal_fig5_map(fatal):
    """US choropleth: burn death rate by state."""
    gdf = _state_gdf()
    if gdf is None:
        return
    m = gdf.merge(fatal[["STATE","burn_death_rate"]], on="STATE", how="left")
    fig, ax = plt.subplots(figsize=(14, 8))
    m.plot(ax=ax, column="burn_death_rate", cmap="YlOrRd", legend=True,
           legend_kwds={"label":"Burn Deaths per 100k (2023)","shrink":0.55},
           edgecolor="white", linewidth=0.3,
           missing_kwds={"color":"lightgray"})
    ax.set_title("CDC WISQARS: Fire/Burn Fatality Rate by State (2023)",
                 fontsize=13, fontweight="bold")
    ax.axis("off")
    fig.tight_layout(); fig.savefig(FIG_DIR / "narr_fatal_us_map.png", bbox_inches="tight"); plt.close(fig)


# ── MAIN ─────────────────────────────────────────────────────────────
def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    df_raw = load_clean_hospital_data()
    access   = pd.read_csv(OUTPUTS / "equitable_access_state_metrics.csv")
    referral = pd.read_csv(OUTPUTS / "referral_network_recommendations.csv")
    tele     = pd.read_csv(OUTPUTS / "telemedicine_priority_state_scores.csv")
    fatal    = _load_fatal_data()

    print("Phase A: NIRD Foundation figures ...")
    ea_fig1_facility_distribution(df_raw)
    ea_fig2_bed_distribution(df_raw)
    ea_fig3_capability_matrix(df_raw)
    ea_fig4_burn_gap(df_raw)
    rn_fig0a_instate_detail(df_raw)
    rn_fig0b_burn_specialisation(df_raw)
    rn_fig0c_largest_burn_facility(df_raw)
    rn_fig1_burn_state_map(df_raw)
    rn_fig2_burn_beds_concentration(df_raw)
    tm_fig1_access_vs_fragility(access)
    tm_fig2_burn_trauma_gap(df_raw)

    print("Phase B: Enriched figures ...")
    ea_fig5_percapita_ranked(access)
    ea_fig6_fragility_scatter(access)
    ea_fig7_population_exposure(access)
    ea_fig8_map(access)
    rn_fig3_referral_urgency(referral, access)
    rn_fig4_referral_map(referral)
    tm_fig3_priority_components(tele)
    tm_fig4_priority_ranking(tele)
    tm_fig5_tele_map(tele)

    print("Phase C: Cross-challenge figure ...")
    cross_fig_heatmap(access, referral, tele)

    if fatal is not None:
        print("Phase D: Burn fatality demand figures ...")
        fatal_fig1_rate_ranking(fatal)
        fatal_fig2_demand_supply(fatal, access)
        fatal_fig3_referral_burden(fatal, referral)
        fatal_fig4_ypll_ranking(fatal)
        fatal_fig5_map(fatal)
    else:
        print("SKIP Phase D: fatal_report_per_state.csv not found")

    print("\nAll narrative figures written to docs/figures/")


if __name__ == "__main__":
    main()

