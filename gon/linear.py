from fractions import Fraction
from functools import reduce
from typing import (Iterator,
                    List,
                    Sequence,
                    Tuple)

from bentley_ottmann.planar import edges_intersect
from reprit.base import generate_repr
from robust.hints import Expansion
from robust.linear import (SegmentsRelationship,
                           segment_contains,
                           segments_relationship)
from robust.utils import (sum_expansions,
                          two_product,
                          two_two_diff)

from .angular import (Orientation,
                      to_orientation)
from .geometry import Geometry
from .hints import Coordinate
from .primitive import (Point,
                        RawPoint)

RawSegment = Tuple[RawPoint, RawPoint]
SegmentsRelationship = SegmentsRelationship
Vertices = Sequence[Point]
RawContour = List[RawPoint]

MIN_VERTICES_COUNT = 3


class Segment(Geometry):
    __slots__ = '_start', '_end', '_raw'

    def __init__(self, start: Point, end: Point) -> None:
        self._start, self._end = start, end
        self._raw = start.raw(), end.raw()

    __repr__ = generate_repr(__init__)

    @property
    def start(self) -> Point:
        return self._start

    @property
    def end(self) -> Point:
        return self._end

    def raw(self) -> RawSegment:
        return self._raw

    @classmethod
    def from_raw(cls, raw: RawSegment) -> 'Segment':
        raw_start, raw_end = raw
        start, end = Point.from_raw(raw_start), Point.from_raw(raw_end)
        return cls(start, end)

    def validate(self) -> None:
        self._start.validate()
        self._end.validate()
        if self._start == self._end:
            raise ValueError('Segment is degenerate.')

    def __eq__(self, other: 'Segment') -> bool:
        return (self._start == other._start and self._end == other._end
                or self._start == other._end and self._end == other._start
                if isinstance(other, Segment)
                else NotImplemented)

    def __hash__(self) -> int:
        return hash(frozenset(self._raw))

    def __contains__(self, point: Point) -> bool:
        return segment_contains(self._raw, point.raw())

    def relationship_with(self, other: 'Segment') -> SegmentsRelationship:
        return segments_relationship(self._raw, other._raw)

    def orientation_with(self, point: Point) -> Orientation:
        return to_orientation(self._end, self._start, point)


class Contour(Geometry):
    __slots__ = '_vertices',

    def __init__(self, vertices: Vertices) -> None:
        self._vertices = tuple(vertices)
        self._raw = [vertex.raw() for vertex in vertices]

    __repr__ = generate_repr(__init__)

    def __hash__(self) -> int:
        return hash(self._vertices)

    def __eq__(self, other: 'Geometry') -> bool:
        if self is other:
            return True
        return (self._vertices == other._vertices
                if isinstance(other, Contour)
                else NotImplemented)

    @property
    def vertices(self) -> Vertices:
        return list(self._vertices)

    def raw(self) -> RawContour:
        return self._raw[:]

    @classmethod
    def from_raw(cls, raw: RawContour) -> 'Contour':
        return cls([Point.from_raw(raw_vertex) for raw_vertex in raw])

    @property
    def normalized(self) -> 'Contour':
        vertices = self._vertices
        min_index = min(range(len(vertices)),
                        key=vertices.__getitem__)
        return Contour(vertices[min_index:] + vertices[:min_index])

    @property
    def orientation(self) -> 'Orientation':
        vertices = self.normalized._vertices
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
        for vertex in self._vertices:
            vertex.validate()
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


def forms_convex_polygon(contour: Contour) -> bool:
    vertices = contour.vertices
    if len(vertices) == 3:
        return True
    orientations = _vertices_to_orientations(vertices)
    base_orientation = next(orientations)
    # orientation change means that internal angle is greater than 180 degrees
    return all(orientation is base_orientation for orientation in orientations)


def _vertices_to_orientations(vertices: Vertices) -> Iterator[Orientation]:
    vertices_count = len(vertices)
    return (to_orientation(vertices[index - 1], vertices[index],
                           vertices[(index + 1) % vertices_count])
            for index in range(vertices_count))


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
