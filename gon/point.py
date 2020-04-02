import math
from typing import Tuple
from weakref import WeakKeyDictionary

from memoir import cached
from reprit.base import generate_repr

from .geometry import Geometry
from .hints import Coordinate

RawPoint = Tuple[Coordinate, Coordinate]


class Point(Geometry):
    __slots__ = '_x', '_y'

    def __init__(self, x: Coordinate, y: Coordinate) -> None:
        self._x = x
        self._y = y

    __repr__ = generate_repr(__init__)

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    def __eq__(self, other: 'Point') -> bool:
        return (self._x == other._x and self._y == other._y
                if isinstance(other, Point)
                else NotImplemented)

    def __lt__(self, other: 'Point') -> bool:
        """
        Checks if the point is less than the other.
        Compares points lexicographically, ``x`` coordinates first.
        """
        return (self.raw() < other.raw()
                if isinstance(other, Point)
                else NotImplemented)

    @property
    def x(self) -> Coordinate:
        return self._x

    @property
    def y(self) -> Coordinate:
        return self._y

    @cached.map_(WeakKeyDictionary())
    def raw(self) -> RawPoint:
        return self._x, self._y

    @classmethod
    def from_raw(cls, raw: RawPoint) -> 'Point':
        x, y = raw
        return cls(x, y)

    def validate(self) -> None:
        _validate_coordinate(self._x)
        _validate_coordinate(self._y)


def _validate_coordinate(value: Coordinate) -> None:
    if not math.isfinite(value):
        raise ValueError('NaN/infinity coordinates are not supported.')
