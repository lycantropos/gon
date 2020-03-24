from typing import (Tuple,
                    Union)

from reprit.base import generate_repr
from robust.linear import (SegmentsRelationship,
                           segment_contains,
                           segments_relationship)

from gon.hints import Coordinate
from .angular import (Angle,
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
        return segments_relationship(self.as_tuple(), other.as_tuple())

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
