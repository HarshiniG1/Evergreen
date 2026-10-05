"""Load and validate inventory data (pandas)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

INVENTORY_COLUMNS = ["asset_id", "building", "room", "model", "category", "status"]
COUNT_COLUMNS = ["building", "model", "category", "count"]


def _check(df: pd.DataFrame, required: list[str], name: str) -> pd.DataFrame:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{name} missing columns: {missing}")
    return df


def load_inventory(path: Path) -> pd.DataFrame:
    """One row per computer."""
    df = pd.read_csv(path, comment="#", dtype={"category": str, "asset_id": str})
    _check(df, INVENTORY_COLUMNS, "inventory")
    if df["asset_id"].duplicated().any():
        raise ValueError("inventory contains duplicate asset_id values")
    return df


def load_building_counts(path: Path) -> pd.DataFrame:
    """Aggregate lists: how many computers of a model/category in each building."""
    df = pd.read_csv(path, comment="#", dtype={"category": str})
    _check(df, COUNT_COLUMNS, "building counts")
    return df
