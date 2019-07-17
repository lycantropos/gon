from abc import (ABC,
                 abstractmethod)
from itertools import (cycle,
                       islice,
                       starmap)
from operator import (attrgetter,
                      itemgetter)
from typing import (Iterable,
                    Sequence,
                    Tuple)

from lz.functional import compose
from lz.hints import Domain
from lz.iterating import pairwise
from lz.sorting import Key
from memoir import cached
from reprit.base import generate_repr

from .angular import (Angle,
                      Orientation)
from .base import Point
from .hints import (Permutation,
                    Scalar)
from .linear import (Segment,
                     to_interval)
from .utils import (inverse_permutation,
                    is_odd,
                    to_index_min,
                    triplewise)


class Polygon(ABC):
    @abstractmethod
    def __hash__(self) -> int:
        pass

    @abstractmethod
    def __eq__(self, other: 'Polygon') -> bool:
        pass

    @abstractmethod
    def __contains__(self, point: Point) -> bool:
        pass

    @property
    @abstractmethod
    def vertices(self) -> Sequence[Point]:
        pass

    @property
    @abstractmethod
    def area(self) -> Scalar:
        pass

    @property
    @abstractmethod
    def convex_hull(self) -> 'Polygon':
        pass

    @property
    @abstractmethod
    def is_convex(self) -> bool:
        pass


class SimplePolygon(Polygon):
    __slots__ = ('_order', '_vertices')

    def __init__(self, vertices: Sequence[Point]) -> None:
        self._order, self._vertices = _normalize_vertices(tuple(vertices))

    __repr__ = generate_repr(__init__)

    def __hash__(self) -> int:
        return hash(self._vertices)

    def __eq__(self, other: Polygon) -> bool:
        if not isinstance(other, Polygon):
            return NotImplemented
        if not isinstance(other, SimplePolygon):
            return False
        return self._vertices == other._vertices

    def __contains__(self, point: Point) -> bool:
        leftmost_bottom_vertex = self._vertices[0]
        if (point.x < leftmost_bottom_vertex.x
                or point.x == leftmost_bottom_vertex.x
                and point.y < leftmost_bottom_vertex.y):
            return False
        try:
            segment = to_interval(leftmost_bottom_vertex, point)
        except ValueError:
            # degenerate segment, point is a leftmost vertex
            return True
        edges_intersections = 0
        for edge in to_edges(self._vertices):
            intersects_with_edge = segment.intersects_with(edge)
            if intersects_with_edge and point in edge:
                return True
            edges_intersections += intersects_with_edge
        return is_odd(edges_intersections)

    @cached.property_
    def vertices(self) -> Sequence[Point]:
        return itemgetter(*inverse_permutation(self._order))(self._vertices)

    @cached.property_
    def area(self) -> Scalar:
        return abs(sum(edge.start.x * edge.end.y - edge.start.y * edge.end.x
                       for edge in to_edges(self._vertices))) / 2

    @cached.property_
    def convex_hull(self) -> Polygon:
        if len(self._vertices) == 3:
            return self
        return SimplePolygon(to_convex_hull(self._vertices))

    @cached.property_
    def is_convex(self) -> bool:
        if len(self._vertices) == 3:
            return True
        orientations = (angle.orientation
                        for angle in to_angles(self._vertices))
        base_orientation = next(orientations)
        return all(orientation == base_orientation
                   for orientation in orientations)


def to_polygon(vertices: Sequence[Point]) -> Polygon:
    if len(vertices) < 3:
        raise ValueError('Polygon should have at least 3 vertices.')
    if not vertices_forms_angles(vertices):
        raise ValueError('Consecutive vertices triplets '
                         'should not be on the same line.')
    if self_intersects(vertices):
        raise ValueError('Simple polygon should not be self-intersecting.')
    return SimplePolygon(vertices)


def _normalize_vertices(vertices: Sequence[Point]) -> Tuple[Permutation,
                                                            Sequence[Point]]:
    order, vertices = zip(*_shift_sequence(tuple(enumerate(vertices)),
                                           key=compose(attrgetter('x', 'y'),
                                                       itemgetter(1))))
    first_angle = Angle(vertices[0], vertices[1], vertices[2])
    if first_angle.orientation != Orientation.COUNTERCLOCKWISE:
        order, vertices = (order[:1] + order[1:][::-1],
                           vertices[:1] + vertices[1:][::-1])
    return order, vertices


def _shift_sequence(sequence: Sequence[Domain],
                    *,
                    key: Key = None) -> Sequence[Domain]:
    index_min = to_index_min(sequence,
                             key=key)
    return sequence[index_min:] + sequence[:index_min]


def to_convex_hull(points: Sequence[Point]) -> Sequence[Point]:
    points = sorted(points,
                    key=attrgetter('x', 'y'))
    lower = _to_sub_hull(points)
    upper = _to_sub_hull(reversed(points))
    return lower[:-1] + upper[:-1]


def _to_sub_hull(points: Iterable[Point]) -> Sequence[Point]:
    result = []
    for point in points:
        while len(result) >= 2:
            if (Angle(result[-2], result[-1], point).orientation
                    != Orientation.COUNTERCLOCKWISE):
                del result[-1]
            else:
                break
        result.append(point)
    return result


def vertices_forms_angles(vertices: Sequence[Point]) -> bool:
    return all(angle.orientation != Orientation.COLLINEAR
               for angle in to_angles(vertices))


def to_angles(vertices: Sequence[Point]) -> Iterable[Angle]:
    return starmap(Angle,
                   triplewise(islice(cycle(vertices), len(vertices) + 2)))


def self_intersects(vertices: Sequence[Point]) -> bool:
    if len(vertices) == 3:
        return False
    edges = tuple(to_edges(vertices))
    for index, edge in enumerate(edges):
        # skipping neighbours because they always intersect
        # NOTE: first & last edges are neighbours
        if any(edge.intersects_with(non_neighbour)
               for non_neighbour in _to_non_neighbours(index, edges)):
            return True
    return False


def _to_non_neighbours(edge_index: int,
                       edges: Sequence[Segment]) -> Sequence[Segment]:
    return (edges[max(edge_index + 2 - len(edges), 0):max(edge_index - 1, 0)]
            + edges[edge_index + 2:edge_index - 1 + len(edges)])


def to_edges(vertices: Sequence[Point]) -> Iterable[Segment]:
    return (to_interval(start, end)
            for start, end in pairwise(islice(cycle(vertices),
                                              len(vertices) + 1)))
