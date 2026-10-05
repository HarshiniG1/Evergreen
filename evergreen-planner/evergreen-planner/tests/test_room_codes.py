import pytest
from evergreen.mapping import parse_room_code


def test_three_digit_room():
    r = parse_room_code("AGN 302")
    assert (r.building, r.number, r.floor) == ("AGN", "302", 3)


def test_four_digit_room_first_floor():
    assert parse_room_code("abc1140").floor == 1


def test_override_rule():
    rules = {"XYZ": lambda digits: int(digits[:2])}
    assert parse_room_code("XYZ 1140", rules).floor == 11


def test_invalid():
    with pytest.raises(ValueError):
        parse_room_code("not a room")
