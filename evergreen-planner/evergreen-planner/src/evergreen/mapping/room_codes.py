"""Parse room codes such as 'AGN 302' into building + floor.

ASSUMPTION (to verify with real uOttawa data): the floor is the FIRST digit of the
room number ('302' -> floor 3, '1140' -> floor 1). Some buildings may differ, so
per-building override rules can be passed in `floor_rules`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Mapping, Optional

_ROOM_RE = re.compile(r"^\s*([A-Za-z]{2,6})\s*[-_ ]?\s*(\d{3,4}[A-Za-z]?)\s*$")

FloorRule = Callable[[str], int]  # receives the digits string, returns the floor


@dataclass(frozen=True)
class RoomCode:
    building: str
    number: str
    floor: int

    @property
    def normalized(self) -> str:
        return f"{self.building} {self.number}"


def floor_from_number(number: str, building: str = "",
                      floor_rules: Optional[Mapping[str, FloorRule]] = None) -> int:
    digits = re.match(r"\d+", number).group(0)
    if floor_rules and building.upper() in floor_rules:
        return floor_rules[building.upper()](digits)
    return int(digits[0])  # default rule


def parse_room_code(code: str,
                    floor_rules: Optional[Mapping[str, FloorRule]] = None) -> RoomCode:
    m = _ROOM_RE.match(code)
    if not m:
        raise ValueError(f"Unrecognised room code: {code!r}")
    building, number = m.group(1).upper(), m.group(2).upper()
    return RoomCode(building, number, floor_from_number(number, building, floor_rules))
