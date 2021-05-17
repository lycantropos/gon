from typing import Optional

from clipping.planar import (intersect_segments,
                             subtract_segments,
                             symmetric_subtract_segments,
                             unite_segments)
from ground.base import (Context,
                         get_context)
from orient.planar import segment_in_segment
from reprit.base import generate_repr

from .compound import (Compound,
                       Linear,
                       Location,
                       Relation)
from .empty import EMPTY
from .geometry import Geometry
from .hints import Scalar
from .iterable import non_negative_min
from .mix import from_mix_components
from .multipoint import Multipoint
from .point import (Point,
                    point_to_step,
                    rotate_point_around_origin,
                    rotate_translate_point,
                    scale_point)
from .utils import relate_multipoint_to_linear_compound


class Segment(Compound, Linear):
    __slots__ = '_context', '_endpoints', '_end', '_start'

    def __init__(self, start: Point, end: Point) -> None:
        """
        Initializes segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        """
        context = get_context()
        self._context = context
        self._start, self._end = self._endpoints = start, end

    __repr__ = generate_repr(__init__)

    def __and__(self, other: Compound) -> Compound:
        """
        Returns intersection of the segment with the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment & segment == segment
        True
        """
        return (intersect_segments(self, other,
                                   context=self.context)
                if isinstance(other, Segment)
                else NotImplemented)

    __rand__ = __and__

    def __contains__(self, point: Point) -> bool:
        """
        Checks if the segment contains the point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.start in segment
        True
        >>> segment.end in segment
        True
        """
        return bool(self.locate(point))

    def __eq__(self, other: 'Segment') -> bool:
        """
        Checks if the segment is equal to the other.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment == segment
        True
        >>> segment == Segment(Point(2, 0), Point(0, 0))
        True
        >>> segment == Segment(Point(0, 0), Point(1, 0))
        False
        >>> segment == Segment(Point(0, 0), Point(0, 2))
        False
        """
        return (self is other
                or (self.start == other.start and self.end == other.end
                    or self.start == other.end and self.end == other.start
                    if isinstance(other, Segment)
                    else NotImplemented))

    def __ge__(self, other: Compound) -> bool:
        """
        Checks if the segment is a superset of the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment >= segment
        True
        >>> segment >= Segment(Point(2, 0), Point(0, 0))
        True
        >>> segment >= Segment(Point(0, 0), Point(1, 0))
        True
        >>> segment >= Segment(Point(0, 0), Point(0, 2))
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

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment > segment
        False
        >>> segment > Segment(Point(2, 0), Point(0, 0))
        False
        >>> segment > Segment(Point(0, 0), Point(1, 0))
        True
        >>> segment > Segment(Point(0, 0), Point(0, 2))
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

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> hash(segment) == hash(segment)
        True
        >>> hash(segment) == hash(Segment(Point(2, 0), Point(0, 0)))
        True
        """
        return hash(frozenset(self._endpoints))

    def __le__(self, other: Compound) -> bool:
        """
        Checks if the segment is a subset of the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment <= segment
        True
        >>> segment <= Segment(Point(2, 0), Point(0, 0))
        True
        >>> segment <= Segment(Point(0, 0), Point(1, 0))
        False
        >>> segment <= Segment(Point(0, 0), Point(0, 2))
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

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment < segment
        False
        >>> segment < Segment(Point(2, 0), Point(0, 0))
        False
        >>> segment < Segment(Point(0, 0), Point(1, 0))
        False
        >>> segment < Segment(Point(0, 0), Point(0, 2))
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

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment | segment == segment
        True
        """
        return (from_mix_components(other - self, self, EMPTY)
                if isinstance(other, Multipoint)
                else (unite_segments(self, other,
                                     context=self.context)
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

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment - segment is EMPTY
        True
        """
        return (self
                if isinstance(other, Multipoint)
                else (subtract_segments(self, other,
                                        context=self.context)
                      if isinstance(other, Segment)
                      else NotImplemented))

    def __xor__(self, other: Compound) -> Compound:
        """
        Returns symmetric difference of the segment with the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment ^ segment is EMPTY
        True
        """
        return (from_mix_components(other - self, self, EMPTY)
                if isinstance(other, Multipoint)
                else (symmetric_subtract_segments(self, other,
                                                  context=self.context)
                      if isinstance(other, Segment)
                      else NotImplemented))

    __rxor__ = __xor__

    @property
    def centroid(self) -> Point:
        """
        Returns centroid of the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.centroid == Point(1, 0)
        True
        """
        return self.context.segment_centroid(self)

    @property
    def context(self) -> Context:
        """
        Returns centroid of the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> isinstance(segment.context, Context)
        True
        """
        return self._context

    @property
    def end(self) -> Point:
        """
        Returns end of the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
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

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.is_horizontal
        True
        """
        return self.start.y == self.end.y

    @property
    def is_vertical(self) -> bool:
        """
        Checks if the segment is vertical.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.is_vertical
        False
        """
        return self.start.x == self.end.x

    @property
    def length(self) -> Scalar:
        """
        Returns length of the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.length == 2
        True
        """
        return self.context.sqrt(
                self.context.points_squared_distance(self.start, self.end))

    @property
    def start(self) -> Point:
        """
        Returns start of the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.start == Point(0, 0)
        True
        """
        return self._start

    def distance_to(self, other: Geometry) -> Scalar:
        """
        Returns distance between the segment and the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.distance_to(segment) == 0
        True
        """
        return (self.context.sqrt(self.context.segment_point_squared_distance(
                self, other))
                if isinstance(other, Point)
                else
                (non_negative_min(
                        self.context.sqrt(
                                self.context.segment_point_squared_distance(
                                        self, point))
                        for point in other.points)
                 if isinstance(other, Multipoint)
                 else (self.context.sqrt(
                        self.context.segments_squared_distance(self, other))
                       if isinstance(other, Segment)
                       else other.distance_to(self))))

    def locate(self, point: Point) -> Location:
        """
        Finds location of the point relative to the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.locate(segment.start) is Location.BOUNDARY
        True
        >>> segment.locate(segment.end) is Location.BOUNDARY
        True
        """
        return (Location.BOUNDARY
                if self.context.segment_contains_point(self, point)
                else Location.EXTERIOR)

    def relate(self, other: Compound) -> Relation:
        """
        Finds relation between the segment and the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.relate(segment) is Relation.EQUAL
        True
        """
        return (relate_multipoint_to_linear_compound(other, self)
                if isinstance(other, Multipoint)
                else (segment_in_segment(other, self,
                                         context=self.context)
                      if isinstance(other, Segment)
                      else other.relate(self).complement))

    def rotate(self,
               cosine: Scalar,
               sine: Scalar,
               point: Optional[Point] = None) -> 'Segment':
        """
        Rotates the segment by given cosine & sine around given point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.rotate(1, 0) == segment
        True
        >>> (segment.rotate(0, 1, Point(1, 1))
        ...  == Segment(Point(2, 0), Point(2, 2)))
        True
        """
        return (rotate_segment_around_origin(self, cosine, sine)
                if point is None
                else rotate_translate_segment(self, cosine, sine,
                                              *point_to_step(point, cosine,
                                                             sine)))

    def scale(self,
              factor_x: Scalar,
              factor_y: Optional[Scalar] = None) -> Compound:
        """
        Scales the segment by given factor.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.scale(1) == segment.scale(1, 2) == segment
        True
        """
        return scale_segment(self, factor_x,
                             factor_x if factor_y is None else factor_y)

    def translate(self, step_x: Scalar, step_y: Scalar) -> 'Segment':
        """
        Translates the segment by given step.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.translate(1, 2) == Segment(Point(1, 2), Point(3, 2))
        True
        """
        return Segment(self.start.translate(step_x, step_y),
                       self.end.translate(step_x, step_y))

    def validate(self) -> None:
        """
        Checks if endpoints are valid and unequal.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.validate()
        """
        self.start.validate()
        self.end.validate()
        if self.start == self.end:
            raise ValueError('Segment is degenerate.')


def rotate_segment_around_origin(segment: Segment,
                                 cosine: Scalar,
                                 sine: Scalar) -> Segment:
    return Segment(rotate_point_around_origin(segment.start, cosine, sine),
                   rotate_point_around_origin(segment.end, cosine, sine))


def rotate_translate_segment(segment: Segment,
                             cosine: Scalar,
                             sine: Scalar,
                             step_x: Scalar,
                             step_y: Scalar) -> Segment:
    return Segment(rotate_translate_point(segment.start, cosine, sine, step_x,
                                          step_y),
                   rotate_translate_point(segment.end, cosine, sine, step_x,
                                          step_y))


def scale_segment(segment: Segment,
                  factor_x: Scalar,
                  factor_y: Scalar) -> Compound:
    return (Segment(scale_point(segment.start, factor_x, factor_y),
                    scale_point(segment.end, factor_x, factor_y))
            if ((factor_x or not segment.is_horizontal) and factor_y
                or factor_x and not segment.is_vertical)
            else Multipoint([scale_point(segment.start, factor_x, factor_y)]))
