from collections import defaultdict
from functools import partial
from itertools import repeat
from typing import (Callable,
                    Hashable,
                    Iterable,
                    Sequence,
                    Set,
                    Tuple)

from hypothesis import strategies
from hypothesis.strategies import SearchStrategy
from lz.functional import (cleave,
                           compose,
                           pack)
from lz.hints import (Domain,
                      Map,
                      Range)
from lz.replication import replicator

from gon.angular import (Orientation,
                         to_orientation)
from gon.base import Point
from gon.hints import Coordinate
from gon.linear import (Segment,
                        to_segment)
from gon.shaped.hints import Contour
from gon.shaped.subdivisional import QuadEdge
from gon.shaped.utils import (to_orientations,
                              to_edges)

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


def to_tuples(elements: Strategy[Domain],
              *,
              size: int) -> Strategy[Tuple[Domain, ...]]:
    return strategies.tuples(*repeat(elements,
                                     times=size))


to_pairs = partial(to_tuples,
                   size=2)
to_triplets = partial(to_tuples,
                      size=3)


def cleave_in_tuples(*functions: Callable[[Strategy[Domain]], Strategy[Range]]
                     ) -> Callable[[Strategy[Domain]],
                                   Strategy[Tuple[Range, ...]]]:
    return compose(pack(strategies.tuples), cleave(*functions))


def points_do_not_lie_on_the_same_line(points: Sequence[Point]) -> bool:
    return any(orientation is not Orientation.COLLINEAR
               for orientation in to_orientations(points))


def edge_to_relatives_endpoints(edge: QuadEdge) -> Tuple[Point, ...]:
    return tuple(relative.end for relative in edge_to_ring(edge))


def edge_to_ring(edge: QuadEdge) -> Iterable[QuadEdge]:
    start = edge
    while True:
        yield edge
        edge = edge.left_from_start
        if edge is start:
            break


def to_boundary(contours: Iterable[Contour]) -> Set[Segment]:
    result = set()
    for contour in contours:
        result.symmetric_difference_update(to_edges(contour))
    shrink_collinear_segments(result)
    return result


def shrink_collinear_segments(segments: Set[Segment]) -> None:
    points_segments = defaultdict(set)
    for segment in segments:
        points_segments[segment.start].add(segment)
        points_segments[segment.end].add(segment.reversed)
    for point, point_segments in points_segments.items():
        first_segment, second_segment = point_segments
        if (first_segment.orientation_with(second_segment.start)
                is first_segment.orientation_with(second_segment.end)
                is Orientation.COLLINEAR):
            segments.remove(first_segment)
            segments.remove(second_segment)
            replacement = to_segment(first_segment.end, second_segment.end)
            replace_segment(points_segments[first_segment.end],
                            first_segment, replacement)
            replace_segment(points_segments[second_segment.end],
                            second_segment, replacement.reversed)
            segments.add(replacement)


def replace_segment(segments: Set[Segment],
                    source: Segment,
                    target: Segment) -> None:
    segments.remove(source)
    segments.add(target)


def is_non_origin_point(point: Point) -> bool:
    return bool(point.x or point.y)


def reflect_point(point: Point) -> Point:
    return Point(-point.x, -point.y)


def scale_segment(segment: Segment,
                  *,
                  scale: Coordinate) -> Segment:
    return Segment(segment.start,
                   Point(segment.start.x
                         + scale * (segment.end.x - segment.start.x),
                         segment.start.y
                         + scale * (segment.end.y - segment.start.y)))


def reflect_segment(segment: Segment) -> Segment:
    return scale_segment(segment,
                         scale=-1)


def to_origin(point: Point) -> Point:
    origin_coordinate = type(point.x)(0)
    return Point(origin_coordinate, origin_coordinate)


def to_perpendicular_point(point: Point) -> Point:
    return Point(-point.y, point.x)
