# Evergreen Planner

Planning tool for the summer **Evergreen** computer replacement at uOttawa.

**Goal:** group computers of the same model/category in the same building (e.g. all
category-5 machines in one building), so during the replacement the technician only swaps
old for new inside a single building. To do that we need (1) a map of the campus to know
the distance between rooms (including floors), (2) the computer inventory, and
(3) a planner that decides which computers move where, with the cheapest movements.

> ⚠️ **All data in `data/sample/` is FAKE** (buildings `SMPA/SMPB/SMPC`, invented x/y in
> metres, `SAMPLE-` asset IDs). No real uOttawa coordinates or inventory are included.

## Architecture

```
src/evergreen/
  config.py        settings (paths, floor-change cost)
  mapping/         MAP SYSTEM  (no dependency on inventory)
    room_codes.py  "AGN 302" -> building AGN, floor 3 (configurable per building)
    graph.py       NetworkX graph builder (nodes = rooms/corridors/stairs/entrances)
    routing.py     shortest route + distance matrix
    loader.py      CSV -> graph
  inventory/       INVENTORY SYSTEM  (no dependency on mapping)
    loader.py      item-level inventory + aggregate per-building counts (pandas)
    grouping.py    group by model / category / building
  planning/        uses BOTH (only place where they meet)
    planner.py     baseline consolidation planner (greedy) - optimiser comes later
app/streamlit_app.py   first interface (Route / Inventory / Consolidation plan)
data/sample/           FAKE sample CSVs
tests/                 pytest
```

**The only link between the two systems** is the room code: `inventory.room` must equal a
room `node_id` in `locations.csv` (e.g. `"SMPA 101"`), and `inventory.building` must equal
the node's `building`.

### Data formats
- `locations.csv`: `node_id, building, floor, kind, x_m, y_m`
  (`kind` = room / corridor / stairs / elevator / entrance). Rooms use their room code as `node_id`.
- `edges.csv`: `source, target, kind, distance_m` (leave `distance_m` blank to compute it from x/y).
  Edge weight = horizontal distance + `FLOOR_CHANGE_COST_M` × floors changed.
- `inventory.csv`: `asset_id, building, room, model, category, status`
- `building_counts.csv`: `building, model, category, count` (for the aggregate lists of
  ~4000–5000 computers we will receive per building)
- Lines starting with `#` in the CSVs are comments.

## Install

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pip install -e .
```

In **GitHub Codespaces** this is done automatically (`.devcontainer/`).

## Run

```bash
streamlit run app/streamlit_app.py
```
(In Codespaces, open the forwarded port 8501.)

## Test

```bash
pytest
```

## Using real data later
Put real files in `data/real/` (git-ignored, never commit them) with the same column
formats, and point the loaders to that folder (`REAL_DATA_DIR` in `config.py`).

## Open questions / assumptions
- Floor rule: first digit of the room number (`302` → 3, `1140` → 1). Buildings that differ
  (e.g. rooms like `11-40`) need a rule in `floor_rules` (see `room_codes.py`).
- Floor-change cost (15 m per floor) is a placeholder.
- Building drop-off point = the building's first `entrance` node.
- Planner is a greedy baseline: it ignores building capacity and truck/trip logistics.
  Lat/lon/altitude can be added as extra columns when the real maps arrive.

## Roadmap
1. Map: model real buildings/floors/corridors → real routes (Habib)
2. Inventory: ingest the real lists, clean models/categories (Harshini)
3. Planner: capacity-aware targets, then trip/route optimisation (both)
4. UI: map visualisation, export of move lists to CSV/Excel
