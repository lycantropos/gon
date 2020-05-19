from typing import (List,
                    Set)

from reprit.base import generate_repr

from .compound import (Compound,
                       Relation)
from .geometry import Geometry
from .hints import Domain
from .primitive import (Point,
                        RawPoint)

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

    def __contains__(self, other: Geometry) -> bool:
        """
        Checks if the multipoint contains the other geometry.

        Time complexity:
            ``O(1)`` expected,
            ``O(len(self.points))`` worst.
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
        return ((self._points_set >= other._points_set
                 if isinstance(other, Multipoint)
                 # multipoint cannot be superset of continuous geometry
                 else False)
                if isinstance(other, Compound)
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
        return ((self._points_set > other._points_set
                 if isinstance(other, Multipoint)
                 # multipoint cannot be strict superset of continuous geometry
                 else False)
                if isinstance(other, Compound)
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
        return ((self._points_set <= other._points_set
                 if isinstance(other, Multipoint)
                 else other >= self)
                if isinstance(other, Compound)
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
        return ((self._points_set < other._points_set
                 if isinstance(other, Multipoint)
                 else other > self)
                if isinstance(other, Compound)
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
    def points(self) -> List[Point]:
        """
        Returns points of the multipoint.

        Time complexity:
            ``O(len(self.points))``
        Memory complexity:
            ``O(len(self.points))``

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> multipoint.points
        [Point(0, 0), Point(1, 0), Point(0, 1)]
        """
        return list(self._points)

    def raw(self) -> RawMultipoint:
        return self._raw[:]

    def relate(self, other: Compound) -> Relation:
        return ((Relation.EQUAL
                 if self is other
                 else _relate_sets(self._points_set, other._points_set))
                if isinstance(other, Multipoint)
                else other.relate(self).complement)

    def validate(self) -> None:
        if not self._points:
            raise ValueError('Multipoint is empty.')
        elif len(self._points) > len(self._points_set):
            raise ValueError('Duplicate points found.')


def _relate_sets(left: Set[Domain], right: Set[Domain]) -> Relation:
    if left == right:
        return Relation.EQUAL
    intersection = left & right
    if not intersection:
        return Relation.DISJOINT
    elif intersection == right:
        return Relation.COMPONENT
    elif intersection == left:
        return Relation.COMPOSITE
    else:
        return Relation.OVERLAP
