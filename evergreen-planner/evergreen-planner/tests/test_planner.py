from evergreen.config import SAMPLE_DATA_DIR
from evergreen.inventory import load_inventory
from evergreen.mapping import load_campus_graph
from evergreen.planning import suggest_targets, plan_consolidation


def test_suggest_targets_picks_largest_holder():
    inv = load_inventory(SAMPLE_DATA_DIR / "inventory.csv")
    assert suggest_targets(inv, "category")["5"] == "SMPA"


def test_plan_moves_only_outside_target_and_has_distance():
    inv = load_inventory(SAMPLE_DATA_DIR / "inventory.csv")
    g = load_campus_graph(SAMPLE_DATA_DIR)
    moves = plan_consolidation(inv, {"5": "SMPA"}, "category", g)
    assert len(moves) == 2  # category-5 units in SMPB and SMPC
    assert (moves["to_building"] == "SMPA").all()
    assert moves["distance_m"].notna().all()
