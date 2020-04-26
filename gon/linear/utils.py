from fractions import Fraction

from robust import projection

from gon.hints import Coordinate
from gon.primitive import (Point,
                           RawPoint)


def squared_points_distance(left: Point, right: Point) -> Coordinate:
    return squared_raw_points_distance(left.raw(), right.raw())


def squared_raw_segment_point_distance(start: RawPoint, end: RawPoint,
                                       point: RawPoint) -> Coordinate:
    numerator = projection.signed_length(start, end, start, point)
    if numerator <= 0:
        return squared_raw_points_distance(start, point)
    else:
        denominator = squared_raw_points_distance(start, end)
        if numerator >= denominator:
            return squared_raw_points_distance(end, point)
        else:
            (start_x, start_y), (end_x, end_y) = start, end
            coefficient = (Fraction(numerator, denominator)
                           if isinstance(denominator, int)
                           else numerator / denominator)
            point_projection = (start_x + coefficient * (end_x - start_x),
                                start_y + coefficient * (end_y - start_y))
            return squared_raw_points_distance(point_projection, point)


def squared_raw_points_distance(left: RawPoint, right: RawPoint) -> Coordinate:
    (left_x, left_y), (right_x, right_y) = left, right
    return (left_x - right_x) ** 2 + (left_y - right_y) ** 2
