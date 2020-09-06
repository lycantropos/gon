from locus.hints import Interval
from robust import projection
from robust.linear import (SegmentsRelationship,
                           segments_relationship)

from gon.core.arithmetic import (robust_divide,
                                 robust_sqrt)
from gon.hints import Coordinate
from gon.primitive import RawPoint
from gon.primitive.raw import squared_raw_points_distance
from .hints import RawSegment


def raw_segment_point_distance(raw_segment: RawSegment,
                               raw_point: RawPoint) -> Coordinate:
    return robust_sqrt(squared_raw_point_segment_distance(raw_point,
                                                          raw_segment))


def raw_segments_distance(left: RawSegment, right: RawSegment) -> Coordinate:
    return robust_sqrt(squared_raw_segments_distance(left, right))


def squared_raw_interval_point_distance(interval: Interval,
                                        raw_point: RawPoint) -> Coordinate:
    x, y = raw_point
    (min_x, max_x), (min_y, max_y) = interval
    return (_distance_to_linear_interval(x, min_x, max_x) ** 2
            + _distance_to_linear_interval(y, min_y, max_y) ** 2)


def squared_raw_point_segment_distance(raw_point: RawPoint,
                                       raw_segment: RawSegment) -> Coordinate:
    raw_start, raw_end = raw_segment
    factor = max(0, min(1, robust_divide(projection.signed_length(
            raw_start, raw_point, raw_start, raw_end),
            squared_raw_points_distance(raw_end, raw_start))))
    start_x, start_y = raw_start
    end_x, end_y = raw_end
    return squared_raw_points_distance((start_x + factor * (end_x - start_x),
                                        start_y + factor * (end_y - start_y)),
                                       raw_point)


def squared_raw_segment_interval_distance(segment: RawSegment,
                                          interval: Interval) -> Coordinate:
    (start_x, start_y), (end_x, end_y) = segment
    (min_x, max_x), (min_y, max_y) = interval
    if (min_x <= start_x <= max_x and min_y <= start_y <= max_y
            or min_x <= end_x <= max_x and min_y <= end_y <= max_y):
        return 0
    return (squared_raw_segments_distance(((min_x, min_y), (min_x, max_y)),
                                          segment)
            if min_x == max_x
            else
            (squared_raw_segments_distance(((min_x, min_y), (max_x, min_y)),
                                           segment)
             if min_y == max_y
             else _squared_raw_segment_non_degenerate_interval_distance(
                    segment, max_x, max_y, min_x, min_y)))


def squared_raw_segments_distance(left: RawSegment,
                                  right: RawSegment) -> Coordinate:
    left_start, left_end = left
    right_start, right_end = right
    return (min(squared_raw_point_segment_distance(right_start, left),
                squared_raw_point_segment_distance(right_end, left),
                squared_raw_point_segment_distance(left_start, right),
                squared_raw_point_segment_distance(left_end, right))
            if (segments_relationship(left, right)
                is SegmentsRelationship.NONE)
            else 0)


def _distance_to_linear_interval(coordinate: Coordinate,
                                 min_coordinate: Coordinate,
                                 max_coordinate: Coordinate) -> Coordinate:
    return (min_coordinate - coordinate
            if coordinate < min_coordinate
            else (coordinate - max_coordinate
                  if coordinate > max_coordinate
                  else 0))


def _squared_raw_segment_non_degenerate_interval_distance(segment: RawSegment,
                                                          max_x: Coordinate,
                                                          max_y: Coordinate,
                                                          min_x: Coordinate,
                                                          min_y: Coordinate
                                                          ) -> Coordinate:
    bottom_left = min_x, min_y
    bottom_right = max_x, min_y
    bottom_side_distance = squared_raw_segments_distance(
            segment, (bottom_left, bottom_right))
    if not bottom_side_distance:
        return bottom_side_distance
    top_right = max_x, max_y
    right_side_distance = squared_raw_segments_distance(
            segment, (bottom_right, top_right))
    if not right_side_distance:
        return right_side_distance
    top_left = min_x, max_y
    top_side_distance = squared_raw_segments_distance(segment,
                                                      (top_left, top_right))
    if not top_side_distance:
        return top_side_distance
    left_side_distance = squared_raw_segments_distance(segment,
                                                       (bottom_left, top_left))
    return (left_side_distance
            and min(bottom_side_distance, right_side_distance,
                    top_side_distance, left_side_distance))
