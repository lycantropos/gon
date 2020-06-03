from reprit.base import generate_repr

from .compound import (Compound,
                       Location,
                       Relation)
from .geometry import Geometry
from .hints import Domain
from .primitive import Point

RawEmpty = type(None)


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
        return (self is other
                if isinstance(other, Geometry)
                else NotImplemented)

    def __ge__(self, other: Compound) -> bool:
        return (self is other
                if isinstance(other, Compound)
                else NotImplemented)

    def __gt__(self, other: Compound) -> bool:
        return (False
                if isinstance(other, Compound)
                else NotImplemented)

    def __hash__(self) -> int:
        return 0

    def __le__(self, other: Compound) -> bool:
        return (True
                if isinstance(other, Compound)
                else NotImplemented)

    def __lt__(self, other: Compound) -> bool:
        return (self is not other
                if isinstance(other, Compound)
                else NotImplemented)

    def locate(self, point: Point) -> Location:
        return Location.EXTERIOR

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
