from typing import Sequence

from ground.base import Context
from ground.hints import (Multipoint,
                          Point,
                          Scalar,
                          Segment)

from .compound import (Compound,
                       Relation)


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


def to_point_nearest_segment(context: Context,
                             segments: Sequence[Segment],
                             point: Point) -> Segment:
    def distance_to_point(segment: Segment) -> Scalar:
        return context.segment_point_squared_distance(segment, point)

    return min(segments,
               key=distance_to_point)


def to_segment_nearest_segment(context: Context,
                               segments: Sequence[Segment],
                               segment: Segment) -> Segment:
    def distance_to_segment(candidate: Segment) -> Scalar:
        return context.segments_squared_distance(candidate, segment)

    return min(segments,
               key=distance_to_segment)
