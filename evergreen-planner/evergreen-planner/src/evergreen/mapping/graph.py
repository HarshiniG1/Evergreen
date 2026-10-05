"""Build the campus graph (NetworkX).

Nodes : rooms, corridor points, stairs, elevators, entrances (one per floor).
Edges : walkable connections. Weight = horizontal distance + floor-change cost.
"""
from __future__ import annotations

import math

import networkx as nx
import pandas as pd

from evergreen.config import FLOOR_CHANGE_COST_M

NODE_COLUMNS = {"node_id", "building", "floor", "kind", "x_m", "y_m"}
EDGE_COLUMNS = {"source", "target", "kind", "distance_m"}


def build_campus_graph(locations: pd.DataFrame, edges: pd.DataFrame,
                       floor_cost_m: float = FLOOR_CHANGE_COST_M) -> nx.Graph:
    missing = NODE_COLUMNS - set(locations.columns)
    if missing:
        raise ValueError(f"locations missing columns: {sorted(missing)}")
    missing = EDGE_COLUMNS - set(edges.columns)
    if missing:
        raise ValueError(f"edges missing columns: {sorted(missing)}")

    g = nx.Graph()
    for row in locations.itertuples(index=False):
        g.add_node(str(row.node_id), building=str(row.building), floor=int(row.floor),
                   kind=str(row.kind), x=float(row.x_m), y=float(row.y_m))

    for row in edges.itertuples(index=False):
        a, b = str(row.source), str(row.target)
        for n in (a, b):
            if n not in g:
                raise ValueError(f"Edge references unknown node: {n!r}")
        na, nb = g.nodes[a], g.nodes[b]
        if pd.isna(row.distance_m):
            horizontal = math.hypot(na["x"] - nb["x"], na["y"] - nb["y"])
        else:
            horizontal = float(row.distance_m)
        vertical = abs(na["floor"] - nb["floor"]) * floor_cost_m
        g.add_edge(a, b, kind=str(row.kind), horizontal_m=horizontal,
                   vertical_cost=vertical, weight=horizontal + vertical)
    return g


def building_hub(g: nx.Graph, building: str) -> str:
    """Drop-off node of a building: its first 'entrance' node (assumption)."""
    for n, d in g.nodes(data=True):
        if d["building"] == building and d["kind"] == "entrance":
            return n
    raise KeyError(f"No entrance node for building {building!r}")
