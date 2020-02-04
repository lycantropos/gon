from numbers import Real
from typing import Tuple

from reprit.base import generate_repr

from .hints import Scalar
from .utils import validate_value


class Point:
    __slots__ = ('_x', '_y')

    def __new__(cls, x: Scalar, y: Scalar) -> 'Point':
        validate_value(x)
        validate_value(y)
        return super().__new__(cls)

    def __init__(self, x: Scalar, y: Scalar) -> None:
        self._x = x
        self._y = y

    @property
    def x(self) -> Scalar:
        return self._x

    @property
    def y(self) -> Scalar:
        return self._y

    def as_tuple(self) -> Tuple[Scalar, Scalar]:
        return self._x, self._y

    __repr__ = generate_repr(__init__)

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    def __eq__(self, other: 'Point') -> bool:
        return (self._x == other._x and self._y == other._y
                if isinstance(other, Point)
                else NotImplemented)


def _point_to_real_tuple(point: Point) -> Tuple[Real, Real]:
    return _scalar_to_real(point.x), _scalar_to_real(point.y)


def _scalar_to_real(scalar: Scalar) -> Real:
    return scalar if isinstance(scalar, Real) else float(scalar)
