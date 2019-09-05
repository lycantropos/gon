from typing import (Hashable,
                    Iterable,
                    Sequence,
                    Tuple)

from hypothesis.searchstrategy import SearchStrategy
from lz.hints import (Domain,
                      Map)
from lz.replication import replicator

from gon.angular import Orientation
from gon.base import Point
from gon.shaped.subdivisional import QuadEdge
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


triplicate = replicator(3)


def points_do_not_lie_on_the_same_line(points: Sequence[Point]) -> bool:
    return any(angle.orientation is not Orientation.COLLINEAR
               for angle in to_angles(points))


def edge_to_relatives_endpoints(edge: QuadEdge) -> Tuple[Point, ...]:
    return tuple(relative.end for relative in edge_to_ring(edge))


def edge_to_ring(edge: QuadEdge) -> Iterable[QuadEdge]:
    start = edge
    while True:
        yield edge
        edge = edge.left_from_start
        if edge is start:
            break
