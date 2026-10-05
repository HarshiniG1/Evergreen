"""Load map CSVs. Lines starting with '#' are comments."""
from __future__ import annotations

from pathlib import Path

import networkx as nx
import pandas as pd

from .graph import build_campus_graph


def load_locations(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, comment="#", dtype={"node_id": str})


def load_edges(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, comment="#", dtype={"source": str, "target": str})


def load_campus_graph(data_dir: Path) -> nx.Graph:
    data_dir = Path(data_dir)
    return build_campus_graph(load_locations(data_dir / "locations.csv"),
                              load_edges(data_dir / "edges.csv"))
