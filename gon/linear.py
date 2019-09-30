from enum import (IntEnum,
                  unique)
from functools import partial
from typing import Union

from reprit.base import generate_repr

from .angular import (Angle,
                      AngleKind,
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
        self_end_orientation = other.orientation_with(self.end)
        if (self_start_orientation is Orientation.COLLINEAR
                and _in_interval(self.start, other)):
            if self_end_orientation is Orientation.COLLINEAR:
                if self.start == other.start:
                    if (Angle(self.end, self.start, other.end).kind
                            is AngleKind.ACUTE):
                        return IntersectionKind.OVERLAP
                    elif self.start_inclusive:
                        return IntersectionKind.CROSS
                    else:
                        return IntersectionKind.NONE
                elif self.start == other.end:
                    if (Angle(self.end, self.start, other.start).kind
                            is AngleKind.ACUTE):
                        return IntersectionKind.OVERLAP
                    elif self.start_inclusive:
                        return IntersectionKind.CROSS
                    else:
                        return IntersectionKind.NONE
                else:
                    return IntersectionKind.OVERLAP
            elif self.start_inclusive:
                return IntersectionKind.CROSS
            else:
                return IntersectionKind.NONE
        elif (self_end_orientation is Orientation.COLLINEAR
              and _in_interval(self.end, other)):
            if self_start_orientation is Orientation.COLLINEAR:
                if self.end == other.start:
                    if (Angle(self.start, self.end, other.end).kind
                            is AngleKind.ACUTE):
                        return IntersectionKind.OVERLAP
                    elif self.end_inclusive:
                        return IntersectionKind.CROSS
                    else:
                        return IntersectionKind.NONE
                elif self.end == other.end:
                    if (Angle(self.start, self.end, other.start).kind
                            is AngleKind.ACUTE):
                        return IntersectionKind.OVERLAP
                    elif self.end_inclusive:
                        return IntersectionKind.CROSS
                    else:
                        return IntersectionKind.NONE
                else:
                    return IntersectionKind.OVERLAP
            elif self.end_inclusive:
                return IntersectionKind.CROSS
            else:
                return IntersectionKind.NONE
        other_start_orientation = self.orientation_with(other.start)
        other_end_orientation = self.orientation_with(other.end)
        if (self_start_orientation * self_end_orientation < 0
                and other_start_orientation * other_end_orientation < 0):
            return IntersectionKind.CROSS
        elif (other_start_orientation is Orientation.COLLINEAR
              and _in_interval(other.start, self)):
            if other_end_orientation is Orientation.COLLINEAR:
                if other.start == self.start:
                    if (Angle(other.end, other.start, self.end).kind
                            is AngleKind.ACUTE):
                        return IntersectionKind.OVERLAP
                    elif other.start_inclusive:
                        return IntersectionKind.CROSS
                    else:
                        return IntersectionKind.NONE
                elif other.start == self.end:
                    if (Angle(other.end, other.start, self.start).kind
                            is AngleKind.ACUTE):
                        return IntersectionKind.OVERLAP
                    elif other.start_inclusive:
                        return IntersectionKind.CROSS
                    else:
                        return IntersectionKind.NONE
                else:
                    return IntersectionKind.OVERLAP
            elif other.start_inclusive:
                return IntersectionKind.CROSS
            else:
                return IntersectionKind.NONE
        elif (other_end_orientation is Orientation.COLLINEAR
              and _in_interval(other.end, self)):
            if other_start_orientation is Orientation.COLLINEAR:
                if other.end == self.start:
                    if (Angle(other.start, other.end, self.end).kind
                            is AngleKind.ACUTE):
                        return IntersectionKind.OVERLAP
                    elif other.end_inclusive:
                        return IntersectionKind.CROSS
                    else:
                        return IntersectionKind.NONE
                elif other.end == self.end:
                    if (Angle(other.start, other.end, self.start).kind
                            is AngleKind.ACUTE):
                        return IntersectionKind.OVERLAP
                    elif other.end_inclusive:
                        return IntersectionKind.CROSS
                    else:
                        return IntersectionKind.NONE
                else:
                    return IntersectionKind.OVERLAP
            elif other.end_inclusive:
                return IntersectionKind.CROSS
            else:
                return IntersectionKind.NONE
        else:
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
        left_x, right_x = ((interval.start.x, interval.end.x)
                           if interval.start.x < interval.end.x
                           else (interval.end.x, interval.start.x))
        bottom_y, top_y = ((interval.start.y, interval.end.y)
                           if interval.start.y < interval.end.y
                           else (interval.end.y, interval.start.y))
        return left_x <= point.x <= right_x and bottom_y <= point.y <= top_y
