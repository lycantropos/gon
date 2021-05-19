from typing import (AbstractSet,
                    Sequence,
                    Type,
                    Union)

from ground.base import Context
from ground.hints import (Empty,
                          Maybe,
                          Multipoint,
                          Multisegment,
                          Point,
                          Segment)

from .compound import (Compound,
                       Relation)
from .hints import Scalar


def pack_points(points: AbstractSet[Point],
                empty: Empty,
                multipoint_cls: Type[Multipoint]) -> Maybe[Multipoint]:
    return multipoint_cls(list(points)) if points else empty


def pack_segments(segments: Sequence[Point],
                  empty: Empty,
                  multisegment_cls: Type[Multisegment]
                  ) -> Union[Empty, Multisegment, Segment]:
    return ((multisegment_cls(segments)
             if len(segments) > 1
             else segments[0])
            if segments
            else empty)


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
                               edges: Sequence[Segment],
                               segment: Segment) -> Segment:
    def distance_to_segment(candidate: Segment) -> Scalar:
        return context.segments_squared_distance(candidate, segment)

    return min(edges,
               key=distance_to_segment)
