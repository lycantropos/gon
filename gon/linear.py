import math
from fractions import Fraction
from functools import reduce
from typing import (Iterator,
                    List,
                    Sequence,
                    Tuple)

from bentley_ottmann.planar import edges_intersect
from orient.planar import (Relation,
                           contour_in_contour,
                           point_in_contour,
                           point_in_segment,
                           segment_in_contour,
                           segment_in_segment)
from reprit.base import generate_repr
from robust.hints import Expansion
from robust.linear import segment_contains
from robust.utils import (sum_expansions,
                          two_product,
                          two_two_diff)

from .angular import (Orientation,
                      to_orientation)
from .geometry import (Geometry,
                       Linear)
from .hints import Coordinate
from .primitive import (Point,
                        RawPoint)

RawContour = List[RawPoint]
RawSegment = Tuple[RawPoint, RawPoint]
Vertices = Sequence[Point]

MIN_VERTICES_COUNT = 3


class Segment(Linear):
    __slots__ = '_start', '_end', '_raw'

    def __init__(self, start: Point, end: Point) -> None:
        """
        Initializes segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        """
        self._start, self._end = start, end
        self._raw = start.raw(), end.raw()

    __repr__ = generate_repr(__init__)

    def __contains__(self, point: Point) -> bool:
        """
        Checks if the point is inside the segment or on its boundary.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> Point(0, 0) in segment
        True
        >>> Point(1, 0) in segment
        True
        >>> Point(0, 1) in segment
        False
        >>> Point(1, 1) in segment
        False
        """
        return segment_contains(self._raw, point.raw())

    def __eq__(self, other: 'Segment') -> bool:
        """
        Checks if the segment is equal to the other.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment == segment
        True
        >>> segment == Segment.from_raw(((2, 0), (0, 0)))
        True
        >>> segment == Segment.from_raw(((0, 0), (1, 0)))
        False
        >>> segment == Segment.from_raw(((0, 0), (0, 2)))
        False
        """
        return (self._start == other._start and self._end == other._end
                or self._start == other._end and self._end == other._start
                if isinstance(other, Segment)
                else NotImplemented)

    def __ge__(self, other: 'Geometry') -> bool:
        return (False
                if isinstance(other, Contour)
                else super().__ge__(other))

    def __gt__(self, other: 'Geometry') -> bool:
        return (False
                if isinstance(other, Contour)
                else super().__gt__(other))

    def __hash__(self) -> int:
        """
        Returns hash value of the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> hash(segment) == hash(segment)
        True
        >>> hash(segment) == hash(Segment.from_raw(((2, 0), (0, 0))))
        True
        """
        return hash(frozenset(self._raw))

    @classmethod
    def from_raw(cls, raw: RawSegment) -> 'Segment':
        """
        Constructs contour from the combination of Python built-ins.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment == Segment(Point(0, 0), Point(2, 0))
        True
        """
        raw_start, raw_end = raw
        start, end = Point.from_raw(raw_start), Point.from_raw(raw_end)
        return cls(start, end)

    @property
    def end(self) -> Point:
        """
        Returns end of the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment.end == Point(2, 0)
        True
        """
        return self._end

    @property
    def length(self) -> Coordinate:
        return math.sqrt(_squared_distance(self.start, self.end))

    @property
    def start(self) -> Point:
        """
        Returns start of the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment.start == Point(0, 0)
        True
        """
        return self._start

    def raw(self) -> RawSegment:
        """
        Returns the segment as combination of Python built-ins.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment.raw()
        ((0, 0), (2, 0))
        """
        return self._raw

    def relate(self, other: 'Geometry') -> Relation:
        return (point_in_segment(other.raw(), self._raw)
                if isinstance(other, Point)
                else (segment_in_segment(other._raw, self._raw)
                      if isinstance(other, Segment)
                      else other.relate(self).complement))

    def validate(self) -> None:
        """
        Checks if endpoints are valid and unequal.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> Segment.from_raw(((0, 0), (2, 0))).validate()
        """
        self._start.validate()
        self._end.validate()
        if self._start == self._end:
            raise ValueError('Segment is degenerate.')


class Contour(Linear):
    __slots__ = '_vertices',

    def __init__(self, vertices: Vertices) -> None:
        """
        Initializes contour.

        Time complexity:
            ``O(len(vertices))``
        Memory complexity:
            ``O(len(vertices))``
        """
        self._vertices = tuple(vertices)
        self._raw = [vertex.raw() for vertex in vertices]

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'Contour') -> bool:
        """
        Checks if the contour is equal to the other.

        Time complexity:
            ``O(min(len(self.vertices), len(other.vertices)))``
        Memory complexity:
            ``O(1)``

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour == contour
        True
        >>> contour == Contour.from_raw([(0, 0), (1, 0), (1, 1), (0, 1)])
        False
        >>> contour == Contour.from_raw([(1, 0), (0, 0), (0, 1)])
        True
        """
        return self is other or (_contours_vertices_equal(self._vertices,
                                                          other._vertices)
                                 if isinstance(other, Contour)
                                 else (False
                                       if isinstance(other, Geometry)
                                       else NotImplemented))

    def __hash__(self) -> int:
        """
        Returns hash value of the contour.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(1)``

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> hash(contour) == hash(contour)
        True
        """
        return hash(self._vertices)

    def __le__(self, other: 'Geometry') -> bool:
        return (False
                if isinstance(other, Segment)
                else super().__le__(other))

    def __lt__(self, other: 'Geometry') -> bool:
        return (False
                if isinstance(other, Segment)
                else super().__lt__(other))

    @classmethod
    def from_raw(cls, raw: RawContour) -> 'Contour':
        """
        Constructs contour from the combination of Python built-ins.

        Time complexity:
            ``O(len(raw))``
        Memory complexity:
            ``O(len(raw))``

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour == Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        True
        """
        return cls([Point.from_raw(raw_vertex) for raw_vertex in raw])

    @property
    def length(self) -> Coordinate:
        vertices = self._vertices
        return sum(Segment(vertices[index - 1], vertices[index]).length
                   for index in range(len(vertices)))

    @property
    def normalized(self) -> 'Contour':
        """
        Returns contour in normalized form.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(1)`` if normalized already,
            ``O(len(self.vertices))`` -- otherwise

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.normalized == contour
        True
        """
        vertices = self._vertices
        min_index = min(range(len(vertices)),
                        key=vertices.__getitem__)
        return (Contour(vertices[min_index:] + vertices[:min_index])
                if min_index
                else self)

    @property
    def orientation(self) -> 'Orientation':
        """
        Returns orientation of the contour.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(1)`` if contour is normalized,
            ``O(len(self.vertices))`` -- otherwise

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.orientation is Orientation.COUNTERCLOCKWISE
        True
        """
        vertices = self.normalized._vertices
        return to_orientation(vertices[0], vertices[-1], vertices[1])

    @property
    def vertices(self) -> Vertices:
        """
        Returns vertices of the contour.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(len(self.vertices))``

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.vertices
        [Point(0, 0), Point(1, 0), Point(0, 1)]
        """
        return list(self._vertices)

    def raw(self) -> RawContour:
        """
        Returns the contour as combination of Python built-ins.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(len(self.vertices))``

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.raw()
        [(0, 0), (1, 0), (0, 1)]
        """
        return self._raw[:]

    def relate(self, other: 'Geometry') -> Relation:
        return (point_in_contour(other.raw(), self._raw)
                if isinstance(other, Point)
                else (segment_in_contour(other.raw(), self._raw)
                      if isinstance(other, Segment)
                      else (contour_in_contour(other._raw, self._raw)
                            if isinstance(other, Contour)
                            else other.relate(self).complement)))

    def reverse(self) -> 'Contour':
        """
        Returns the reversed contour.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(len(self.vertices))``

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.reverse() == contour
        False
        >>> contour.reverse().reverse() == contour
        True
        """
        vertices = self._vertices
        return Contour(vertices[:1] + vertices[:0:-1])

    def to_clockwise(self) -> 'Contour':
        """
        Returns the clockwise contour.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(1)`` if normalized and clockwise already,
            ``O(len(self.vertices))`` -- otherwise

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.to_clockwise() == contour
        False
        >>> contour.to_clockwise().orientation is Orientation.CLOCKWISE
        True
        """
        return (self
                if self.orientation is Orientation.CLOCKWISE
                else self.reverse())

    def to_counterclockwise(self) -> 'Contour':
        """
        Returns the counterclockwise contour.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(1)`` if normalized and counterclockwise already,
            ``O(len(self.vertices))`` -- otherwise

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.to_counterclockwise() == contour
        True
        >>> (contour.to_counterclockwise().orientation
        ...  is Orientation.COUNTERCLOCKWISE)
        True
        """
        return (self
                if self.orientation is Orientation.COUNTERCLOCKWISE
                else self.reverse())

    def validate(self) -> None:
        """
        Checks if vertices are valid.

        Time complexity:
            ``O(len(self.vertices) * log len(self.vertices))``
        Memory complexity:
            ``O(len(self.vertices))``

        >>> Contour.from_raw([(0, 0), (1, 0), (0, 1)]).validate()
        """
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
        if edges_intersect(self._raw):
            raise ValueError('Contour should not be self-intersecting.')


def forms_convex_polygon(contour: Contour) -> bool:
    vertices = contour._vertices
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


def to_signed_area(contour: Contour) -> Coordinate:
    vertices = contour._vertices
    double_area = reduce(sum_expansions,
                         (_to_endpoints_cross_product_z(vertices[index - 1],
                                                        vertices[index])
                          for index in range(len(vertices))))[-1]
    return (Fraction(double_area, 2)
            if isinstance(double_area, int)
            else double_area / 2)


def _to_endpoints_cross_product_z(start: Point, end: Point) -> Expansion:
    minuend, minuend_tail = two_product(start.x, end.y)
    subtrahend, subtrahend_tail = two_product(start.y, end.x)
    return (two_two_diff(minuend, minuend_tail, subtrahend, subtrahend_tail)
            if minuend_tail or subtrahend_tail
            else (minuend - subtrahend,))


def _vertices_orientation(vertices: Vertices) -> Orientation:
    index = min(range(len(vertices)),
                key=vertices.__getitem__)
    return to_orientation(vertices[index], vertices[index - 1],
                          vertices[(index + 1) % len(vertices)])


def _contours_vertices_equal(left: Vertices, right: Vertices) -> bool:
    if len(left) != len(right):
        return False
    right_step = (1
                  if (_vertices_orientation(left)
                      is _vertices_orientation(right))
                  else -1)
    size = len(left)
    try:
        index = right.index(left[0])
    except ValueError:
        return False
    else:
        left_index = 0
        for left_index, right_index in zip(range(size),
                                           range(index, size)
                                           if right_step == 1
                                           else range(index - 1, -1,
                                                      right_step)):
            if left[left_index] != right[right_index]:
                return False
        else:
            for left_index, right_index in zip(range(left_index + 1, size),
                                               range(index)
                                               if right_step == 1
                                               else range(size - 1, index - 1,
                                                          right_step)):
                if left[left_index] != right[right_index]:
                    return False
            else:
                return True


def _squared_distance(left: Point, right: Point) -> Coordinate:
    return (right.x - left.x) ** 2 + (right.y - left.y) ** 2
