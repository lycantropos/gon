from operator import (le,
                      lt)
from types import MappingProxyType
from typing import (Callable,
                    Mapping,
                    Union)

from reprit.base import generate_repr

from .angular import (Angle,
                      Orientation)
from .base import Point
from .hints import Scalar


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

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'Interval') -> bool:
        return (self._start_inclusive is other._start_inclusive
                and self._end_inclusive is other._end_inclusive
                and self._start == other._start
                and self._end == other._end
                or self._start_inclusive is other._end_inclusive
                and self._end_inclusive is other._start_inclusive
                and self._start == other._end
                and self._end == other._start)

    def __hash__(self) -> int:
        return hash(frozenset([(self._start, self.start_inclusive),
                               (self._end, self.end_inclusive)]))

    def __contains__(self, point: Point) -> bool:
        return (self.orientation_with(point) == Orientation.COLLINEAR
                and _in_interval(point, self))

    def intersects_with(self, other: 'Interval') -> bool:
        self_start_orientation = other.orientation_with(self.start)
        if (self.start_inclusive
                and self_start_orientation == Orientation.COLLINEAR
                and _in_interval(self.start, other)):
            return True
        self_end_orientation = other.orientation_with(self.end)
        if (self.end_inclusive
                and self_end_orientation == Orientation.COLLINEAR
                and _in_interval(self.end, other)):
            return True
        other_start_orientation = self.orientation_with(other.start)
        if (other.start_inclusive
                and other_start_orientation == Orientation.COLLINEAR
                and _in_interval(other.start, self)):
            return True
        other_end_orientation = self.orientation_with(other.end)
        return (self_start_orientation * self_end_orientation < 0
                and other_start_orientation * other_end_orientation < 0
                or other.end_inclusive
                and other_end_orientation == Orientation.COLLINEAR
                and _in_interval(other.end, self))

    def orientation_with(self, point: Point) -> int:
        return Angle(self.start, self.end, point).orientation


class Segment(Interval):
    def __init__(self, start: Point, end: Point) -> None:
        super().__init__(start, end,
                         start_inclusive=True,
                         end_inclusive=True)

    __repr__ = generate_repr(__init__)


def to_interval(start: Point, end: Point,
                *,
                start_inclusive: bool = True,
                end_inclusive: bool = True) -> Union[Interval, Segment]:
    if start == end:
        raise ValueError('Degenerate interval found.')
    if start_inclusive and end_inclusive:
        return Segment(start, end)
    return Interval(start, end,
                    start_inclusive=start_inclusive,
                    end_inclusive=end_inclusive)


def _in_interval(point: Point, interval: Interval,
                 *,
                 flags_predicates: Mapping[bool,
                                           Callable[[Scalar, Scalar], bool]]
                 = MappingProxyType({False: lt,
                                     True: le})
                 ) -> bool:
    start_predicate = flags_predicates[interval.start_inclusive]
    end_predicate = flags_predicates[interval.end_inclusive]
    ((left_x, left_x_predicate),
     (right_x, right_x_predicate)) = sorted([(interval.start.x,
                                              start_predicate),
                                             (interval.end.x,
                                              end_predicate)])
    ((bottom_y, bottom_y_predicate),
     (top_y, top_y_predicate)) = sorted([(interval.start.y, start_predicate),
                                         (interval.end.y, end_predicate)])
    return (left_x_predicate(left_x, point.x)
            and right_x_predicate(point.x, right_x)
            and bottom_y_predicate(bottom_y, point.y)
            and top_y_predicate(point.y, top_y))
