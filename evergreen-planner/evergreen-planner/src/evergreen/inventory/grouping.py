"""Group computers by model / category / building."""
from __future__ import annotations

import pandas as pd


def summarize_by_building(inv: pd.DataFrame) -> pd.DataFrame:
    """Units per (building, model, category) from an item-level inventory."""
    return (inv.groupby(["building", "model", "category"]).size()
               .reset_index(name="count"))


def group_by_model(inv: pd.DataFrame) -> pd.DataFrame:
    return inv.groupby("model").size().reset_index(name="count").sort_values(
        "count", ascending=False, ignore_index=True)


def group_by_category(inv: pd.DataFrame) -> pd.DataFrame:
    return inv.groupby("category").size().reset_index(name="count").sort_values(
        "category", ignore_index=True)


def counts_by_building(counts: pd.DataFrame) -> pd.DataFrame:
    """Total units per building from an aggregate counts table."""
    return counts.groupby("building")["count"].sum().reset_index().sort_values(
        "count", ascending=False, ignore_index=True)
