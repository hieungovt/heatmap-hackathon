from __future__ import annotations

from typing import Optional

import pandas as pd


def add_basic_capacity_features(
    df: pd.DataFrame, population_col: Optional[str] = None
) -> pd.DataFrame:
    """
    Add simple capacity-related features to the hospital dataset.

    If a population column is provided (e.g., joined from external census data),
    derive per-capita bed metrics.
    """
    df = df.copy()

    if population_col and population_col in df.columns:
        pop = df[population_col].replace({0: pd.NA})
        total_beds_col = "TOTAL_BEDS" if "TOTAL_BEDS" in df.columns else "total_beds"
        burn_beds_col = "BURN_BEDS" if "BURN_BEDS" in df.columns else "burn_beds"

        if total_beds_col in df.columns:
            df["total_beds_per_100k"] = (df[total_beds_col] / pop) * 100_000
        if burn_beds_col in df.columns:
            df["burn_beds_per_100k"] = (df[burn_beds_col] / pop) * 100_000

    return df


__all__ = [
    "add_basic_capacity_features",
]
