from typing import (Tuple,
                    Union)

from reprit.base import generate_repr
from robust.linear import (SegmentsRelationship,
                           segment_contains)

from gon.hints import Coordinate
from .angular import (Angle,
                      AngleKind,
                      Orientation)
from .base import Point

SegmentsRelationship = SegmentsRelationship


class Segment:
    __slots__ = '_start', '_end'

    def __init__(self, start: Point, end: Point) -> None:
        self._start = start
        self._end = end

    @property
    def start(self) -> Point:
        return self._start

    @property
    def end(self) -> Point:
        return self._end

    @property
    def reversed(self) -> 'Segment':
        return type(self)(self.end, self.start)

    def as_tuple(self) -> Tuple[Tuple[Coordinate, Coordinate],
                                Tuple[Coordinate, Coordinate]]:
        return self._start.as_tuple(), self._end.as_tuple()

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'Segment') -> bool:
        return (self._start == other._start
                and self._end == other._end
                or self._start == other._end
                and self._end == other._start
                if isinstance(other, Segment)
                else NotImplemented)

    def __hash__(self) -> int:
        return hash(frozenset((self._start, self._end)))

    def __contains__(self, point: Point) -> bool:
        return segment_contains(self.as_tuple(), point.as_tuple())

    def relationship_with(self, other: 'Segment') -> SegmentsRelationship:
        if self == other:
            return SegmentsRelationship.OVERLAP
        self_start_orientation = other.orientation_with(self.start)
        self_end_orientation = other.orientation_with(self.end)
        if (self_start_orientation is Orientation.COLLINEAR
                and _in_segment(self.start, other)):
            if self_end_orientation is Orientation.COLLINEAR:
                if self.start == other.start:
                    if (Angle(self.end, self.start, other.end).kind
                            is AngleKind.ACUTE):
                        return SegmentsRelationship.OVERLAP
                    else:
                        return SegmentsRelationship.CROSS
                elif self.start == other.end:
                    if (Angle(self.end, self.start, other.start).kind
                            is AngleKind.ACUTE):
                        return SegmentsRelationship.OVERLAP
                    else:
                        return SegmentsRelationship.CROSS
                else:
                    return SegmentsRelationship.OVERLAP
            else:
                return SegmentsRelationship.CROSS
        elif (self_end_orientation is Orientation.COLLINEAR
              and _in_segment(self.end, other)):
            if self_start_orientation is Orientation.COLLINEAR:
                if self.end == other.start:
                    if (Angle(self.start, self.end, other.end).kind
                            is AngleKind.ACUTE):
                        return SegmentsRelationship.OVERLAP
                    else:
                        return SegmentsRelationship.CROSS
                elif self.end == other.end:
                    if (Angle(self.start, self.end, other.start).kind
                            is AngleKind.ACUTE):
                        return SegmentsRelationship.OVERLAP
                    else:
                        return SegmentsRelationship.CROSS
                else:
                    return SegmentsRelationship.OVERLAP
            else:
                return SegmentsRelationship.CROSS
        other_start_orientation = self.orientation_with(other.start)
        other_end_orientation = self.orientation_with(other.end)
        if (self_start_orientation * self_end_orientation < 0
                and other_start_orientation * other_end_orientation < 0):
            return SegmentsRelationship.CROSS
        elif (other_start_orientation is Orientation.COLLINEAR
              and _in_segment(other.start, self)):
            if other_end_orientation is Orientation.COLLINEAR:
                if other.start == self.start:
                    if (Angle(other.end, other.start, self.end).kind
                            is AngleKind.ACUTE):
                        return SegmentsRelationship.OVERLAP
                    else:
                        return SegmentsRelationship.CROSS
                elif other.start == self.end:
                    if (Angle(other.end, other.start, self.start).kind
                            is AngleKind.ACUTE):
                        return SegmentsRelationship.OVERLAP
                    else:
                        return SegmentsRelationship.CROSS
                else:
                    return SegmentsRelationship.OVERLAP
            else:
                return SegmentsRelationship.CROSS
        elif (other_end_orientation is Orientation.COLLINEAR
              and _in_segment(other.end, self)):
            if other_start_orientation is Orientation.COLLINEAR:
                if other.end == self.start:
                    if (Angle(other.start, other.end, self.end).kind
                            is AngleKind.ACUTE):
                        return SegmentsRelationship.OVERLAP
                    else:
                        return SegmentsRelationship.CROSS
                elif other.end == self.end:
                    if (Angle(other.start, other.end, self.start).kind
                            is AngleKind.ACUTE):
                        return SegmentsRelationship.OVERLAP
                    else:
                        return SegmentsRelationship.CROSS
                else:
                    return SegmentsRelationship.OVERLAP
            else:
                return SegmentsRelationship.CROSS
        else:
            return SegmentsRelationship.NONE

    def orientation_with(self, point: Point) -> Orientation:
        return self.angle_with(point).orientation

    def angle_with(self, point: Point) -> Angle:
        return Angle(self.end, self.start, point)


def to_segment(start: Point, end: Point) -> Union[Segment, Segment]:
    if start == end:
        raise ValueError('Degenerate segment found.')
    return Segment(start, end)


def _in_segment(point: Point, segment: Segment) -> bool:
    if point == segment.start:
        return True
    elif point == segment.end:
        return True
    else:
        left_x, right_x = ((segment.start.x, segment.end.x)
                           if segment.start.x < segment.end.x
                           else (segment.end.x, segment.start.x))
        bottom_y, top_y = ((segment.start.y, segment.end.y)
                           if segment.start.y < segment.end.y
                           else (segment.end.y, segment.start.y))
        return left_x <= point.x <= right_x and bottom_y <= point.y <= top_y
