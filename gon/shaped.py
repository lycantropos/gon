from abc import (ABC,
                 abstractmethod)
from enum import (IntEnum,
                  unique)
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
                     to_segment)
from .utils import (inverse_permutation,
                    to_index_min,
                    triplewise)


@unique
class InclusionKind(IntEnum):
    OUTSIDE = 0
    INSIDE = 1
    ON_BOUNDARY = 2


class Polygon(ABC):
    """
    Polygons interface.

    Reference:
        https://en.wikipedia.org/wiki/Polygon
    """

    @abstractmethod
    def __contains__(self, point: Point) -> InclusionKind:
        """Checks if the point lies inside the polygon or on its boundary."""
        pass

    @abstractmethod
    def __eq__(self, other: 'Polygon') -> bool:
        """Checks if polygons are equal."""

    @abstractmethod
    def __ge__(self, other: 'Polygon') -> bool:
        """Checks if the polygon is a superset of the compared one."""

    def issuperset(self, other: 'Polygon') -> bool:
        """Checks if the polygon is a superset of the compared one."""
        return self >= other

    def __gt__(self, other: 'Polygon') -> bool:
        """Checks if the polygon is a proper superset of the compared one."""
        return self >= other and self != other

    @abstractmethod
    def __le__(self, other: 'Polygon') -> bool:
        """Checks if the polygon is a proper subset of the compared one."""

    def issubset(self, other: 'Polygon') -> bool:
        """Checks if the polygon is a superset of the compared one."""
        return self <= other

    def __lt__(self, other: 'Polygon') -> bool:
        """Checks if the polygon is a proper superset of the compared one."""
        return self <= other and self != other

    @abstractmethod
    def __hash__(self) -> int:
        """Returns hash value of the polygon."""

    @property
    @abstractmethod
    def vertices(self) -> Sequence[Point]:
        """Returns vertices of the polygon."""

    @property
    @abstractmethod
    def area(self) -> Scalar:
        """Returns area of the polygon."""

    @property
    @abstractmethod
    def convex_hull(self) -> 'Polygon':
        """Returns convex hull of the polygon."""

    @property
    @abstractmethod
    def is_convex(self) -> bool:
        """Checks if the polygon is convex."""


class SimplePolygon(Polygon):
    """
    Sorts vertices by lexicographical order
    and rotates to establish counter-clockwise orientation.

    Reference:
        https://en.wikipedia.org/wiki/Simple_polygon

    Time complexity:
        O(n), where
        n -- vertices count.
    """

    __slots__ = ('_order', '_vertices')

    def __init__(self, vertices: Sequence[Point]) -> None:
        self._order, self._vertices = _normalize_vertices(tuple(vertices))

    __repr__ = generate_repr(__init__)

    def __contains__(self, point: Point) -> InclusionKind:
        """
        Checks if the point lies inside the polygon or on its boundary.

        Based on:
            "PNPOLY" ray-casting algorithm.

        Reference:
            https://wrf.ecse.rpi.edu//Research/Short_Notes/pnpoly.html

        Time complexity:
            O(n), where
            n -- polygon's vertices count.

        >>> polygon = SimplePolygon([Point(-1, -1), Point(1, -1),
        ...                          Point(1, 1), Point(-1, 1)])
        >>> Point(1, 1) in polygon
        True
        >>> Point(0, 0) in polygon
        True
        >>> Point(2, 2) in polygon
        False
        >>> Point(-2, -2) in polygon
        False
        """
        result = False
        for edge in to_edges(self._vertices):
            if point in edge:
                return InclusionKind.ON_BOUNDARY
            if (((edge.start.y > point.y) is not (edge.end.y > point.y))
                    and point.x < ((edge.end.x - edge.start.x)
                                   * (point.y - edge.end.y)
                                   / (edge.end.y - edge.start.y)
                                   + edge.end.x)):
                result = not result
        return InclusionKind(result)

    def __ge__(self, other: Polygon) -> bool:
        """
        Checks if the polygon is a superset of the compared one.

        Reference:
            https://en.wikipedia.org/wiki/Subset

        Time complexity:
            O(m * n), where
            m -- polygon's vertices count,
            n -- compared polygon's vertices count.
        """
        return (all(vertex in self for vertex in other.vertices)
                and all(_point_not_inside(vertex, other)
                        for vertex in self._vertices))

    def __le__(self, other: Polygon) -> bool:
        """
        Checks if the polygon is a subset of the compared one.

        Reference:
            https://en.wikipedia.org/wiki/Subset

        Time complexity:
            O(m * n), where
            m -- polygon's vertices count,
            n -- compared polygon's vertices count.
        """
        if not isinstance(other, SimplePolygon):
            return other >= self
        return (all(vertex in other for vertex in self._vertices)
                and all(_point_not_inside(vertex, self)
                        for vertex in other._vertices))

    def __eq__(self, other: Polygon) -> bool:
        """
        Checks if polygons are equal.

        Time complexity:
            O(min(m, n)), where
            m -- polygon's vertices count,
            n -- compared polygon's vertices count.

        >>> polygon = SimplePolygon([Point(-1, -1), Point(1, -1),
        ...                          Point(1, 1), Point(-1, 1)])
        >>> polygon == polygon
        True
        """
        if not isinstance(other, Polygon):
            return NotImplemented
        if not isinstance(other, SimplePolygon):
            return False
        return self._vertices == other._vertices

    def __hash__(self) -> int:
        """
        Returns hash value of the polygon.

        Time complexity:
            O(n), where
            n -- polygon's vertices count.

        >>> polygon = SimplePolygon([Point(-1, -1), Point(1, -1),
        ...                          Point(1, 1), Point(-1, 1)])
        >>> hash(polygon) == hash(polygon)
        True
        """
        return hash(self._vertices)

    @cached.property_
    def vertices(self) -> Sequence[Point]:
        """
        Returns vertices of the polygon in the original order.
        Original order is the order from polygon's definition.

        Based on:
            inversion of vertices' permutation
            produced during polygon's creation.

        Reference:
            http://mathworld.wolfram.com/InversePermutation.html

        Time complexity:
            O(n), where
            n -- polygon's vertices count.

        >>> vertices = [Point(-1, -1), Point(1, -1), Point(1, 1), Point(-1, 1)]
        >>> polygon = SimplePolygon(vertices)
        >>> all(actual == original
        ...     for actual, original in zip(polygon.vertices, vertices))
        True
        """
        return itemgetter(*inverse_permutation(self._order))(self._vertices)

    @cached.property_
    def area(self) -> Scalar:
        """
        Returns area of the polygon.

        Based on:
            "Shoelace formula".

        Reference:
            https://en.wikipedia.org/wiki/Shoelace_formula

        Time complexity:
            O(n), where
            n -- polygon's vertices count.

        >>> polygon = SimplePolygon([Point(-1, -1), Point(1, -1),
        ...                          Point(1, 1), Point(-1, 1)])
        >>> polygon.area == 4
        True
        """
        return abs(sum(edge.start.x * edge.end.y - edge.start.y * edge.end.x
                       for edge in to_edges(self._vertices))) / 2

    @cached.property_
    def convex_hull(self) -> Polygon:
        """
        Returns convex hull of the polygon.

        Based on:
            "Monotone chain" (aka "Andrew's algorithm").

        Reference:
            https://en.wikibooks.org/wiki/Algorithm_Implementation/Geometry/Convex_hull/Monotone_chain

        Time complexity:
            O(n * log n), where
            n -- polygon's vertices count.

        >>> polygon = SimplePolygon([Point(-1, -1), Point(1, -1),
        ...                          Point(1, 1), Point(-1, 1)])
        >>> polygon.convex_hull == polygon
        True
        """
        if len(self._vertices) == 3:
            return self
        return SimplePolygon(to_convex_hull(self._vertices))

    @cached.property_
    def is_convex(self) -> bool:
        """
        Checks if the polygon is convex.

        Based on:
            property that each internal angle of convex polygon
            is less than 180 degrees.

        Reference:
            https://en.wikipedia.org/wiki/Convex_polygon

        Time complexity:
            O(n), where
            n -- polygon's vertices count.

        >>> polygon = SimplePolygon([Point(-1, -1), Point(1, -1),
        ...                          Point(1, 1), Point(-1, 1)])
        >>> polygon.is_convex
        True
        """
        return _vertices_forms_convex_polygon(self._vertices)


def _point_not_inside(point: Point, polygon: Polygon) -> bool:
    return polygon.__contains__(point) is not InclusionKind.INSIDE


def _vertices_forms_convex_polygon(vertices: Sequence[Point]) -> bool:
    if len(vertices) == 3:
        return True
    orientations = (angle.orientation for angle in to_angles(vertices))
    base_orientation = next(orientations)
    # orientation change means
    # that internal angle is greater than 180 degrees
    return all(orientation == base_orientation for orientation in orientations)


def to_polygon(vertices: Sequence[Point]) -> Polygon:
    """
    Based on:
        vertices validation for non-collinear consecutive edges
        & checking of self-intersection.

    Reference:
        https://en.wikipedia.org/wiki/Polygon

    Time complexity:
        O(n^2), where
        n -- vertices count.

    >>> to_polygon([Point(-1, -1), Point(1, -1), Point(1, 1), Point(-1, 1)])
    SimplePolygon((Point(-1, -1), Point(1, -1), Point(1, 1), Point(-1, 1)))
    """
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
    return (to_segment(start, end)
            for start, end in pairwise(islice(cycle(vertices),
                                              len(vertices) + 1)))
