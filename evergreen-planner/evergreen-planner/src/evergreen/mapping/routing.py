"""Shortest-path routing between rooms/nodes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import networkx as nx
import pandas as pd


@dataclass(frozen=True)
class Route:
    nodes: list[str]
    distance_m: float
    floors_changed: int
    buildings: list[str]  # buildings visited, in order, without repeats


def find_route(g: nx.Graph, source: str, target: str) -> Route:
    for n in (source, target):
        if n not in g:
            raise KeyError(f"Unknown node: {n!r}")
    try:
        path = nx.dijkstra_path(g, source, target, weight="weight")
    except nx.NetworkXNoPath as exc:
        raise ValueError(f"No route between {source!r} and {target!r}") from exc

    dist, floors = 0.0, 0
    for a, b in zip(path, path[1:]):
        e = g.edges[a, b]
        dist += e["weight"]
        floors += abs(g.nodes[a]["floor"] - g.nodes[b]["floor"])
    buildings: list[str] = []
    for n in path:
        b = g.nodes[n]["building"]
        if not buildings or buildings[-1] != b:
            buildings.append(b)
    return Route(path, dist, floors, buildings)


def distance_matrix(g: nx.Graph, nodes: Iterable[str]) -> pd.DataFrame:
    """All-pairs distances between `nodes` (building block for later optimisation)."""
    nodes = list(nodes)
    rows = {}
    for s in nodes:
        lengths = nx.single_source_dijkstra_path_length(g, s, weight="weight")
        rows[s] = [lengths.get(t, float("inf")) for t in nodes]
    return pd.DataFrame(rows, index=nodes).T
