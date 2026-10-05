import pytest
from evergreen.config import SAMPLE_DATA_DIR, FLOOR_CHANGE_COST_M
from evergreen.mapping import load_campus_graph, find_route, distance_matrix


@pytest.fixture(scope="module")
def g():
    return load_campus_graph(SAMPLE_DATA_DIR)


def test_same_floor_route(g):
    r = find_route(g, "SMPA 101", "SMPA 102")
    assert r.distance_m == pytest.approx(10 + (15**2 + 10**2) ** 0.5)
    assert r.floors_changed == 0


def test_floor_change_adds_cost(g):
    r = find_route(g, "SMPA 101", "SMPA 201")
    assert r.floors_changed == 1
    assert r.distance_m >= FLOOR_CHANGE_COST_M


def test_between_buildings(g):
    r = find_route(g, "SMPA 101", "SMPB 1140")
    assert r.buildings == ["SMPA", "SMPB"]


def test_unknown_node(g):
    with pytest.raises(KeyError):
        find_route(g, "NOPE", "SMPA 101")


def test_distance_matrix_symmetric(g):
    m = distance_matrix(g, ["SMPA 101", "SMPB 1140", "SMPC 105"])
    assert m.loc["SMPA 101", "SMPB 1140"] == pytest.approx(m.loc["SMPB 1140", "SMPA 101"])
    assert m.loc["SMPA 101", "SMPA 101"] == 0
