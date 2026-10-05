"""Baseline consolidation planner (NOT optimal - a starting point).

Goal: every building ends up holding one group (e.g. category 5), so during the
summer replacement the technician only swaps old for new inside one building.
"""
from __future__ import annotations

from typing import Mapping, Optional

import networkx as nx
import pandas as pd

from evergreen.mapping.graph import building_hub
from evergreen.mapping.routing import find_route


def suggest_targets(inv: pd.DataFrame, key: str = "category") -> dict[str, str]:
    """Greedy baseline: send each group to the building that already holds most of it.

    Note: two groups may pick the same building. A later optimiser should also
    balance building capacity.
    """
    counts = inv.groupby([key, "building"]).size().reset_index(name="n")
    counts = counts.sort_values([key, "n", "building"], ascending=[True, False, True])
    return counts.drop_duplicates(key).set_index(key)["building"].to_dict()


def plan_consolidation(inv: pd.DataFrame, targets: Mapping[str, str], key: str = "category",
                       graph: Optional[nx.Graph] = None) -> pd.DataFrame:
    """List the moves needed. If `graph` is given, add an estimated walking distance
    from the computer's room to the target building's entrance."""
    rows = []
    for r in inv.itertuples(index=False):
        group = getattr(r, key)
        target = targets.get(group)
        if target is None or target == r.building:
            continue
        dist = float("nan")
        if graph is not None and r.room in graph:
            try:
                dist = find_route(graph, r.room, building_hub(graph, target)).distance_m
            except (ValueError, KeyError):
                pass
        rows.append({"asset_id": r.asset_id, "model": r.model, "category": r.category,
                     "from_building": r.building, "from_room": r.room,
                     "to_building": target, "distance_m": dist})
    cols = ["asset_id", "model", "category", "from_building", "from_room",
            "to_building", "distance_m"]
    return pd.DataFrame(rows, columns=cols)
