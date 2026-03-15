from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
MAIN_CSV = DATA_DIR / "NIRD 20230130 Database_Hackathon.csv"


def load_raw_hospital_data(csv_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load the raw hospital trauma/burn dataset from CSV.

    Parameters
    ----------
    csv_path:
        Optional override path. Defaults to the main CSV in the data directory.

    Returns
    -------
    pd.DataFrame
        Raw DataFrame as read from CSV (minimal type inference).
    """
    path = csv_path or MAIN_CSV
    if not path.exists():
        raise FileNotFoundError(f"Hospital dataset not found at {path}")

    df = pd.read_csv(path)
    return df


def clean_hospital_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply basic cleaning and type normalization to the hospital dataset.

    This focuses on:
    - Stripping whitespace from string columns.
    - Normalizing Yes/No style flag columns into booleans.
    - Ensuring numeric columns such as bed counts are numeric.
    """
    df = df.copy()

    # Strip whitespace from all object columns
    obj_cols = df.select_dtypes(include=["object"]).columns
    for col in obj_cols:
        df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)

    # Normalize flag columns that are expected to behave like Yes/No
    yes_no_like_cols = [
        "TRAUMA_ADULT",
        "TRAUMA_PEDS",
        "BURN_ADULT",
        "BURN_PEDS",
        "ACS_VERIFIED",
        "ABA_VERIFIED",
        "ADULT_TRAUMA_L1",
        "ADULT_TRAUMA_L2",
        "PEDS_TRAUMA_L1",
        "PEDS_TRAUMA_L2",
        "TC_STATE_DESIGNATED",
        "BC_STATE_DESIGNATED",
    ]

    def _to_bool(value: object) -> Optional[bool]:
        if pd.isna(value):
            return None
        if isinstance(value, (int, float)):
            if value == 1:
                return True
            if value == 0:
                return False
        v = str(value).strip().lower()
        if v in {"yes", "y", "true", "1"}:
            return True
        if v in {"no", "n", "false", "0"}:
            return False
        return None

    for col in yes_no_like_cols:
        if col in df.columns:
            df[col] = df[col].map(_to_bool)

    # Ensure numeric bed count columns are numeric
    for col in ["TOTAL_BEDS", "BURN_BEDS"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def load_clean_hospital_data(csv_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Convenience wrapper: load the main CSV and apply basic cleaning.
    """
    raw = load_raw_hospital_data(csv_path=csv_path)
    return clean_hospital_data(raw)


__all__ = [
    "DATA_DIR",
    "MAIN_CSV",
    "load_raw_hospital_data",
    "clean_hospital_data",
    "load_clean_hospital_data",
]
