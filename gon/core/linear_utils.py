from typing import Sequence

from ground.base import Context
from ground.hints import (Coordinate,
                          Multipoint,
                          Multisegment,
                          Point,
                          Segment)

from .compound import (Compound,
                       Relation)
from .empty import EMPTY


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


def from_mix_components(multipoint: Multipoint,
                        multisegment: Multisegment) -> Compound:
    # importing here to avoid cyclic imports
    from .mix import from_mix_components
    return from_mix_components(unpack_multipoint(multipoint),
                               unpack_multisegment(multisegment), EMPTY)


def unpack_multipoint(multipoint: Multipoint) -> Compound:
    return multipoint if multipoint.points else EMPTY


def unpack_multisegment(multisegment: Multisegment) -> Compound:
    return ((multisegment
             if len(multisegment.segments) > 1
             else multisegment.segments[0])
            if multisegment.segments
            else EMPTY)


def to_point_nearest_segment(context: Context,
                             segments: Sequence[Segment],
                             point: Point) -> Segment:
    def distance_to_point(segment: Segment) -> Coordinate:
        return context.segment_point_squared_distance(segment.start,
                                                      segment.end, point)

    return min(segments,
               key=distance_to_point)


def to_segment_nearest_segment(context: Context,
                               edges: Sequence[Segment],
                               segment: Segment) -> Segment:
    def distance_to_segment(candidate: Segment) -> Coordinate:
        return context.segments_squared_distance(
                candidate.start, candidate.end, segment.start, segment.end)

    return min(edges,
               key=distance_to_segment)
