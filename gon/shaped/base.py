from abc import (ABC,
                 abstractmethod)
from enum import (IntEnum,
                  unique)
from operator import (attrgetter,
                      itemgetter)
from typing import (Sequence,
                    Tuple)

from lz.functional import compose
from lz.hints import Domain
from lz.sorting import Key
from memoir import cached
from reprit.base import generate_repr

from gon.angular import (Angle,
                         Orientation)
from gon.base import Point
from gon.hints import (Permutation,
                       Scalar)
from gon.linear import Segment
from gon.utils import (inverse_permutation,
                       to_index_min,
                       to_sign)
from . import triangular
from .contracts import (self_intersects,
                        vertices_forms_strict_polygon,
                        vertices_forms_convex_polygon)
from .utils import (to_convex_hull,
                    to_edges)


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

    @abstractmethod
    def __eq__(self, other: 'Polygon') -> bool:
        """Checks if polygons are equal."""

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

    @property
    @abstractmethod
    def triangulation(self) -> Sequence['Polygon']:
        """Returns triangulation of the polygon."""


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
            if ((edge.start.y > point.y) is not (edge.end.y > point.y)
                    and _is_point_to_the_left_of_line(point, edge)):
                result = not result
        return InclusionKind(result)

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
        return vertices_forms_convex_polygon(self._vertices)

    @property
    def triangulation(self) -> Sequence[Polygon]:
        """
        Returns triangulation of the polygon.

        Based on:
            constrained Delaunay triangulation.

        Reference:
            https://www.newcastle.edu.au/__data/assets/pdf_file/0019/22519/23_A-fast-algortithm-for-generating-constrained-Delaunay-triangulations.pdf

        Time complexity:
            O(n * log n), where
            n -- polygon's vertices count.
        """
        result = triangular.constrained_delaunay(
                self._vertices,
                constraints=to_edges(self._vertices))
        return [SimplePolygon(vertices) for vertices in result]


def _is_point_to_the_left_of_line(point: Point, line_segment: Segment) -> bool:
    y_diff = line_segment.end.y - line_segment.start.y
    return ((point.x - line_segment.end.x) * abs(y_diff)
            < ((line_segment.end.x - line_segment.start.x)
               * (point.y - line_segment.end.y)
               * to_sign(y_diff)))


def _point_not_inside(point: Point, polygon: Polygon) -> bool:
    return polygon.__contains__(point) is not InclusionKind.INSIDE


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
    if not vertices_forms_strict_polygon(vertices):
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
    first_angle = Angle(vertices[-1], vertices[0], vertices[1])
    if first_angle.orientation is not Orientation.CLOCKWISE:
        order, vertices = (order[:1] + order[1:][::-1],
                           vertices[:1] + vertices[1:][::-1])
    return order, vertices


def _shift_sequence(sequence: Sequence[Domain],
                    *,
                    key: Key = None) -> Sequence[Domain]:
    index_min = to_index_min(sequence,
                             key=key)
    return sequence[index_min:] + sequence[:index_min]
