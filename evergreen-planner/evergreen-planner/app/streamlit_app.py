"""Initial Streamlit interface. Run: streamlit run app/streamlit_app.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import streamlit as st

from evergreen.config import SAMPLE_DATA_DIR
from evergreen.inventory import (load_inventory, load_building_counts, group_by_model,
                                 group_by_category, summarize_by_building, counts_by_building)
from evergreen.mapping import load_campus_graph, find_route
from evergreen.planning import suggest_targets, plan_consolidation

st.set_page_config(page_title="Evergreen Planner", layout="wide")
st.title("Evergreen Planner")
st.warning("Showing SAMPLE data (fake buildings, rooms and computers). "
           "Not real uOttawa data.")


@st.cache_data
def _load():
    return (load_campus_graph(SAMPLE_DATA_DIR),
            load_inventory(SAMPLE_DATA_DIR / "inventory.csv"),
            load_building_counts(SAMPLE_DATA_DIR / "building_counts.csv"))


graph, inv, counts = _load()
tab_route, tab_inv, tab_plan = st.tabs(["Route", "Inventory", "Consolidation plan"])

with tab_route:
    rooms = sorted(n for n, d in graph.nodes(data=True) if d["kind"] == "room")
    c1, c2 = st.columns(2)
    src = c1.selectbox("From room", rooms, index=0)
    dst = c2.selectbox("To room", rooms, index=len(rooms) - 1)
    if st.button("Compute route"):
        r = find_route(graph, src, dst)
        st.metric("Distance (m, incl. floor cost)", f"{r.distance_m:.1f}")
        st.write(f"Floors changed: {r.floors_changed} | Buildings: {' -> '.join(r.buildings)}")
        st.write(" -> ".join(r.nodes))

with tab_inv:
    a, b = st.columns(2)
    a.subheader("By model"); a.dataframe(group_by_model(inv), hide_index=True)
    b.subheader("By category"); b.dataframe(group_by_category(inv), hide_index=True)
    st.subheader("By building / model"); st.dataframe(summarize_by_building(inv), hide_index=True)
    st.subheader("Aggregate counts per building (sample lists)")
    st.dataframe(counts_by_building(counts), hide_index=True)

with tab_plan:
    key = st.radio("Group by", ["category", "model"], horizontal=True)
    targets = suggest_targets(inv, key)
    st.write("Suggested target building per group (greedy baseline):", targets)
    moves = plan_consolidation(inv, targets, key, graph)
    st.write(f"{len(moves)} computers to move")
    st.dataframe(moves, hide_index=True)
