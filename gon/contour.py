from fractions import Fraction
from functools import reduce
from typing import (Iterable,
                    List,
                    Sequence)
from weakref import WeakKeyDictionary

from bentley_ottmann.planar import edges_intersect
from memoir import cached
from reprit.base import generate_repr
from robust.hints import Expansion
from robust.utils import (sum_expansions,
                          two_product,
                          two_two_diff)

from gon.angular import (Orientation,
                         to_orientation)
from gon.geometry import Geometry
from gon.hints import Coordinate
from gon.point import (Point,
                       RawPoint)

MIN_VERTICES_COUNT = 3

Vertices = Sequence[Point]
RawContour = List[RawPoint]


class Contour(Geometry):
    __slots__ = '_vertices',

    def __init__(self, vertices: Iterable[Point]) -> None:
        self._vertices = tuple(vertices)

    __repr__ = generate_repr(__init__)

    def __hash__(self) -> int:
        return hash(self._vertices)

    def __eq__(self, other: 'Geometry') -> int:
        return (self._vertices == other._vertices
                if isinstance(other, Contour)
                else NotImplemented)

    @property
    def vertices(self) -> Vertices:
        return self._vertices

    @cached.map_(WeakKeyDictionary())
    def raw(self) -> RawContour:
        return [vertex.raw() for vertex in self._vertices]

    @classmethod
    def from_raw(cls, raw: RawContour) -> 'Contour':
        return cls(Point.from_raw(raw_vertex) for raw_vertex in raw)

    @cached.property_
    def normalized(self) -> 'Contour':
        vertices = self._vertices
        min_index = min(range(len(vertices)),
                        key=vertices.__getitem__)
        return Contour(vertices[min_index:] + vertices[:min_index])

    @cached.property_
    def orientation(self) -> 'Orientation':
        vertices = self.normalized.vertices
        return to_orientation(vertices[0], vertices[-1], vertices[1])

    def to_clockwise(self) -> 'Contour':
        return (self
                if self.orientation is Orientation.CLOCKWISE
                else self.reverse())

    def to_counterclockwise(self) -> 'Contour':
        return (self
                if self.orientation is Orientation.COUNTERCLOCKWISE
                else self.reverse())

    def reverse(self) -> 'Contour':
        vertices = self._vertices
        return Contour(vertices[:1] + vertices[:0:-1])

    def validate(self) -> None:
        if len(self._vertices) < MIN_VERTICES_COUNT:
            raise ValueError('Contour should have '
                             'at least {expected} vertices, '
                             'but found {actual}.'
                             .format(expected=MIN_VERTICES_COUNT,
                                     actual=len(self._vertices)))
        if any(orientation is Orientation.COLLINEAR
               for orientation in _vertices_to_orientations(self._vertices)):
            raise ValueError('Consecutive vertices triplets '
                             'should not be on the same line.')
        if edges_intersect(self.raw()):
            raise ValueError('Contour should not be self-intersecting.')


def _vertices_to_orientations(vertices: Vertices) -> Iterable[Orientation]:
    vertices_count = len(vertices)
    return (to_orientation(vertices[index - 1], vertices[index],
                           vertices[(index + 1) % vertices_count])
            for index in range(vertices_count))


def forms_convex_polygon(contour: Contour) -> bool:
    if len(contour.vertices) == 3:
        return True
    orientations = iter(_vertices_to_orientations(contour.vertices))
    base_orientation = next(orientations)
    # orientation change means
    # that internal angle is greater than 180 degrees
    return all(orientation is base_orientation for orientation in orientations)


def _to_first_vertex(contour: Contour) -> Point:
    return contour.vertices[0]


def to_area(contour: Contour) -> Coordinate:
    return abs(to_signed_area(contour))


def to_signed_area(contour: Contour) -> Coordinate:
    vertices = contour.vertices
    double_area = reduce(sum_expansions,
                         [_to_endpoints_cross_product_z(vertices[index - 1],
                                                        vertices[index])
                          for index in range(len(vertices))])[-1]
    return (Fraction(double_area, 2)
            if isinstance(double_area, int)
            else double_area / 2)


def _to_endpoints_cross_product_z(start: Point, end: Point) -> Expansion:
    minuend, minuend_tail = two_product(start.x, end.y)
    subtrahend, subtrahend_tail = two_product(start.y, end.x)
    return (two_two_diff(minuend, minuend_tail, subtrahend, subtrahend_tail)
            if minuend_tail or subtrahend_tail
            else (minuend - subtrahend,))
