from typing import Optional

from clipping.planar import (intersect_segments,
                             subtract_segments,
                             symmetric_subtract_segments,
                             unite_segments)
from ground.hints import Scalar
from orient.planar import (point_in_segment,
                           segment_in_segment)
from reprit.base import generate_repr

from .angle import Angle
from .compound import (Compound,
                       Linear,
                       Location,
                       Relation)
from .geometry import Geometry
from .iterable import non_negative_min
from .multipoint import Multipoint
from .packing import pack_mix
from .point import Point
from .utils import relate_multipoint_to_linear_compound


class Segment(Compound[Scalar], Linear[Scalar]):
    __slots__ = '_endpoints', '_end', '_start'

    def __init__(self,
                 start: Point[Scalar],
                 end: Point[Scalar]) -> None:
        """
        Initializes segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        """
        self._start, self._end = self._endpoints = start, end

    __repr__ = generate_repr(__init__)

    def __and__(self, other: Compound[Scalar]) -> Compound[Scalar]:
        """
        Returns intersection of the segment with the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Segment
        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment & segment == segment
        True
        """
        return (intersect_segments(self, other,
                                   context=self._context)
                if isinstance(other, Segment)
                else NotImplemented)

    __rand__ = __and__

    def __contains__(self, point: Point[Scalar]) -> bool:
        """
        Checks if the segment contains the point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Segment
        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.start in segment
        True
        >>> segment.end in segment
        True
        """
        return bool(self.locate(point))

    def __eq__(self, other: 'Segment[Scalar]') -> bool:
        """
        Checks if the segment is equal to the other.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Segment
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

    def __ge__(self, other: Compound[Scalar]) -> bool:
        """
        Checks if the segment is a superset of the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Segment
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
        return (other is self._context.empty
                or self == other
                or ((self.relate(other) is Relation.COMPONENT
                     if isinstance(other, (Multipoint, Segment))
                     # segment cannot be superset of contour or shaped
                     else False)
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __gt__(self, other: Compound[Scalar]) -> bool:
        """
        Checks if the segment is a strict superset of the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Segment
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
        return (other is self._context.empty
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

        >>> from gon.base import Point, Segment
        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> hash(segment) == hash(segment)
        True
        >>> hash(segment) == hash(Segment(Point(2, 0), Point(0, 0)))
        True
        """
        return hash(frozenset(self._endpoints))

    def __le__(self, other: Compound[Scalar]) -> bool:
        """
        Checks if the segment is a subset of the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Segment
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

    def __lt__(self, other: Compound[Scalar]) -> bool:
        """
        Checks if the segment is a strict subset of the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Segment
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

        >>> from gon.base import Point, Segment
        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment | segment == segment
        True
        """
        context = self._context
        return (pack_mix(other - self, self, context.empty, context.empty,
                         context.mix_cls)
                if isinstance(other, Multipoint)
                else (unite_segments(self, other,
                                     context=context)
                      if isinstance(other, Segment)
                      else NotImplemented))

    __ror__ = __or__

    def __sub__(self, other: Compound[Scalar]) -> Compound[Scalar]:
        """
        Returns difference of the segment with the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import EMPTY, Point, Segment
        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment - segment is EMPTY
        True
        """
        return (self
                if isinstance(other, Multipoint)
                else (subtract_segments(self, other,
                                        context=self._context)
                      if isinstance(other, Segment)
                      else NotImplemented))

    def __xor__(self, other: Compound[Scalar]) -> Compound[Scalar]:
        """
        Returns symmetric difference of the segment with the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import EMPTY, Point, Segment
        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment ^ segment is EMPTY
        True
        """
        context = self._context
        return (pack_mix(other - self, self, context.empty, context.empty,
                         context.mix_cls)
                if isinstance(other, Multipoint)
                else (symmetric_subtract_segments(self, other,
                                                  context=context)
                      if isinstance(other, Segment)
                      else NotImplemented))

    __rxor__ = __xor__

    @property
    def centroid(self) -> Point[Scalar]:
        """
        Returns centroid of the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Segment
        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.centroid == Point(1, 0)
        True
        """
        return self._context.segment_centroid(self)

    @property
    def end(self) -> Point[Scalar]:
        """
        Returns end of the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Segment
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

        >>> from gon.base import Point, Segment
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

        >>> from gon.base import Point, Segment
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

        >>> from gon.base import Point, Segment
        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.length == 2
        True
        """
        return self._context.segment_length(self)

    @property
    def start(self) -> Point[Scalar]:
        """
        Returns start of the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Segment
        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.start == Point(0, 0)
        True
        """
        return self._start

    def distance_to(self, other: Geometry[Scalar]) -> Scalar:
        """
        Returns distance between the segment and the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Segment
        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.distance_to(segment) == 0
        True
        """
        if isinstance(other, Point):
            return self._context.sqrt(
                    self._context.segment_point_squared_distance(self, other)
            )
        elif isinstance(other, Multipoint):
            return non_negative_min(
                    self._context.sqrt(
                            self._context.segment_point_squared_distance(
                                    self, point
                            ))
                    for point in other.points
            )
        elif isinstance(other, Segment):
            return self._context.sqrt(
                    self._context.segments_squared_distance(self, other)
            )
        else:
            return other.distance_to(self)

    def locate(self, point: Point[Scalar]) -> Location:
        """
        Finds location of the point relative to the segment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Segment
        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.locate(segment.start) is Location.BOUNDARY
        True
        >>> segment.locate(segment.end) is Location.BOUNDARY
        True
        """
        return point_in_segment(point, self,
                                context=self._context)

    def relate(self, other: Compound[Scalar]) -> Relation:
        """
        Finds relation between the segment and the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Segment
        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.relate(segment) is Relation.EQUAL
        True
        """
        return (relate_multipoint_to_linear_compound(other, self)
                if isinstance(other, Multipoint)
                else (segment_in_segment(other, self,
                                         context=self._context)
                      if isinstance(other, Segment)
                      else other.relate(self).complement))

    def rotate(self,
               angle: Angle,
               point: Optional[Point[Scalar]] = None) -> 'Segment[Scalar]':
        """
        Rotates the segment by given angle around given point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Angle, Point, Segment
        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.rotate(Angle(1, 0)) == segment
        True
        >>> (segment.rotate(Angle(0, 1), Point(1, 1))
        ...  == Segment(Point(2, 0), Point(2, 2)))
        True
        """
        return (self._context.rotate_segment_around_origin(self, angle.cosine,
                                                           angle.sine)
                if point is None
                else self._context.rotate_segment(self, angle.cosine,
                                                  angle.sine, point))

    def scale(self,
              factor_x: Scalar,
              factor_y: Optional[Scalar] = None) -> Compound[Scalar]:
        """
        Scales the segment by given factor.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Segment
        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.scale(1) == segment.scale(1, 2) == segment
        True
        """
        return self._context.scale_segment(
                self, factor_x, factor_x if factor_y is None else factor_y
        )

    def translate(self,
                  step_x: Scalar,
                  step_y: Scalar) -> 'Segment[Scalar]':
        """
        Translates the segment by given step.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Segment
        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.translate(1, 2) == Segment(Point(1, 2), Point(3, 2))
        True
        """
        return self._context.translate_segment(self, step_x, step_y)

    def validate(self) -> None:
        """
        Checks if endpoints are valid and unequal.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Segment
        >>> segment = Segment(Point(0, 0), Point(2, 0))
        >>> segment.validate()
        """
        self.start.validate()
        self.end.validate()
        if self.start == self.end:
            raise ValueError('Segment is degenerate.')
