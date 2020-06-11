from typing import Union

from reprit.base import generate_repr

from .compound import (Compound,
                       Location,
                       Relation)
from .geometry import Geometry
from .hints import Domain
from .primitive import Point

RAW_EMPTY = None
RawEmpty = type(RAW_EMPTY)


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
        """
        Checks if the empty geometry contains the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY in EMPTY
        False
        """
        return False

    def __eq__(self, other: 'Empty') -> bool:
        """
        Checks if empty geometries are equal.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY == EMPTY
        True
        """
        return (self is other
                if isinstance(other, Geometry)
                else NotImplemented)

    def __ge__(self, other: Compound) -> bool:
        """
        Checks if the empty geometry is a superset of the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY >= EMPTY
        True
        """
        return (self is other
                if isinstance(other, Compound)
                else NotImplemented)

    def __gt__(self, other: Compound) -> bool:
        """
        Checks if the empty geometry is a strict superset
        of the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY > EMPTY
        False
        """
        return (False
                if isinstance(other, Compound)
                else NotImplemented)

    def __hash__(self) -> int:
        """
        Returns hash value of the empty geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> hash(EMPTY) == hash(EMPTY)
        True
        """
        return 0

    def __le__(self, other: Compound) -> bool:
        """
        Checks if the empty geometry is a subset of the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY <= EMPTY
        True
        """
        return (True
                if isinstance(other, Compound)
                else NotImplemented)

    def __lt__(self, other: Compound) -> bool:
        """
        Checks if the empty geometry is a strict subset of the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY < EMPTY
        False
        """
        return (self is not other
                if isinstance(other, Compound)
                else NotImplemented)

    @classmethod
    def from_raw(cls, raw: RawEmpty) -> Domain:
        """
        Constructs empty geometry from the combination of Python built-ins.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> Empty.from_raw(RAW_EMPTY) is EMPTY
        True
        """
        assert raw is RAW_EMPTY
        return cls()

    def locate(self, point: Point) -> Location:
        """
        Finds location of the point relative to the empty geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY.locate(Point(0, 0)) is Location.EXTERIOR
        True
        """
        return Location.EXTERIOR

    def raw(self) -> RawEmpty:
        """
        Returns the empty geometry as combination of Python built-ins.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY.raw()
        """
        return RAW_EMPTY

    def relate(self, other: Compound) -> Relation:
        """
        Finds relation between the empty geometry and the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY.relate(EMPTY) is Relation.DISJOINT
        True
        """
        return Relation.DISJOINT

    def validate(self) -> None:
        """
        Checks if the empty geometry is valid.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        """
        # empty geometry considered to be always valid


Maybe = Union[Empty, Domain]
EMPTY = Empty()
