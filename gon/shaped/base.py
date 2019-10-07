from abc import (ABC,
                 abstractmethod)
from enum import (IntEnum,
                  unique)
from functools import reduce
from operator import (attrgetter,
                      itemgetter)
from typing import (Sequence,
                    Tuple)

from lz.functional import compose
from lz.hints import Domain
from lz.sorting import Key
from memoir import cached
from reprit.base import generate_repr

from gon import documentation
from gon.angular import (Angle,
                         Orientation)
from gon.base import Point
from gon.hints import (Permutation,
                       Scalar)
from gon.linear import Segment
from gon.robust.utils import (Expansion,
                              sum_expansions,
                              two_product,
                              two_two_diff)
from gon.utils import (inverse_permutation,
                       to_index_min)
from . import triangular
from .contracts import (self_intersects,
                        vertices_forms_convex_polygon,
                        vertices_forms_strict_polygon)
from .hints import Vertices
from .utils import (to_convex_hull,
                    to_edges)


@unique
class LocationKind(IntEnum):
    OUTSIDE = 0
    INSIDE = 1
    ON_BOUNDARY = 2


@documentation.setup(docstring='Polygons interface.',
                     reference='http://tiny.cc/n_gon')
class Polygon(ABC):
    @abstractmethod
    def location_of(self, point: Point) -> LocationKind:
        """
        Locates whether the point lies outside the polygon,
        on its boundary or inside it.
        """

    def __contains__(self, point: Point) -> bool:
        """Checks if the point lies inside the polygon or on its boundary."""
        return self.location_of(point) is not LocationKind.OUTSIDE

    @abstractmethod
    def __eq__(self, other: 'Polygon') -> bool:
        """Checks if polygons are equal."""

    @abstractmethod
    def __hash__(self) -> int:
        """Returns hash value of the polygon."""

    @property
    @abstractmethod
    def vertices(self) -> Vertices:
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


@documentation.setup(docstring='Sorts vertices by lexicographical order '
                               'and rotates to establish '
                               'counter-clockwise orientation.',
                     reference='http://tiny.cc/simple_polygon',
                     time_complexity='O(n), where\n'
                                     'n -- vertices count')
class SimplePolygon(Polygon):
    __slots__ = ('_order', '_vertices')

    def __init__(self, vertices: Vertices) -> None:
        self._order, self._vertices = _normalize_vertices(tuple(vertices))

    __repr__ = generate_repr(__init__)

    @documentation.setup(docstring='Locates whether the point lies '
                                   'outside the polygon, on its boundary '
                                   'or inside it.',
                         origin='"PNPOLY" ray-casting algorithm',
                         reference='http://tiny.cc/pnpoly',
                         time_complexity='O(n), where\n'
                                         'n -- polygon\'s vertices count')
    def location_of(self, point: Point) -> LocationKind:
        """
        >>> polygon = SimplePolygon([Point(-1, -1), Point(1, -1),
        ...                          Point(1, 1), Point(-1, 1)])
        >>> polygon.location_of(Point(1, 1)) is LocationKind.ON_BOUNDARY
        True
        >>> polygon.location_of(Point(0, 0)) is LocationKind.INSIDE
        True
        >>> polygon.location_of(Point(2, 2)) is LocationKind.OUTSIDE
        True
        >>> polygon.location_of(Point(-2, -2)) is LocationKind.OUTSIDE
        True
        """
        result = False
        for edge in to_edges(self._vertices):
            if point in edge:
                return LocationKind.ON_BOUNDARY
            if ((edge.start.y > point.y) is not (edge.end.y > point.y)
                    and ((edge.end.y > edge.start.y)
                         is (edge.orientation_with(point)
                             is Orientation.COUNTERCLOCKWISE))):
                result = not result
        return LocationKind(result)

    @documentation.setup(docstring='Checks if polygons are equal.',
                         time_complexity=
                         'O(min(m, n)), where\n'
                         'm -- polygon\'s vertices count,\n'
                         'n -- compared polygon\'s vertices count')
    def __eq__(self, other: Polygon) -> bool:
        """
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

    @documentation.setup(docstring='Returns hash value of the polygon.',
                         time_complexity='O(n), where\n'
                                         'n -- polygon\'s vertices count')
    def __hash__(self) -> int:
        """
        >>> polygon = SimplePolygon([Point(-1, -1), Point(1, -1),
        ...                          Point(1, 1), Point(-1, 1)])
        >>> hash(polygon) == hash(polygon)
        True
        """
        return hash(self._vertices)

    @cached.property_
    @documentation.setup(docstring='Returns vertices of the polygon '
                                   'in the original order.\n'
                                   'Original order is the order '
                                   'from polygon\'s definition.',
                         origin='inversion of vertices\' permutation'
                                'produced during polygon\'s creation',
                         reference='http://tiny.cc/inverse_permutation',
                         time_complexity='O(n), where\n'
                                         'n -- polygon\'s vertices count')
    def vertices(self) -> Vertices:
        """
        >>> vertices = [Point(-1, -1), Point(1, -1), Point(1, 1), Point(-1, 1)]
        >>> polygon = SimplePolygon(vertices)
        >>> all(actual == original
        ...     for actual, original in zip(polygon.vertices, vertices))
        True
        """
        return itemgetter(*inverse_permutation(self._order))(self._vertices)

    @cached.property_
    @documentation.setup(docstring='Returns area of the polygon.',
                         origin='"Shoelace formula"',
                         reference='http://tiny.cc/shoelace_formula',
                         time_complexity='O(n), where\n'
                                         'n -- polygon\'s vertices count')
    def area(self) -> Scalar:
        """
        >>> polygon = SimplePolygon([Point(-1, -1), Point(1, -1),
        ...                          Point(1, 1), Point(-1, 1)])
        >>> polygon.area == 4
        True
        """
        expansions = [_edge_to_endpoints_cross_product_z(edge)
                      for edge in to_edges(self._vertices)]
        return abs(reduce(sum_expansions, expansions)[-1]) / 2

    @cached.property_
    @documentation.setup(docstring='Returns convex hull of the polygon.',
                         origin='"Monotone chain" (aka "Andrew\'s algorithm")',
                         reference='http://tiny.cc/convex_hull',
                         time_complexity='O(n * log n), where\n'
                                         'n -- polygon\'s vertices count')
    def convex_hull(self) -> Polygon:
        """
        >>> polygon = SimplePolygon([Point(-1, -1), Point(1, -1),
        ...                          Point(1, 1), Point(-1, 1)])
        >>> polygon.convex_hull == polygon
        True
        """
        if len(self._vertices) == 3:
            return self
        return SimplePolygon(to_convex_hull(self._vertices))

    @cached.property_
    @documentation.setup(docstring='Checks if the polygon is convex.',
                         origin='property that each internal angle '
                                'of convex polygon is less than 180 degrees',
                         reference='http://tiny.cc/convex_polygon',
                         time_complexity='O(n), where\n'
                                         'n -- polygon\'s vertices count')
    def is_convex(self) -> bool:
        """
        >>> polygon = SimplePolygon([Point(-1, -1), Point(1, -1),
        ...                          Point(1, 1), Point(-1, 1)])
        >>> polygon.is_convex
        True
        """
        return vertices_forms_convex_polygon(self._vertices)

    @property
    @documentation.setup(docstring='Returns triangulation of the polygon.',
                         origin='constrained Delaunay triangulation',
                         reference='http://tiny.cc/delaunay_triangulation\n'
                                   'http://tiny.cc/constrained_delaunay',
                         time_complexity='O(n * log n) for convex polygons,\n'
                                         'O(n^2) for concave polygons, where\n'
                                         'n -- polygon\'s vertices count')
    def triangulation(self) -> Sequence[Polygon]:
        """
        >>> polygon = SimplePolygon([Point(-1, -1), Point(1, -1),
        ...                          Point(1, 1), Point(-1, 1)])
        >>> set(polygon.triangulation) == {SimplePolygon([Point(-1, 1),
        ...                                               Point(1, -1),
        ...                                               Point(1, 1)]),
        ...                                SimplePolygon([Point(-1, 1),
        ...                                               Point(-1, -1),
        ...                                               Point(1, -1)])}
        True
        """
        return [SimplePolygon(vertices)
                for vertices in triangular.constrained_delaunay_vertices(
                    self._vertices,
                    boundary=tuple(to_edges(self._vertices)))]


def _edge_to_endpoints_cross_product_z(edge: Segment) -> Expansion:
    start_x_end_y, start_x_end_y_tail = two_product(edge.start.x,
                                                    edge.end.y)
    start_y_end_x, start_y_end_x_tail = two_product(edge.start.y,
                                                    edge.end.x)
    if not start_x_end_y_tail and not start_y_end_x_tail:
        return 0, 0, 0, start_x_end_y - start_y_end_x
    return two_two_diff(start_x_end_y, start_x_end_y_tail,
                        start_y_end_x, start_y_end_x_tail)


@documentation.setup(docstring='Creates polygon from given vertices.',
                     origin='vertices validation '
                            'for non-collinear consecutive edges '
                            '& checking of self-intersection',
                     reference='http://tiny.cc/n_gon',
                     time_complexity='O(n^2), where\n'
                                     'n -- vertices count')
def to_polygon(vertices: Vertices) -> Polygon:
    """
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


def _normalize_vertices(vertices: Vertices) -> Tuple[Permutation, Vertices]:
    order, vertices = zip(*_rotate_sequence(tuple(enumerate(vertices)),
                                            key=compose(attrgetter('x', 'y'),
                                                        itemgetter(1))))
    first_angle = Angle(vertices[-1], vertices[0], vertices[1])
    if first_angle.orientation is not Orientation.CLOCKWISE:
        order, vertices = (order[:1] + order[1:][::-1],
                           vertices[:1] + vertices[1:][::-1])
    return order, vertices


def _rotate_sequence(sequence: Sequence[Domain],
                     *,
                     key: Key = None) -> Sequence[Domain]:
    index_min = to_index_min(sequence,
                             key=key)
    return sequence[index_min:] + sequence[:index_min]
