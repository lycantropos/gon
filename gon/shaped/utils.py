from itertools import (cycle,
                       islice)
from operator import attrgetter
from typing import (Iterable,
                    List,
                    Sequence)

from lz.iterating import pairwise

from gon.angular import (Angle,
                         Orientation)
from gon.base import Point
from gon.linear import (Segment,
                        to_segment)


def to_angles(vertices: Sequence[Point]) -> Iterable[Angle]:
    return (Angle(vertices[index - 1],
                  vertices[index],
                  vertices[(index + 1) % len(vertices)])
            for index in range(len(vertices)))


def to_edges(vertices: Sequence[Point]) -> Iterable[Segment]:
    return (to_segment(start, end)
            for start, end in pairwise(islice(cycle(vertices),
                                              len(vertices) + 1)))


def _to_non_neighbours(edge_index: int,
                       edges: Sequence[Segment]) -> Sequence[Segment]:
    return (edges[max(edge_index + 2 - len(edges), 0):max(edge_index - 1, 0)]
            + edges[edge_index + 2:edge_index - 1 + len(edges)])


def to_convex_hull(points: Sequence[Point]) -> List[Point]:
    points = sorted(points,
                    key=attrgetter('x', 'y'))
    lower = _to_sub_hull(points)
    upper = _to_sub_hull(reversed(points))
    return lower[:-1] + upper[:-1]


def _to_sub_hull(points: Iterable[Point]) -> List[Point]:
    result = []
    for point in points:
        while len(result) >= 2:
            if (Angle(result[-1], result[-2], point).orientation
                    != Orientation.COUNTERCLOCKWISE):
                del result[-1]
            else:
                break
        result.append(point)
    return result
