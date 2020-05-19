from typing import (List,
                    Set)

from reprit.base import generate_repr

from .compound import (Compound,
                       Relation)
from .geometry import Geometry
from .hints import Domain
from .primitive import (Point,
                        RawPoint)

RawEmpty = type(None)
RawMultipoint = List[RawPoint]


class Empty(Compound):
    __slots__ = ()

    _instance = None

    def __new__(cls) -> 'Empty':
        """
        Returns empty geometry instance.

        Based on singleton pattern.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        Reference:
            https://en.wikipedia.org/wiki/Singleton_pattern
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    __repr__ = generate_repr(__new__)

    def __contains__(self, other: Geometry) -> bool:
        return False

    def __eq__(self, other: Geometry) -> bool:
        return self is other

    def __ge__(self, other: Compound) -> bool:
        return self is other

    def __gt__(self, other: Compound) -> bool:
        return False

    def __hash__(self) -> int:
        return 0

    def __le__(self, other: Compound) -> bool:
        return True

    def __lt__(self, other: Compound) -> bool:
        return self is not other

    def relate(self, other: Compound) -> Relation:
        return Relation.DISJOINT

    @classmethod
    def from_raw(cls, raw: RawEmpty) -> Domain:
        assert raw is None
        return cls()

    def raw(self) -> RawEmpty:
        return None

    def validate(self) -> None:
        """
        Checks if the empty geometry is valid.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        """
        # empty geometry considered to be always valid


EMPTY = Empty()


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
        return (other is EMPTY
                or ((self._points_set >= other._points_set
                     if isinstance(other, Multipoint)
                     # multipoint cannot be superset of continuous geometry
                     else False)
                    if isinstance(other, Compound)
                    else NotImplemented))

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
        return (other is EMPTY
                or ((self._points_set > other._points_set
                     if isinstance(other, Multipoint)
                     # multipoint cannot be strict superset
                     # of continuous geometry
                     else False)
                    if isinstance(other, Compound)
                    else NotImplemented))

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
            ``O(points_count)``
        Memory complexity:
            ``O(points_count)``

        where ``points_count = len(self.points)``.

        >>> multipoint = Multipoint.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> multipoint.points
        [Point(0, 0), Point(1, 0), Point(0, 1)]
        """
        return list(self._points)

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
                else other.relate(self).complement)

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
