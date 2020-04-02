from typing import Tuple

from reprit.base import generate_repr
from robust.hints import Expansion
from robust.linear import (SegmentsRelationship,
                           segment_contains,
                           segments_relationship)
from robust.utils import (two_product,
                          two_two_diff)

from .angular import (Orientation,
                      to_orientation)
from .geometry import Geometry
from .point import (Point,
                    RawPoint)

RawSegment = Tuple[RawPoint, RawPoint]
SegmentsRelationship = SegmentsRelationship


class Segment(Geometry):
    __slots__ = '_start', '_end'

    def __init__(self, start: Point, end: Point) -> None:
        self._start = start
        self._end = end

    __repr__ = generate_repr(__init__)

    @property
    def start(self) -> Point:
        return self._start

    @property
    def end(self) -> Point:
        return self._end

    def raw(self) -> RawSegment:
        return self._start.raw(), self._end.raw()

    @classmethod
    def from_raw(cls, raw: RawSegment) -> 'Segment':
        raw_start, raw_end = raw
        start, end = Point.from_raw(raw_start), Point.from_raw(raw_end)
        return cls(start, end)

    def validate(self) -> None:
        if self.start == self.end:
            raise ValueError('Segment is degenerate.')

    def __eq__(self, other: 'Segment') -> bool:
        return (self._start == other._start and self._end == other._end
                or self._start == other._end and self._end == other._start
                if isinstance(other, Segment)
                else NotImplemented)

    def __hash__(self) -> int:
        return hash(frozenset((self._start, self._end)))

    def __contains__(self, point: Point) -> bool:
        return segment_contains(self.raw(), point.raw())

    def relationship_with(self, other: 'Segment') -> SegmentsRelationship:
        return segments_relationship(self.raw(), other.raw())

    def orientation_with(self, point: Point) -> Orientation:
        return to_orientation(self.end, self.start, point)


def _segment_to_endpoints_cross_product_z(segment: Segment) -> Expansion:
    minuend, minuend_tail = two_product(segment.start.x, segment.end.y)
    subtrahend, subtrahend_tail = two_product(segment.start.y, segment.end.x)
    return (two_two_diff(minuend, minuend_tail, subtrahend, subtrahend_tail)
            if minuend_tail or subtrahend_tail
            else (minuend - subtrahend,))
