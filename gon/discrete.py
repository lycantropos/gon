import sys
from fractions import Fraction
from typing import (AbstractSet,
                    Iterable,
                    List,
                    Optional,
                    Set)

from reprit.base import generate_repr

from .compound import (Compound,
                       Location,
                       Relation)
from .degenerate import EMPTY
from .geometry import Geometry
from .hints import (Coordinate,
                    Domain)
from .primitive import (Point,
                        RawPoint,
                        _point_to_step,
                        _rotate_point_around_origin,
                        _rotate_translate_point,
                        _scale_point)

RawMultipoint = List[RawPoint]


class Multipoint(Compound):
    __slots__ = '_points', '_points_set', '_raw'

    def __init__(self, *points: Point) -> None:
        """
        Initializes multipoint.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(points)``.
        """
        self._points = points
        self._points_set = frozenset(points)
        self._raw = [point.raw() for point in points]

    __repr__ = generate_repr(__init__)

    def __and__(self, other: Compound) -> Compound:
        """
        Returns intersection of the multipoint with the other geometry.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> multipoint & multipoint == multipoint
        True
        """
        return (from_points(self._points_set & other._points_set
                            if isinstance(other, Multipoint)
                            else [point
                                  for point in self._points
                                  if point in other])
                if isinstance(other, Compound)
                else NotImplemented)

    __rand__ = __and__

    def __contains__(self, other: Geometry) -> bool:
        """
        Checks if the multipoint contains the other geometry.

        Time complexity:
            ``O(1)`` expected,
            ``O(len(self.points))`` worst
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> all(point in multipoint for point in multipoint.points)
        True
        """
        return isinstance(other, Point) and other in self._points_set

    def __eq__(self, other: 'Multipoint') -> bool:
        """
        Checks if multipoints are equal.

        Time complexity:
            ``O(min(len(self.points), len(other.points)))``
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> multipoint == multipoint
        True
        >>> multipoint == Multipoint.from_raw([(0, 0), (1, 0), (1, 1), (0, 1)])
        False
        >>> multipoint == Multipoint.from_raw([(1, 0), (0, 0), (0, 1)])
        True
        """
        return self is other or (self._points_set == other._points_set
                                 if isinstance(other, Multipoint)
                                 else (False
                                       if isinstance(other, Geometry)
                                       else NotImplemented))

    def __ge__(self, other: Compound) -> bool:
        """
        Checks if the multipoint is a superset of the other geometry.

        Time complexity:
            ``O(len(self.points))``
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> multipoint >= multipoint
        True
        >>> multipoint >= Multipoint.from_raw([(0, 0), (1, 0), (1, 1), (0, 1)])
        False
        >>> multipoint >= Multipoint.from_raw([(1, 0), (0, 0), (0, 1)])
        True
        """
        return (self._points_set >= other._points_set
                if isinstance(other, Multipoint)
                else NotImplemented)

    def __gt__(self, other: Compound) -> bool:
        """
        Checks if the multipoint is a strict superset of the other geometry.

        Time complexity:
            ``O(len(self.points))``
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> multipoint > multipoint
        False
        >>> multipoint > Multipoint.from_raw([(0, 0), (1, 0), (1, 1), (0, 1)])
        False
        >>> multipoint > Multipoint.from_raw([(1, 0), (0, 0), (0, 1)])
        False
        """
        return (self._points_set > other._points_set
                if isinstance(other, Multipoint)
                else NotImplemented)

    def __hash__(self) -> int:
        """
        Returns hash value of the multipoint.

        Time complexity:
            ``O(len(self.points))``
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> hash(multipoint) == hash(multipoint)
        True
        """
        return hash(self._points_set)

    def __le__(self, other: Compound) -> bool:
        """
        Checks if the multipoint is a subset of the other geometry.

        Time complexity:
            ``O(len(self.points))``
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> multipoint <= multipoint
        True
        >>> multipoint <= Multipoint.from_raw([(0, 0), (1, 0), (1, 1), (0, 1)])
        True
        >>> multipoint <= Multipoint.from_raw([(1, 0), (0, 0), (0, 1)])
        True
        """
        return (self._points_set <= other._points_set
                if isinstance(other, Multipoint)
                else NotImplemented)

    def __lt__(self, other: Compound) -> bool:
        """
        Checks if the multipoint is a strict subset of the other geometry.

        Time complexity:
            ``O(len(self.points))``
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> multipoint < multipoint
        False
        >>> multipoint < Multipoint.from_raw([(0, 0), (1, 0), (1, 1), (0, 1)])
        True
        >>> multipoint < Multipoint.from_raw([(1, 0), (0, 0), (0, 1)])
        False
        """
        return (self._points_set < other._points_set
                if isinstance(other, Multipoint)
                else NotImplemented)

    def __or__(self, other: Compound) -> Compound:
        """
        Returns union of the multipoint with the other geometry.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> multipoint | multipoint == multipoint
        True
        """
        return (Multipoint(*(self._points_set | other._points_set))
                if isinstance(other, Multipoint)
                else NotImplemented)

    def __sub__(self, other: Compound) -> Compound:
        """
        Returns difference of the multipoint with the other geometry.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> multipoint - multipoint is EMPTY
        True
        """
        return (from_points(self._points_set - other._points_set
                            if isinstance(other, Multipoint)
                            else [point
                                  for point in self._points
                                  if point not in other])
                if isinstance(other, Compound)
                else NotImplemented)

    def __xor__(self, other: Compound) -> Compound:
        """
        Returns symmetric difference of the multipoint with the other geometry.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> multipoint ^ multipoint is EMPTY
        True
        """
        return (from_points(self._points_set ^ other._points_set)
                if isinstance(other, Multipoint)
                else NotImplemented)

    @classmethod
    def from_raw(cls, raw: RawMultipoint) -> Domain:
        """
        Constructs multipoint from the combination of Python built-ins.

        Time complexity:
            ``O(len(raw))``
        Memory complexity:
            ``O(len(raw))``

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> multipoint == Multipoint(Point(0, 0), Point(1, 0), Point(0, 1))
        True
        """
        return cls(*map(Point.from_raw, raw))

    @property
    def centroid(self) -> Point:
        """
        Returns centroid of the multipoint.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint.from_raw([(0, 0), (3, 0), (0, 3)])
        >>> multipoint.centroid == Point(1, 1)
        True
        """
        accumulated_x = accumulated_y = 0
        for x, y in self._raw:
            accumulated_x += x
            accumulated_y += y
        divisor = len(self._raw)
        return Point(_robust_divide(accumulated_x, divisor),
                     _robust_divide(accumulated_y, divisor))

    @property
    def points(self) -> List[Point]:
        """
        Returns points of the multipoint.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> multipoint.points
        [Point(0, 0), Point(1, 0), Point(0, 1)]
        """
        return list(self._points)

    def locate(self, point: Point) -> Location:
        """
        Finds location of the point relative to the multipoint.

        Time complexity:
            ``O(1)`` expected,
            ``O(len(self.points))`` worst
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> all(multipoint.locate(point) is Location.BOUNDARY
        ...     for point in multipoint.points)
        True
        """
        return (Location.BOUNDARY
                if point in self._points_set
                else Location.EXTERIOR)

    def raw(self) -> RawMultipoint:
        """
        Returns the multipoint as combination of Python built-ins.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> multipoint.raw()
        [(0, 0), (1, 0), (0, 1)]
        """
        return self._raw[:]

    def relate(self, other: Compound) -> Relation:
        """
        Finds relation between the multipoint and the other geometry.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> multipoint.relate(multipoint) is Relation.EQUAL
        True
        """
        return ((Relation.EQUAL
                 if self is other
                 else _relate_sets(self._points_set, other._points_set))
                if isinstance(other, Multipoint)
                else self._relate_geometry(other))

    def rotate(self,
               cosine: Coordinate,
               sine: Coordinate,
               point: Optional[Point] = None) -> 'Multipoint':
        """
        Rotates geometric object by given cosine & sine around given point.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> multipoint.rotate(1, 0) == multipoint
        True
        >>> (multipoint.rotate(0, 1, Point(1, 1))
        ...  == Multipoint.from_raw([(2, 0), (2, 1), (1, 0)]))
        True
        """
        return (Multipoint(*_rotate_points_around_origin(self._points, cosine,
                                                         sine))
                if point is None
                else
                Multipoint(*_rotate_translate_points(
                        self._points, cosine, sine,
                        *_point_to_step(point, cosine, sine))))

    def scale(self,
              factor_x: Coordinate,
              factor_y: Optional[Coordinate] = None) -> 'Multipoint':
        """
        Scales the multipoint by given factor.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> multipoint.scale(1) == multipoint
        True
        >>> (multipoint.scale(1, 2)
        ...  == Multipoint.from_raw([(0, 0), (1, 0), (0, 2)]))
        True
        """
        if factor_y is None:
            factor_y = factor_x
        return (Multipoint(*[_scale_point(point, factor_x, factor_y)
                             for point in self._points])
                if factor_x and factor_y
                else (Multipoint(*_unique_ever_seen(_scale_point(point,
                                                                 factor_x,
                                                                 factor_y)
                                                    for point in self._points))
                      if factor_x or factor_y
                      else Multipoint(Point(factor_x, factor_y))))

    def translate(self,
                  step_x: Coordinate,
                  step_y: Coordinate) -> 'Multipoint':
        """
        Translates the multipoint by given step.

        Time complexity:
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> (multipoint.translate(1, 2)
        ...  == Multipoint.from_raw([(1, 2), (2, 2), (1, 3)]))
        True
        """
        return Multipoint(*[point.translate(step_x, step_y)
                            for point in self._points])

    def validate(self) -> None:
        """
        Checks if the multipoint is valid.

        Time complexity:
            ``O(len(self.points))``
        Memory complexity:
            ``O(1)``

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> multipoint.validate()
        """
        if not self._points:
            raise ValueError('Multipoint is empty.')
        elif len(self._points) > len(self._points_set):
            raise ValueError('Duplicate points found.')
        for point in self._points:
            point.validate()

    def _relate_geometry(self, other: Compound) -> Relation:
        disjoint = is_subset = not_interior = not_boundary = True
        for point in self._points:
            location = other.locate(point)
            if location is Location.INTERIOR:
                if disjoint:
                    disjoint = False
                if not_interior:
                    not_interior = False
            elif location is Location.BOUNDARY:
                if disjoint:
                    disjoint = False
                if not_boundary:
                    not_boundary = True
            elif is_subset:
                is_subset = False
        return (Relation.DISJOINT
                if disjoint
                else ((Relation.COMPOSITE
                       if is_subset
                       else Relation.TOUCH)
                      if not_interior
                      else ((Relation.COVER
                             if not_boundary
                             else Relation.ENCLOSES)
                            if is_subset
                            else Relation.CROSS)))


def from_points(points: AbstractSet[Point]) -> Compound:
    return Multipoint(*points) if points else EMPTY


def _rotate_points_around_origin(points: Iterable[Point],
                                 cosine: Coordinate,
                                 sine: Coordinate) -> List[Point]:
    return [_rotate_point_around_origin(point, cosine, sine)
            for point in points]


def _rotate_translate_points(points: Iterable[Point],
                             cosine: Coordinate,
                             sine: Coordinate,
                             step_x: Coordinate,
                             step_y: Coordinate) -> List[Point]:
    return [_rotate_translate_point(point, cosine, sine, step_x, step_y)
            for point in points]


def _relate_sets(left: Set[Domain], right: Set[Domain]) -> Relation:
    if left == right:
        return Relation.EQUAL
    intersection = left & right
    return ((Relation.COMPONENT
             if intersection == right
             else (Relation.COMPOSITE
                   if intersection == left
                   else Relation.OVERLAP))
            if intersection
            else Relation.DISJOINT)


def _robust_divide(dividend: Coordinate, divisor: int) -> Coordinate:
    return (Fraction(dividend, divisor)
            if isinstance(dividend, int)
            else dividend / divisor)


if sys.version_info < (3, 6):
    from collections import OrderedDict
else:
    OrderedDict = dict
_unique_ever_seen = OrderedDict.fromkeys
del OrderedDict, sys
