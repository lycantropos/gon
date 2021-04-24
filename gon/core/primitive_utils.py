import math
from numbers import Real

from symba.base import Expression

from .arithmetic import sqrt
from .hints import Coordinate
from .raw import RawPoint


def is_finite(value: Coordinate) -> bool:
    return (math.isfinite(value)
            if isinstance(value, Real)
            else isinstance(value, Expression) and value.is_finite)


def raw_points_distance(left: RawPoint, right: RawPoint) -> Coordinate:
    return sqrt(squared_raw_points_distance(left, right))


def scale_raw_point(point: RawPoint,
                    factor_x: Coordinate,
                    factor_y: Coordinate) -> RawPoint:
    x, y = point
    return x * factor_x, y * factor_y


def squared_raw_points_distance(left: RawPoint,
                                right: RawPoint) -> Coordinate:
    (left_x, left_y), (right_x, right_y) = left, right
    return (left_x - right_x) ** 2 + (left_y - right_y) ** 2
