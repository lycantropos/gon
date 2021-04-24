from locus.hints import Interval
from robust import projection
from robust.linear import (SegmentsRelationship,
                           segments_relationship)
from symba.base import Expression

from gon.core.compound import (Compound,
                               Relation)
from .arithmetic import (robust_divide,
                         sqrt)
from .degenerate import EMPTY
from .hints import Coordinate
from .multipoint import Multipoint
from .primitive_utils import squared_raw_points_distance
from .raw import (RawMultipoint,
                  RawMultisegment,
                  RawPoint,
                  RawSegment)


def raw_segment_point_distance(raw_segment: RawSegment,
                               raw_point: RawPoint) -> Expression:
    return sqrt(squared_raw_point_segment_distance(raw_point,
                                                   raw_segment))


def raw_segments_distance(left: RawSegment, right: RawSegment) -> Expression:
    return sqrt(squared_raw_segments_distance(left, right))


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


def relate_multipoint_to_linear_compound(multipoint: Multipoint,
                                         compound: Compound) -> Relation:
    disjoint = is_subset = True
    for point in multipoint.points:
        if point in compound:
            if disjoint:
                disjoint = False
        elif is_subset:
            is_subset = False
    return (Relation.DISJOINT
            if disjoint
            else (Relation.COMPONENT
                  if is_subset
                  else Relation.TOUCH))


def from_raw_mix_components(raw_multipoint: RawMultipoint,
                            raw_multisegment: RawMultisegment) -> Compound:
    # importing here to avoid cyclic imports
    from gon.core.mix import from_mix_components
    return from_mix_components(from_raw_multipoint(raw_multipoint),
                               from_raw_multisegment(raw_multisegment),
                               EMPTY)


def from_raw_multipoint(raw_multipoint: RawMultipoint) -> Multipoint:
    return (Multipoint.from_raw(raw_multipoint)
            if raw_multipoint
            else EMPTY)


def from_raw_multisegment(raw: RawMultisegment) -> Compound:
    # importing here to avoid cyclic imports
    from .segment import Segment
    from .multisegment import Multisegment
    return ((Segment.from_raw(raw[0])
             if len(raw) == 1
             else Multisegment.from_raw(raw))
            if raw
            else EMPTY)
