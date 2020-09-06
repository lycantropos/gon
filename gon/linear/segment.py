from typing import Optional

from orient.planar import (point_in_segment,
                           segment_in_segment)
from reprit.base import generate_repr
from robust.linear import (segments_intersection,
                           segments_intersections)

from gon.compound import (Compound,
                          Linear,
                          Location,
                          Relation)
from gon.core.arithmetic import (non_negative_min,
                                 robust_divide)
from gon.degenerate import EMPTY
from gon.discrete import Multipoint
from gon.geometry import Geometry
from gon.hints import Coordinate
from gon.primitive import Point
from gon.primitive.point import (point_to_step,
                                 rotate_point_around_origin,
                                 rotate_translate_point,
                                 scale_point)
from .hints import (RawMultisegment,
                    RawSegment)
from .raw import (raw_segment_point_distance,
                  raw_segments_distance)
from .utils import (from_raw_multisegment,
                    relate_multipoint_to_linear_compound)


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
        return (self._intersect_with_segment(other)
                if isinstance(other, Segment)
                else NotImplemented)

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

    def __xor__(self, other: Compound) -> Compound:
        """
        Returns symmetric difference of the segment with the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment ^ segment is EMPTY
        True
        """
        return (self._unite_with_multipoint(other)
                if isinstance(other, Multipoint)
                else (self._symmetric_subtract_segment(other)
                      if isinstance(other, Segment)
                      else NotImplemented))

    __rxor__ = __xor__

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
    def centroid(self) -> Point:
        """
        Returns centroid of the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment.centroid == Point(1, 0)
        True
        """
        return Point(robust_divide(self._start.x + self._end.x, 2),
                     robust_divide(self._start.y + self._end.y, 2))

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
    def is_horizontal(self) -> bool:
        """
        Checks if the segment is horizontal.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment.is_horizontal
        True
        """
        return self._start.y == self._end.y

    @property
    def is_vertical(self) -> bool:
        """
        Checks if the segment is vertical.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment.is_vertical
        False
        """
        return self._start.x == self._end.x

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
        return self._end._distance_to_point(self._start)

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

    def distance_to(self, other: Geometry) -> Coordinate:
        """
        Returns distance between the segment and the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment.distance_to(segment) == 0
        True
        """
        return (raw_segment_point_distance(self._raw, other.raw())
                if isinstance(other, Point)
                else (non_negative_min(raw_segment_point_distance(self._raw,
                                                                  raw_point)
                                       for raw_point in other._raw)
                      if isinstance(other, Multipoint)
                      else (raw_segments_distance(self._raw, other._raw)
                            if isinstance(other, Segment)
                            else other.distance_to(self))))

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
        return (Location.BOUNDARY
                if point_in_segment(point.raw(), self._raw)
                else Location.EXTERIOR)

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

    def rotate(self,
               cosine: Coordinate,
               sine: Coordinate,
               point: Optional[Point] = None) -> 'Segment':
        """
        Rotates the segment by given cosine & sine around given point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment.rotate(1, 0) == segment
        True
        >>> (segment.rotate(0, 1, Point(1, 1))
        ...  == Segment.from_raw(((2, 0), (2, 2))))
        True
        """
        return (rotate_segment_around_origin(self, cosine, sine)
                if point is None
                else rotate_translate_segment(self, cosine, sine,
                                              *point_to_step(point, cosine,
                                                             sine)))

    def scale(self,
              factor_x: Coordinate,
              factor_y: Optional[Coordinate] = None) -> Compound:
        """
        Scales the segment by given factor.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment.scale(1) == segment.scale(1, 2) == segment
        True
        """
        return scale_segment(self, factor_x,
                             factor_x if factor_y is None else factor_y)

    def translate(self, step_x: Coordinate, step_y: Coordinate) -> 'Segment':
        """
        Translates the segment by given step.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment.from_raw(((0, 0), (2, 0)))
        >>> segment.translate(1, 2) == Segment.from_raw(((1, 2), (3, 2)))
        True
        """
        return Segment(self._start.translate(step_x, step_y),
                       self._end.translate(step_x, step_y))

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

    def _intersect_with_segment(self, other: 'Segment') -> Compound:
        intersections = [Point.from_raw(raw_point)
                         for raw_point in segments_intersections(self._raw,
                                                                 other._raw)]
        return ((Multipoint(*intersections)
                 if len(intersections) == 1
                 else Segment(*intersections))
                if intersections
                else EMPTY)

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

    def _symmetric_subtract_segment(self, other: 'Segment') -> Compound:
        # importing here to avoid cyclic imports
        from .multisegment import Multisegment
        relation = segment_in_segment(self._raw, other._raw)
        return (EMPTY
                if relation is Relation.EQUAL
                else
                (Multisegment(self, other)
                 if relation is Relation.DISJOINT or relation is Relation.TOUCH
                 else (Multisegment.from_raw(_raw_unite_cross(self._raw,
                                                              other._raw))
                       if relation is Relation.CROSS
                       else
                       (Multisegment.from_raw(_raw_symmetric_subtract_overlap(
                               self._raw, other._raw))
                        if relation is Relation.OVERLAP
                        else from_raw_multisegment(
                               _raw_subtract_composite(self._raw, other._raw)
                               if relation is Relation.COMPOSITE
                               else _raw_subtract_composite(other._raw,
                                                            self._raw))))))

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


def rotate_segment_around_origin(segment: Segment,
                                 cosine: Coordinate,
                                 sine: Coordinate) -> Segment:
    return Segment(rotate_point_around_origin(segment._start, cosine, sine),
                   rotate_point_around_origin(segment._end, cosine, sine))


def rotate_translate_segment(segment: Segment,
                             cosine: Coordinate,
                             sine: Coordinate,
                             step_x: Coordinate,
                             step_y: Coordinate) -> Segment:
    return Segment(rotate_translate_point(segment._start, cosine, sine, step_x,
                                          step_y),
                   rotate_translate_point(segment._end, cosine, sine, step_x,
                                          step_y))


def scale_segment(segment: Segment,
                  factor_x: Coordinate,
                  factor_y: Coordinate) -> Compound:
    return (Segment(scale_point(segment._start, factor_x, factor_y),
                    scale_point(segment._end, factor_x, factor_y))
            if ((factor_x or not segment.is_horizontal) and factor_y
                or factor_x and not segment.is_vertical)
            else Multipoint(scale_point(segment._start, factor_x, factor_y)))


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


def _raw_symmetric_subtract_overlap(minuend: RawSegment,
                                    subtrahend: RawSegment) -> RawMultisegment:
    left_start, left_end, right_start, right_end = sorted(minuend + subtrahend)
    return [(left_start, left_end), (right_start, right_end)]


def _raw_unite_cross(first_addend: RawSegment,
                     second_addend: RawSegment) -> RawMultisegment:
    cross_point = segments_intersection(first_addend, second_addend)
    first_addend_start, first_addend_end = first_addend
    second_addend_start, second_addend_end = second_addend
    return [(first_addend_start, cross_point),
            (second_addend_start, cross_point),
            (cross_point, first_addend_end),
            (cross_point, second_addend_end)]


def _raw_unite_overlap(first_addend: RawSegment,
                       second_addend: RawSegment) -> RawSegment:
    start, _, _, end = sorted(first_addend + second_addend)
    return start, end
