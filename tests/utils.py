from typing import (Hashable,
                    Iterable,
                    Sequence)

from hypothesis.searchstrategy import SearchStrategy
from lz.hints import (Domain,
                      Map)

from gon.angular import Orientation
from gon.base import Point
from gon.shaped.utils import to_angles

Strategy = SearchStrategy


def equivalence(left_statement: bool, right_statement: bool) -> bool:
    return left_statement is right_statement


def implication(antecedent: bool, consequent: bool) -> bool:
    return not antecedent or consequent


def unique_everseen(iterable: Iterable[Domain],
                    *,
                    key: Map[Domain, Hashable] = None) -> Iterable[Domain]:
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in iterable:
            if element not in seen:
                seen_add(element)
                yield element
    else:
        for element in iterable:
            value = key(element)
            if value not in seen:
                seen_add(value)
                yield element


def points_do_not_lie_on_the_same_line(points: Sequence[Point]) -> bool:
    return any(angle.orientation is not Orientation.COLLINEAR
               for angle in to_angles(points))
