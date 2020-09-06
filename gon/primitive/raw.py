from gon.core.arithmetic import robust_sqrt
from gon.hints import Coordinate
from .hints import RawPoint


def raw_points_distance(left: RawPoint, right: RawPoint) -> Coordinate:
    return robust_sqrt(squared_raw_points_distance(left, right))


def scale_raw_point(point: RawPoint,
                    factor_x: Coordinate,
                    factor_y: Coordinate) -> RawPoint:
    x, y = point
    return x * factor_x, y * factor_y


def squared_raw_points_distance(left: RawPoint,
                                right: RawPoint) -> Coordinate:
    (left_x, left_y), (right_x, right_y) = left, right
    return (left_x - right_x) ** 2 + (left_y - right_y) ** 2
