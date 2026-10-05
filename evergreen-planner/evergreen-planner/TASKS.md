# Team brief: Habib & Harshini

Two independent workstreams that meet only through the **room code** (see README).
Roles can be swapped; what matters is that each person owns one package.

## Habib – Map & Routing (`src/evergreen/mapping/`, `data/.../locations.csv, edges.csv`)
1. Collect the building maps (floor plans, campus map) and decide the data model per building.
2. Fill `locations.csv` / `edges.csv` for real buildings: rooms, corridors, stairs,
   elevators, entrances, tunnels, outdoor links between buildings.
3. Verify the room-number → floor rules per building (`room_codes.py`), e.g. `AGN 302` vs four-digit rooms.
4. Improve routing: elevator vs stairs cost, accessibility, outdoor vs indoor cost.
5. Tests for every new rule; later, a map visualisation (floor view, route drawn on map).
**Deliverable:** `find_route("ROOM A", "ROOM B")` gives correct distances on real data.

## Harshini – Inventory & Grouping (`src/evergreen/inventory/`, `data/.../inventory.csv, building_counts.csv`)
1. Define the real column format with the people who send the lists (4000–5000 computers per building).
2. Write loaders/cleaners for the real files (Excel/CSV): normalise building codes, room codes, model names, categories.
3. Validation: duplicates, missing rooms, unknown models, rooms not found in the map.
4. Reports: units per model / category / building, which building holds most of each group.
5. Tests for loaders and grouping.
**Deliverable:** one clean inventory DataFrame + summary tables from the real lists.

## Shared (`planning/`, `app/`, README)
- Agree on the target-building rules (which category goes to which building, capacity).
- Evolve `planner.py` from the greedy baseline to an optimiser (minimise total distance / trips).
- Build the Streamlit tabs together; keep README and tests up to date.
- Git workflow: one branch per person (`habib/mapping`, `harshini/inventory`), small pull
  requests, review each other's PRs, `pytest` must pass before merging.

## Milestones
| Step | Habib | Harshini |
|------|-------|----------|
| 1 | Map data model + first real building | Real file format + loader |
| 2 | 3–5 real buildings routable | Clean inventory + summary reports |
| 3 | Cross-building routes | Room codes validated against the map |
| 4 | Together: capacity-aware planner, UI, export of move lists |
