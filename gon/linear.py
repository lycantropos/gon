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
    __slots__ = ('_start', '_end', '_with_start', '_with_end')

    def __init__(self,
                 start: Point,
                 end: Point,
                 *,
                 with_start: bool,
                 with_end: bool) -> None:
        self._start = start
        self._end = end
        self._with_start = with_start
        self._with_end = with_end

    @property
    def start(self) -> Point:
        return self._start

    @property
    def end(self) -> Point:
        return self._end

    @property
    def with_start(self) -> bool:
        return self._with_start

    @property
    def with_end(self) -> bool:
        return self._with_end

    @property
    def reversed(self) -> 'Interval':
        return type(self)(self.end, self.start,
                          with_start=self.with_end,
                          with_end=self.with_start)

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'Interval') -> bool:
        return (self._with_start is other._with_start
                and self._with_end is other._with_end
                and self._start == other._start
                and self._end == other._end
                or self._with_start is other._with_end
                and self._with_end is other._with_start
                and self._start == other._end
                and self._end == other._start
                if isinstance(other, Interval)
                else NotImplemented)

    def __hash__(self) -> int:
        return hash(frozenset([(self._start, self._with_start),
                               (self._end, self._with_end)]))

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
                    elif self.with_start:
                        return IntersectionKind.CROSS
                    else:
                        return IntersectionKind.NONE
                elif self.start == other.end:
                    if (Angle(self.end, self.start, other.start).kind
                            is AngleKind.ACUTE):
                        return IntersectionKind.OVERLAP
                    elif self.with_start:
                        return IntersectionKind.CROSS
                    else:
                        return IntersectionKind.NONE
                else:
                    return IntersectionKind.OVERLAP
            elif self.with_start:
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
                    elif self.with_end:
                        return IntersectionKind.CROSS
                    else:
                        return IntersectionKind.NONE
                elif self.end == other.end:
                    if (Angle(self.start, self.end, other.start).kind
                            is AngleKind.ACUTE):
                        return IntersectionKind.OVERLAP
                    elif self.with_end:
                        return IntersectionKind.CROSS
                    else:
                        return IntersectionKind.NONE
                else:
                    return IntersectionKind.OVERLAP
            elif self.with_end:
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
                    elif other.with_start:
                        return IntersectionKind.CROSS
                    else:
                        return IntersectionKind.NONE
                elif other.start == self.end:
                    if (Angle(other.end, other.start, self.start).kind
                            is AngleKind.ACUTE):
                        return IntersectionKind.OVERLAP
                    elif other.with_start:
                        return IntersectionKind.CROSS
                    else:
                        return IntersectionKind.NONE
                else:
                    return IntersectionKind.OVERLAP
            elif other.with_start:
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
                    elif other.with_end:
                        return IntersectionKind.CROSS
                    else:
                        return IntersectionKind.NONE
                elif other.end == self.end:
                    if (Angle(other.start, other.end, self.start).kind
                            is AngleKind.ACUTE):
                        return IntersectionKind.OVERLAP
                    elif other.with_end:
                        return IntersectionKind.CROSS
                    else:
                        return IntersectionKind.NONE
                else:
                    return IntersectionKind.OVERLAP
            elif other.with_end:
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
                         with_start=True,
                         with_end=True)

    @property
    def reversed(self) -> 'Segment':
        return type(self)(self.end, self.start)

    __repr__ = generate_repr(__init__)


def to_interval(start: Point, end: Point,
                *,
                with_start: bool,
                with_end: bool) -> Union[Interval, Segment]:
    if start == end:
        raise ValueError('Degenerate interval found.')
    if with_start and with_end:
        return Segment(start, end)
    return Interval(start, end,
                    with_start=with_start,
                    with_end=with_end)


to_segment = partial(to_interval,
                     with_start=True,
                     with_end=True)


def _in_interval(point: Point, interval: Interval) -> bool:
    if point == interval.start:
        return interval.with_start
    elif point == interval.end:
        return interval.with_end
    else:
        left_x, right_x = ((interval.start.x, interval.end.x)
                           if interval.start.x < interval.end.x
                           else (interval.end.x, interval.start.x))
        bottom_y, top_y = ((interval.start.y, interval.end.y)
                           if interval.start.y < interval.end.y
                           else (interval.end.y, interval.start.y))
        return left_x <= point.x <= right_x and bottom_y <= point.y <= top_y
