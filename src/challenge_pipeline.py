from __future__ import annotations

from pathlib import Path
import sys

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_loading import load_clean_hospital_data
from src.features import add_basic_capacity_features


DATA_EXTERNAL = ROOT / "data" / "external"
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "docs" / "figures"


def _safe_minmax(series: pd.Series) -> pd.Series:
    min_v = series.min()
    max_v = series.max()
    if pd.isna(min_v) or pd.isna(max_v) or min_v == max_v:
        return pd.Series(0.0, index=series.index)
    return (series - min_v) / (max_v - min_v)


def build_state_base_metrics() -> pd.DataFrame:
    df = load_clean_hospital_data()

    by_state = (
        df.groupby("STATE")
        .agg(
            facilities=("STATE", "size"),
            total_beds=("TOTAL_BEDS", "sum"),
            burn_beds=("BURN_BEDS", "sum"),
            adult_trauma_centers=("TRAUMA_ADULT", lambda s: (s == True).sum()),
            peds_trauma_centers=("TRAUMA_PEDS", lambda s: (s == True).sum()),
            adult_burn_centers=("BURN_ADULT", lambda s: (s == True).sum()),
            peds_burn_centers=("BURN_PEDS", lambda s: (s == True).sum()),
        )
        .reset_index()
    )

    pop = pd.read_csv(DATA_EXTERNAL / "state_population_2012.csv")
    base = by_state.merge(pop, on="STATE", how="left")
    base = add_basic_capacity_features(base, population_col="population")

    # Resilience proxy: loss if largest facility in the state is unavailable.
    top_facility = (
        df[["STATE", "TOTAL_BEDS"]]
        .dropna(subset=["TOTAL_BEDS"])
        .groupby("STATE")["TOTAL_BEDS"]
        .max()
        .rename("largest_single_facility_beds")
    )
    base = base.set_index("STATE").join(top_facility, how="left").reset_index()
    base["capacity_loss_pct"] = (
        base["largest_single_facility_beds"] / base["total_beds"] * 100
    )
    return base


def build_rurality_by_state() -> pd.DataFrame:
    rucc = pd.read_csv(DATA_EXTERNAL / "rucc_2023_county.csv", encoding="latin1")
    rucc_code = rucc[rucc["Attribute"] == "RUCC_2023"].copy()
    rucc_code["rucc_code"] = pd.to_numeric(rucc_code["Value"], errors="coerce")
    rucc_code["is_rural"] = rucc_code["rucc_code"] >= 4

    rural = (
        rucc_code.groupby("State")
        .agg(
            counties=("FIPS", "nunique"),
            rural_counties=("is_rural", "sum"),
        )
        .reset_index()
        .rename(columns={"State": "STATE"})
    )
    rural["rural_county_share"] = rural["rural_counties"] / rural["counties"] * 100
    return rural


def build_svi_by_state() -> pd.DataFrame:
    svi = pd.read_csv(DATA_EXTERNAL / "SVI_2022_US_county.csv")
    svi = svi.copy()
    svi["E_TOTPOP"] = pd.to_numeric(svi["E_TOTPOP"], errors="coerce")
    svi["RPL_THEMES"] = pd.to_numeric(svi["RPL_THEMES"], errors="coerce")
    svi = svi.dropna(subset=["ST_ABBR", "E_TOTPOP", "RPL_THEMES"])
    svi = svi[svi["E_TOTPOP"] > 0]

    # Population-weighted state social vulnerability percentile.
    grp = svi.groupby("ST_ABBR")
    weighted = grp.apply(
        lambda x: np.average(x["RPL_THEMES"], weights=x["E_TOTPOP"]),
        include_groups=False,
    )
    out = weighted.rename("svi_weighted").reset_index().rename(columns={"ST_ABBR": "STATE"})
    return out


def build_mobile_broadband_by_state() -> pd.DataFrame:
    bdc_path = (
        DATA_EXTERNAL
        / "bdc_us_mobile_broadband_summary_by_geography_J25_03mar2026"
        / "bdc_us_mobile_broadband_summary_by_geography_J25_03mar2026.csv"
    )
    if not bdc_path.exists():
        return pd.DataFrame(columns=["STATE", "digital_coverage_pct"])

    bdc = pd.read_csv(bdc_path, low_memory=False)
    bdc = bdc[
        (bdc["area_data_type"] == "Total") & (bdc["geography_type"] == "State")
    ].copy()

    bdc["digital_coverage_pct"] = (
        pd.to_numeric(bdc["mobilebb_5g_spd2_area_st_pct"], errors="coerce") * 100.0
    )

    # Build state abbreviation mapping from state names.
    ab = pd.read_csv(DATA_EXTERNAL / "state_abbrevs.csv")
    out = bdc.merge(
        ab[["state", "abbreviation"]],
        left_on="geography_desc",
        right_on="state",
        how="left",
    )
    out = out.rename(columns={"abbreviation": "STATE"})
    out = out[["STATE", "digital_coverage_pct"]].dropna(subset=["STATE"])
    return out


def build_ahrf_provider_by_state() -> pd.DataFrame:
    base_dir = DATA_EXTERNAL / "AHRF_2024-2025_CSV" / "NCHWA-2024-2025+AHRF+COUNTY+CSV"
    hp_path = base_dir / "AHRF2025hp.csv"
    pop_path = base_dir / "AHRF2025pop.csv"
    if not hp_path.exists() or not pop_path.exists():
        return pd.DataFrame(columns=["STATE", "provider_density_score"])

    hp = pd.read_csv(
        hp_path,
        usecols=["fips_st_cnty", "cnty_name_st_abbrev", "phys_nf_prim_care_pc_exc_rsdt_23"],
        low_memory=False,
    )
    pop = pd.read_csv(
        pop_path,
        usecols=["fips_st_cnty", "popn_est_23"],
        low_memory=False,
    )

    hp["provider_density_score"] = pd.to_numeric(
        hp["phys_nf_prim_care_pc_exc_rsdt_23"], errors="coerce"
    )
    pop["popn_est_23"] = pd.to_numeric(pop["popn_est_23"], errors="coerce")
    hp = hp.merge(pop, on="fips_st_cnty", how="left")
    hp = hp.dropna(subset=["provider_density_score", "popn_est_23"])
    hp = hp[hp["popn_est_23"] > 0]
    hp["STATE"] = hp["cnty_name_st_abbrev"].astype(str).str[-2:]

    state_provider = (
        hp.groupby("STATE")
        .apply(
            lambda x: np.average(
                x["provider_density_score"], weights=x["popn_est_23"]
            ),
            include_groups=False,
        )
        .rename("provider_density_score")
        .reset_index()
    )
    return state_provider


def build_referral_network_recommendations(base: pd.DataFrame) -> pd.DataFrame:
    zip_path = DATA_EXTERNAL / "cb_2023_us_state_20m.zip"
    shp_path = DATA_EXTERNAL / "cb_2023_us_state_20m" / "cb_2023_us_state_20m.shp"

    if zip_path.exists():
        gdf = gpd.read_file(f"zip://{zip_path}")
    elif shp_path.exists():
        gdf = gpd.read_file(shp_path)
    else:
        # Fallback to previously generated file when geometry files are missing.
        fallback = OUTPUTS / "referral_network_recommendations.csv"
        if fallback.exists():
            return pd.read_csv(fallback)
        return pd.DataFrame(
            columns=[
                "origin_state",
                "recommended_hub_state",
                "estimated_distance_km",
                "referral_type",
            ]
        )

    gdf = gdf[["STUSPS", "NAME", "geometry"]].rename(columns={"STUSPS": "STATE"})
    gdf = gdf[gdf["STATE"].isin(base["STATE"])].copy()
    gdf = gdf.to_crs(2163)  # meters-based projection for distance.
    gdf["centroid"] = gdf.geometry.centroid

    geom_map = gdf.set_index("STATE")["centroid"].to_dict()
    burn_map = base.set_index("STATE")["adult_burn_centers"].to_dict()

    # States with no adult burn center are likely to require out-of-state referral.
    underserved = [s for s, v in burn_map.items() if pd.notna(v) and v == 0]
    hubs = [s for s, v in burn_map.items() if pd.notna(v) and v > 0]

    rows = []
    for state in underserved:
        if state not in geom_map:
            continue
        origin = geom_map[state]

        best_hub = None
        best_dist_km = None
        for hub in hubs:
            if hub not in geom_map:
                continue
            dist_km = origin.distance(geom_map[hub]) / 1000.0
            if best_dist_km is None or dist_km < best_dist_km:
                best_dist_km = dist_km
                best_hub = hub

        rows.append(
            {
                "origin_state": state,
                "recommended_hub_state": best_hub,
                "estimated_distance_km": round(best_dist_km, 1)
                if best_dist_km is not None
                else np.nan,
                "referral_type": "adult_burn",
            }
        )
    if not rows:
        return pd.DataFrame(
            columns=[
                "origin_state",
                "recommended_hub_state",
                "estimated_distance_km",
                "referral_type",
            ]
        )
    out = pd.DataFrame(rows).sort_values("estimated_distance_km", ascending=False)
    return out


def build_telemedicine_priority(base: pd.DataFrame) -> pd.DataFrame:
    broadband = pd.read_csv(DATA_EXTERNAL / "state_broadband_acs2022.csv")
    bdc_mobile = build_mobile_broadband_by_state()
    providers = build_ahrf_provider_by_state()
    rurality = build_rurality_by_state()
    svi = build_svi_by_state()

    tele = (
        base.merge(
            broadband[["STATE", "broadband_pct"]],
            on="STATE",
            how="left",
        )
        .merge(
            bdc_mobile[["STATE", "digital_coverage_pct"]],
            on="STATE",
            how="left",
        )
        .merge(
            rurality[["STATE", "rural_county_share"]],
            on="STATE",
            how="left",
        )
        .merge(
            providers[["STATE", "provider_density_score"]],
            on="STATE",
            how="left",
        )
        .merge(
            svi[["STATE", "svi_weighted"]],
            on="STATE",
            how="left",
        )
        .copy()
    )

    # Build interpretable priority components.
    tele["access_gap_component"] = _safe_minmax(
        1 / tele["total_beds_per_100k"].replace(0, np.nan)
    )
    tele["fragility_component"] = _safe_minmax(tele["capacity_loss_pct"])
    tele["rurality_component"] = _safe_minmax(tele["rural_county_share"])
    digital_source = tele["digital_coverage_pct"].fillna(tele["broadband_pct"])
    tele["digital_gap_component"] = _safe_minmax(100 - digital_source)
    tele["provider_shortage_component"] = _safe_minmax(
        1 / tele["provider_density_score"].replace(0, np.nan)
    )
    tele["vulnerability_component"] = _safe_minmax(tele["svi_weighted"])

    tele["telemedicine_priority_score"] = (
        0.25 * tele["access_gap_component"]
        + 0.15 * tele["fragility_component"]
        + 0.15 * tele["rurality_component"]
        + 0.15 * tele["digital_gap_component"]
        + 0.15 * tele["provider_shortage_component"]
        + 0.15 * tele["vulnerability_component"]
    ) * 100

    return tele.sort_values("telemedicine_priority_score", ascending=False)


def save_visuals(
    base: pd.DataFrame, referral: pd.DataFrame, telemedicine: pd.DataFrame
) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)

    # Equitable access: top and bottom per-capita access.
    top = base.sort_values("total_beds_per_100k", ascending=False).head(10)
    low = base.sort_values("total_beds_per_100k", ascending=True).head(10)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].bar(top["STATE"], top["total_beds_per_100k"])
    axes[0].set_title("Top 10 States: Total Beds per 100k")
    axes[0].set_ylabel("Beds per 100k")
    axes[1].bar(low["STATE"], low["total_beds_per_100k"], color="tomato")
    axes[1].set_title("Bottom 10 States: Total Beds per 100k")
    fig.tight_layout()
    fig.savefig(FIGURES / "equitable_access_top_bottom_beds_per_100k.png", dpi=150)
    plt.close(fig)

    # Referral: underserved states and estimated referral distance to nearest hub.
    if not referral.empty:
        view = referral.head(12).sort_values("estimated_distance_km", ascending=True)
        plt.figure(figsize=(10, 5))
        plt.barh(view["origin_state"], view["estimated_distance_km"], color="#5271ff")
        plt.xlabel("Estimated distance to nearest adult burn hub (km)")
        plt.ylabel("Origin state")
        plt.title("Referral Burden for States Without Adult Burn Centers")
        plt.tight_layout()
        plt.savefig(FIGURES / "referral_network_distance_burden.png", dpi=150)
        plt.close()

    # Telemedicine: highest priority states.
    top_tele = telemedicine.head(12).sort_values(
        "telemedicine_priority_score", ascending=True
    )
    plt.figure(figsize=(10, 5))
    plt.barh(top_tele["STATE"], top_tele["telemedicine_priority_score"], color="#00a676")
    plt.xlabel("Telemedicine priority score (0-100)")
    plt.ylabel("State")
    plt.title("Top Telemedicine Priority States")
    plt.tight_layout()
    plt.savefig(FIGURES / "telemedicine_priority_top_states.png", dpi=150)
    plt.close()


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    base = build_state_base_metrics()
    referral = build_referral_network_recommendations(base)
    telemedicine = build_telemedicine_priority(base)

    base.to_csv(OUTPUTS / "equitable_access_state_metrics.csv", index=False)
    referral.to_csv(OUTPUTS / "referral_network_recommendations.csv", index=False)
    telemedicine.to_csv(OUTPUTS / "telemedicine_priority_state_scores.csv", index=False)

    save_visuals(base, referral, telemedicine)

    print("Generated outputs:")
    print("- outputs/equitable_access_state_metrics.csv")
    print("- outputs/referral_network_recommendations.csv")
    print("- outputs/telemedicine_priority_state_scores.csv")
    print("Generated figures under docs/figures/")


if __name__ == "__main__":
    main()
