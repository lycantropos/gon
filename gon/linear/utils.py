from gon.hints import Coordinate
from gon.primitive import (Point,
                           RawPoint)


def squared_points_distance(left: Point, right: Point) -> Coordinate:
    return squared_raw_points_distance(left.raw(), right.raw())


def squared_raw_points_distance(left: RawPoint, right: RawPoint) -> Coordinate:
    (left_x, left_y), (right_x, right_y) = left, right
    return (left_x - right_x) ** 2 + (left_y - right_y) ** 2
