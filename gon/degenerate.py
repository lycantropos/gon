from reprit.base import generate_repr

from .compound import (Compound,
                       Relation)
from .geometry import Geometry
from .hints import Domain

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
