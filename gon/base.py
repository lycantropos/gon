from enum import IntEnum

from reprit.base import generate_repr

from .hints import Scalar
from .utils import (to_sign,
                    validate_value)


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

    __repr__ = generate_repr(__init__)

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    def __eq__(self, other: 'Point') -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self._x == other._x and self._y == other._y


class Orientation(IntEnum):
    CLOCKWISE = -1
    COLLINEAR = 0
    COUNTERCLOCKWISE = 1


def to_orientation(vertex: Point,
                   first_ray_point: Point,
                   second_ray_point: Point) -> int:
    first_ray_vector = Vector.from_points(vertex, first_ray_point)
    second_ray_vector = Vector.from_points(vertex, second_ray_point)
    return to_sign(to_cross_product_z(first_ray_vector, second_ray_vector))


class Vector:
    __slots__ = ('_x', '_y')

    def __new__(cls, x: Scalar, y: Scalar) -> 'Vector':
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

    __repr__ = generate_repr(__init__)

    @classmethod
    def from_points(cls, start: Point, end: Point) -> 'Vector':
        return cls(end.x - start.x, end.y - start.y)

    @property
    def squared_length(self) -> Scalar:
        return self._x ** 2 + self._y ** 2


def to_cross_product_z(left_vector: Vector, right_vector: Vector) -> Scalar:
    """
    Z-coordinate of planar vectors cross product
    (assuming that their z-coordinates are zeros).

    Corresponds to signed area of parallelogram built on given vectors.
    """
    return left_vector.x * right_vector.y - left_vector.y * right_vector.x
