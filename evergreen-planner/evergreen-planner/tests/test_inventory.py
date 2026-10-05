import pytest
from evergreen.config import SAMPLE_DATA_DIR
from evergreen.inventory import (load_inventory, load_building_counts, group_by_model,
                                 group_by_category, counts_by_building)


def test_load_and_group():
    inv = load_inventory(SAMPLE_DATA_DIR / "inventory.csv")
    assert len(inv) == 12
    assert group_by_model(inv)["count"].sum() == 12
    assert set(group_by_category(inv)["category"]) == {"3", "4", "5"}


def test_counts_total():
    counts = load_building_counts(SAMPLE_DATA_DIR / "building_counts.csv")
    assert counts_by_building(counts)["count"].sum() == counts["count"].sum()


def test_missing_columns(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("asset_id,building\n1,A\n")
    with pytest.raises(ValueError):
        load_inventory(p)
