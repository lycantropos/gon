from enum import (IntEnum,
                  unique)
from functools import partial
from typing import Union

from reprit.base import generate_repr

from .angular import (Angle,
                      Orientation)
from .base import Point


@unique
class IntersectionKind(IntEnum):
    NONE = 0
    CROSS = 1
    OVERLAP = 2


class Interval:
    __slots__ = ('_start', '_end', '_start_inclusive', '_end_inclusive')

    def __init__(self,
                 start: Point,
                 end: Point,
                 *,
                 start_inclusive: bool,
                 end_inclusive: bool) -> None:
        self._start = start
        self._end = end
        self._start_inclusive = start_inclusive
        self._end_inclusive = end_inclusive

    @property
    def start(self) -> Point:
        return self._start

    @property
    def end(self) -> Point:
        return self._end

    @property
    def start_inclusive(self) -> bool:
        return self._start_inclusive

    @property
    def end_inclusive(self) -> bool:
        return self._end_inclusive

    @property
    def reversed(self) -> 'Interval':
        return type(self)(self.end, self.start,
                          start_inclusive=self.end_inclusive,
                          end_inclusive=self.start_inclusive)

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'Interval') -> bool:
        if not isinstance(other, Interval):
            return NotImplemented
        return (self._start_inclusive is other._start_inclusive
                and self._end_inclusive is other._end_inclusive
                and self._start == other._start
                and self._end == other._end
                or self._start_inclusive is other._end_inclusive
                and self._end_inclusive is other._start_inclusive
                and self._start == other._end
                and self._end == other._start)

    def __hash__(self) -> int:
        return hash(frozenset([(self._start, self._start_inclusive),
                               (self._end, self._end_inclusive)]))

    def __contains__(self, point: Point) -> bool:
        return (self.orientation_with(point) is Orientation.COLLINEAR
                and _in_interval(point, self))

    def intersects_with(self, other: 'Interval') -> bool:
        return self.relationship_with(other) is not IntersectionKind.NONE

    def relationship_with(self, other: 'Interval') -> IntersectionKind:
        if self == other:
            return IntersectionKind.OVERLAP
        self_start_orientation = other.orientation_with(self.start)
        if (self.start_inclusive
                and self_start_orientation is Orientation.COLLINEAR
                and _in_interval(self.start, other)):
            return IntersectionKind.OVERLAP
        self_end_orientation = other.orientation_with(self.end)
        if (self.end_inclusive
                and self_end_orientation is Orientation.COLLINEAR
                and _in_interval(self.end, other)):
            return IntersectionKind.OVERLAP
        other_start_orientation = self.orientation_with(other.start)
        if (other.start_inclusive
                and other_start_orientation is Orientation.COLLINEAR
                and _in_interval(other.start, self)):
            return IntersectionKind.OVERLAP
        other_end_orientation = self.orientation_with(other.end)
        if (self_start_orientation * self_end_orientation < 0
                and other_start_orientation * other_end_orientation < 0):
            return IntersectionKind.CROSS
        if (other.end_inclusive
                and other_end_orientation is Orientation.COLLINEAR
                and _in_interval(other.end, self)):
            return IntersectionKind.OVERLAP
        return IntersectionKind.NONE

    def orientation_with(self, point: Point) -> Orientation:
        return self.angle_with(point).orientation

    def angle_with(self, point: Point) -> Angle:
        return Angle(self.end, self.start, point)


class Segment(Interval):
    def __init__(self, start: Point, end: Point) -> None:
        super().__init__(start, end,
                         start_inclusive=True,
                         end_inclusive=True)

    @property
    def reversed(self) -> 'Segment':
        return type(self)(self.end, self.start)

    __repr__ = generate_repr(__init__)


def to_interval(start: Point, end: Point,
                *,
                start_inclusive: bool,
                end_inclusive: bool) -> Union[Interval, Segment]:
    if start == end:
        raise ValueError('Degenerate interval found.')
    if start_inclusive and end_inclusive:
        return Segment(start, end)
    return Interval(start, end,
                    start_inclusive=start_inclusive,
                    end_inclusive=end_inclusive)


to_segment = partial(to_interval,
                     start_inclusive=True,
                     end_inclusive=True)


def _in_interval(point: Point, interval: Interval) -> bool:
    if point == interval.start:
        return interval.start_inclusive
    elif point == interval.end:
        return interval.end_inclusive
    else:
        left_x, right_x = sorted([interval.start.x, interval.end.x])
        bottom_y, top_y = sorted([interval.start.y, interval.end.y])
        return left_x <= point.x <= right_x and bottom_y <= point.y <= top_y
