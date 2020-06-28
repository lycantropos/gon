import math

from orient.planar import (point_in_segment,
                           segment_in_segment)
from reprit.base import generate_repr
from robust.hints import Point
from robust.linear import (segments_intersection,
                           segments_intersections)

from gon.compound import (Compound,
                          Linear,
                          Location,
                          Relation)
from gon.degenerate import EMPTY
from gon.discrete import Multipoint
from gon.geometry import Geometry
from gon.hints import Coordinate
from gon.primitive import (Point,
                           RawPoint)
from .hints import (RawMultisegment,
                    RawSegment)
from .utils import (from_raw_multisegment,
                    relate_multipoint_to_linear_compound,
                    squared_points_distance)


class Segment(Compound, Linear):
    __slots__ = '_start', '_end', '_raw'

    def __init__(self, start: Point, end: Point) -> None:
        """
        Initializes segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        """
        self._start, self._end = start, end
        self._raw = start.raw(), end.raw()

    __repr__ = generate_repr(__init__)

    def __and__(self, other: Compound) -> Compound:
        """
        Returns intersection of the segment with the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment & segment == segment
        True
        """
        return (self._intersect_with_multipoint(other)
                if isinstance(other, Multipoint)
                else (self._intersect_with_segment(other)
                      if isinstance(other, Segment)
                      else NotImplemented))

    __rand__ = __and__

    def __contains__(self, other: Geometry) -> bool:
        """
        Checks if the segment contains the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment.start in segment
        True
        >>> segment.end in segment
        True
        """
        return isinstance(other, Point) and bool(self.locate(other))

    def __eq__(self, other: 'Segment') -> bool:
        """
        Checks if the segment is equal to the other.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment == segment
        True
        >>> segment == Segment.from_raw(((2, 0), (0, 0)))
        True
        >>> segment == Segment.from_raw(((0, 0), (1, 0)))
        False
        >>> segment == Segment.from_raw(((0, 0), (0, 2)))
        False
        """
        return (self is other
                or (self._start == other._start and self._end == other._end
                    or self._start == other._end and self._end == other._start
                    if isinstance(other, Segment)
                    else NotImplemented))

    def __ge__(self, other: Compound) -> bool:
        """
        Checks if the segment is a superset of the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment >= segment
        True
        >>> segment >= Segment.from_raw(((2, 0), (0, 0)))
        True
        >>> segment >= Segment.from_raw(((0, 0), (1, 0)))
        True
        >>> segment >= Segment.from_raw(((0, 0), (0, 2)))
        False
        """
        return (other is EMPTY
                or self == other
                or ((self.relate(other) is Relation.COMPONENT
                     if isinstance(other, (Multipoint, Segment))
                     # segment cannot be superset of contour or shaped
                     else False)
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __gt__(self, other: Compound) -> bool:
        """
        Checks if the segment is a strict superset of the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment > segment
        False
        >>> segment > Segment.from_raw(((2, 0), (0, 0)))
        False
        >>> segment > Segment.from_raw(((0, 0), (1, 0)))
        True
        >>> segment > Segment.from_raw(((0, 0), (0, 2)))
        False
        """
        return (other is EMPTY
                or self != other
                and ((self.relate(other) is Relation.COMPONENT
                      if isinstance(other, (Multipoint, Segment))
                      # segment cannot be strict superset of contour or shaped
                      else False)
                     if isinstance(other, Compound)
                     else NotImplemented))

    def __hash__(self) -> int:
        """
        Returns hash value of the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> hash(segment) == hash(segment)
        True
        >>> hash(segment) == hash(Segment.from_raw(((2, 0), (0, 0))))
        True
        """
        return hash(frozenset(self._raw))

    def __le__(self, other: Compound) -> bool:
        """
        Checks if the segment is a subset of the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment <= segment
        True
        >>> segment <= Segment.from_raw(((2, 0), (0, 0)))
        True
        >>> segment <= Segment.from_raw(((0, 0), (1, 0)))
        False
        >>> segment <= Segment.from_raw(((0, 0), (0, 2)))
        False
        """
        return (self == other
                or not isinstance(other, Multipoint)
                and (self.relate(other) in (Relation.EQUAL, Relation.COMPOSITE)
                     if isinstance(other, Linear)
                     else NotImplemented))

    def __lt__(self, other: Compound) -> bool:
        """
        Checks if the segment is a strict subset of the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment < segment
        False
        >>> segment < Segment.from_raw(((2, 0), (0, 0)))
        False
        >>> segment < Segment.from_raw(((0, 0), (1, 0)))
        False
        >>> segment < Segment.from_raw(((0, 0), (0, 2)))
        False
        """
        return (self != other
                and not isinstance(other, Multipoint)
                and (self.relate(other) is Relation.COMPOSITE
                     if isinstance(other, Linear)
                     else NotImplemented))

    def __or__(self, other: Compound) -> Compound:
        """
        Returns union of the segment with the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment | segment == segment
        True
        """
        return (self._unite_with_multipoint(other)
                if isinstance(other, Multipoint)
                else (self._unite_with_segment(other)
                      if isinstance(other, Segment)
                      else NotImplemented))

    __ror__ = __or__

    def __sub__(self, other: Compound) -> Compound:
        """
        Returns difference of the segment with the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment - segment is EMPTY
        True
        """
        return (self
                if isinstance(other, Multipoint)
                else (self._subtract_segment(other)
                      if isinstance(other, Segment)
                      else NotImplemented))

    @classmethod
    def from_raw(cls, raw: RawSegment) -> 'Segment':
        """
        Constructs segment from the combination of Python built-ins.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment == Segment(Point(0, 0), Point(2, 0))
        True
        """
        raw_start, raw_end = raw
        start, end = Point.from_raw(raw_start), Point.from_raw(raw_end)
        return cls(start, end)

    @property
    def end(self) -> Point:
        """
        Returns end of the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment.end == Point(2, 0)
        True
        """
        return self._end

    @property
    def length(self) -> Coordinate:
        """
        Returns length of the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment.length == 2
        True
        """
        return math.sqrt(squared_points_distance(self.start, self.end))

    @property
    def start(self) -> Point:
        """
        Returns start of the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment.start == Point(0, 0)
        True
        """
        return self._start

    def locate(self, point: Point) -> Location:
        """
        Finds location of the point relative to the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment.locate(segment.start) is Location.BOUNDARY
        True
        >>> segment.locate(segment.end) is Location.BOUNDARY
        True
        """
        return raw_locate_point(self._raw, point.raw())

    def raw(self) -> RawSegment:
        """
        Returns the segment as combination of Python built-ins.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment.raw()
        ((0, 0), (2, 0))
        """
        return self._raw

    def relate(self, other: Compound) -> Relation:
        """
        Finds relation between the segment and the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment.relate(segment) is Relation.EQUAL
        True
        """
        return (relate_multipoint_to_linear_compound(other, self)
                if isinstance(other, Multipoint)
                else (segment_in_segment(other._raw, self._raw)
                      if isinstance(other, Segment)
                      else other.relate(self).complement))

    def validate(self) -> None:
        """
        Checks if endpoints are valid and unequal.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment.validate()
        """
        self._start.validate()
        self._end.validate()
        if self._start == self._end:
            raise ValueError('Segment is degenerate.')

    def _intersect_with_multipoint(self, other: Multipoint) -> Compound:
        points = [point for point in other.points if point in self]
        return Multipoint(*points) if points else EMPTY

    def _intersect_with_segment(self, other: 'Segment') -> Compound:
        intersections = [Point.from_raw(raw_point)
                         for raw_point in segments_intersections(self._raw,
                                                                 other._raw)]
        return ((Multipoint(*intersections)
                 if len(intersections) == 1
                 else Segment(*intersections))
                if intersections
                else EMPTY)

    def _unite_with_multipoint(self, other: Multipoint) -> Compound:
        # importing here to avoid cyclic imports
        from gon.mixed.mix import from_mix_components
        return from_mix_components(other - self, self, EMPTY)

    def _unite_with_segment(self, other: 'Segment') -> Compound:
        from .multisegment import Multisegment
        relation = segment_in_segment(self._raw, other._raw)
        return (self
                if relation is Relation.EQUAL or relation is Relation.COMPOSITE
                else (other
                      if relation is Relation.COMPONENT
                      else
                      (Segment.from_raw(_raw_unite_overlap(self._raw,
                                                           other._raw))
                       if relation is Relation.OVERLAP
                       else (Multisegment.from_raw(
                              _raw_unite_cross(self._raw, other._raw))
                             if relation is Relation.CROSS
                             else Multisegment(self, other)))))

    def _subtract_segment(self, other: 'Segment') -> Compound:
        relation = segment_in_segment(self._raw, other._raw)
        return (EMPTY
                if relation is Relation.EQUAL or relation is Relation.COMPONENT
                else
                (self
                 if relation in (Relation.DISJOINT, Relation.TOUCH,
                                 Relation.CROSS)
                 else (Segment.from_raw(_raw_subtract_overlap(self._raw,
                                                              other._raw))
                       if relation is Relation.OVERLAP
                       else from_raw_multisegment(_raw_subtract_composite(
                        self._raw, other._raw)))))


def raw_locate_point(raw_segment: RawSegment, raw_point: RawPoint) -> Location:
    return (Location.BOUNDARY
            if point_in_segment(raw_point, raw_segment)
            else Location.EXTERIOR)


def _raw_subtract_overlap(minuend: RawSegment,
                          subtrahend: RawSegment) -> RawSegment:
    left_start, left_end, right_start, right_end = sorted(minuend + subtrahend)
    return ((left_start, left_end)
            if left_start in minuend
            else (right_start, right_end))


def _raw_subtract_composite(minuend: RawSegment,
                            subtrahend: RawSegment) -> RawMultisegment:
    left_start, left_end, right_start, right_end = sorted(minuend + subtrahend)
    return ([(right_start, right_end)]
            if left_start in subtrahend
            else ((([(left_start, left_end)]
                    if right_start == right_end
                    else [(left_start, left_end), (right_start, right_end)])
                   if right_start in subtrahend
                   else [(left_start, left_end)])
                  if left_end in subtrahend
                  else [(left_start, right_start)]))


def _raw_unite_overlap(first_addend: RawSegment,
                       second_addend: RawSegment) -> RawSegment:
    start, _, _, end = sorted(first_addend + second_addend)
    return start, end


def _raw_unite_cross(first_addend: RawSegment,
                     second_addend: RawSegment) -> RawMultisegment:
    cross_point = segments_intersection(first_addend, second_addend)
    first_addend_start, first_addend_end = first_addend
    second_addend_start, second_addend_end = second_addend
    return [(first_addend_start, cross_point),
            (second_addend_start, cross_point),
            (cross_point, first_addend_end),
            (cross_point, second_addend_end)]
