from typing import Tuple

from reprit.base import generate_repr

from .hints import Coordinate
from .utils import validate_value


class Point:
    __slots__ = ('_x', '_y')

    def __new__(cls, x: Coordinate, y: Coordinate) -> 'Point':
        validate_value(x)
        validate_value(y)
        return super().__new__(cls)

    def __init__(self, x: Coordinate, y: Coordinate) -> None:
        self._x = x
        self._y = y

    @property
    def x(self) -> Coordinate:
        return self._x

    @property
    def y(self) -> Coordinate:
        return self._y

    def as_tuple(self) -> Tuple[Coordinate, Coordinate]:
        return self._x, self._y

    __repr__ = generate_repr(__init__)

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    def __eq__(self, other: 'Point') -> bool:
        return (self._x == other._x and self._y == other._y
                if isinstance(other, Point)
                else NotImplemented)
