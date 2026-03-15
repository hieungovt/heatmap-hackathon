from __future__ import annotations

from typing import Iterable, Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_beds_distribution(
    df: pd.DataFrame,
    columns: Iterable[str] = ("TOTAL_BEDS", "BURN_BEDS"),
    log_scale: bool = True,
) -> plt.Figure:
    """
    Plot simple distributions of bed-related columns.
    """
    cols = [c for c in columns if c in df.columns]
    n = len(cols)
    if n == 0:
        raise ValueError("No valid bed columns to plot.")

    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4))
    if n == 1:
        axes = [axes]

    for ax, col in zip(axes, cols):
        sns.histplot(df[col].dropna(), kde=True, ax=ax)
        ax.set_title(f"{col} distribution")
        if log_scale:
            ax.set_xscale("log")
            ax.set_xlabel(f"{col} (log scale)")

    fig.tight_layout()
    return fig


def plot_facilities_by_state(df: pd.DataFrame, state_col: str = "STATE") -> plt.Figure:
    """
    Plot a bar chart of facility counts by state.
    """
    if state_col not in df.columns:
        raise ValueError(f"Column {state_col!r} not found in DataFrame.")

    counts = df[state_col].value_counts().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(12, 4))
    counts.plot(kind="bar", ax=ax)
    ax.set_ylabel("Number of facilities")
    ax.set_title("Facilities by state")
    fig.tight_layout()
    return fig


__all__ = [
    "plot_beds_distribution",
    "plot_facilities_by_state",
]
