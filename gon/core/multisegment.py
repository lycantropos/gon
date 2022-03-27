from functools import partial
from typing import (Optional,
                    Sequence)

from bentley_ottmann.planar import segments_cross_or_overlap
from clipping.planar import (complete_intersect_multisegments,
                             complete_intersect_segment_with_multisegment,
                             subtract_multisegment_from_segment,
                             subtract_multisegments,
                             subtract_segment_from_multisegment,
                             symmetric_subtract_multisegment_from_segment,
                             symmetric_subtract_multisegments,
                             unite_multisegments,
                             unite_segment_with_multisegment)
from ground.hints import Scalar
from locus import segmental
from orient.planar import (multisegment_in_multisegment,
                           point_in_multisegment,
                           segment_in_multisegment)
from reprit.base import generate_repr
from sect.decomposition import Graph

from .angle import Angle
from .compound import (Compound,
                       Indexable,
                       Linear,
                       Location,
                       Relation)
from .geometry import Geometry
from .iterable import non_negative_min
from .multipoint import Multipoint
from .packing import pack_mix
from .point import Point
from .segment import Segment
from .utils import (relate_multipoint_to_linear_compound,
                    to_point_nearest_segment,
                    to_segment_nearest_segment)

MIN_MULTISEGMENT_SEGMENTS_COUNT = 2


class Multisegment(Indexable[Scalar], Linear[Scalar]):
    __slots__ = ('_locate', '_point_nearest_segment',
                 '_segment_nearest_segment', '_segments', '_segments_set')

    def __init__(self, segments: Sequence[Segment]) -> None:
        """
        Initializes multisegment.

        Time complexity:
            ``O(segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(segments)``.
        """
        self._segments, self._segments_set = segments, frozenset(segments)
        context = self._context
        self._locate = partial(point_in_multisegment,
                               multisegment=self,
                               context=context)
        self._point_nearest_segment, self._segment_nearest_segment = (
            partial(to_point_nearest_segment, context, segments),
            partial(to_segment_nearest_segment, context, segments)
        )

    __repr__ = generate_repr(__init__)

    def __and__(self, other: Compound[Scalar]) -> Compound[Scalar]:
        """
        Returns intersection of the multisegment with the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment & multisegment == multisegment
        True
        """
        if isinstance(other, Segment):
            return complete_intersect_segment_with_multisegment(
                    other, self,
                    context=self._context
            )
        else:
            return (complete_intersect_multisegments(self, other,
                                                     context=self._context)
                    if isinstance(other, Multisegment)
                    else NotImplemented)

    __rand__ = __and__

    def __contains__(self, point: Point[Scalar]) -> bool:
        """
        Checks if the multisegment contains the point.

        Time complexity:
            ``O(log segments_count)`` expected after indexing,
            ``O(segments_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where ``segments_count = len(self.segments)``.

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> all(segment.start in multisegment and segment.end in multisegment
        ...     for segment in multisegment.segments)
        True
        """
        return bool(self.locate(point))

    def __eq__(self, other: 'Multisegment[Scalar]') -> bool:
        """
        Checks if multisegments are equal.

        Time complexity:
            ``O(len(self.segments))``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment == multisegment
        True
        >>> multisegment == Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                               Segment(Point(0, 1), Point(1, 1)),
        ...                               Segment(Point(0, 0), Point(1, 1))])
        False
        >>> multisegment == Multisegment([Segment(Point(0, 1), Point(1, 1)),
        ...                               Segment(Point(0, 0), Point(1, 0))])
        True
        """
        return self is other or (self._segments_set == other._segments_set
                                 if isinstance(other, Multisegment)
                                 else NotImplemented)

    def __ge__(self, other: Compound[Scalar]) -> bool:
        """
        Checks if the multisegment is a superset of the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment >= multisegment
        True
        >>> multisegment >= Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                               Segment(Point(0, 1), Point(1, 1)),
        ...                               Segment(Point(0, 0), Point(1, 1))])
        False
        >>> multisegment >= Multisegment([Segment(Point(0, 1), Point(1, 1)),
        ...                               Segment(Point(0, 0), Point(1, 0))])
        True
        """
        return (other is self._context.empty
                or self == other
                or ((self.relate(other) is Relation.COMPONENT
                     if isinstance(other, (Multipoint, Multisegment, Segment))
                     else (other <= self
                           if isinstance(other, Linear)
                           # multisegment cannot be superset of shaped
                           else False))
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __gt__(self, other: Compound[Scalar]) -> bool:
        """
        Checks if the multisegment is a strict superset of the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment > multisegment
        False
        >>> multisegment > Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1)),
        ...                              Segment(Point(0, 0), Point(1, 1))])
        False
        >>> multisegment > Multisegment([Segment(Point(0, 1), Point(1, 1)),
        ...                              Segment(Point(0, 0), Point(1, 0))])
        False
        """
        return (other is self._context.empty
                or self != other
                and ((self.relate(other) is Relation.COMPONENT
                      if isinstance(other, (Multipoint, Multisegment, Segment))
                      else (other < self
                            if isinstance(other, Linear)
                            # multisegment cannot be strict superset of shaped
                            else False))
                     if isinstance(other, Compound)
                     else NotImplemented))

    def __hash__(self) -> int:
        """
        Returns hash value of the multisegment.

        Time complexity:
            ``O(len(self.segments))``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> hash(multisegment) == hash(multisegment)
        True
        """
        return hash(self._segments_set)

    def __le__(self, other: Compound[Scalar]) -> bool:
        """
        Checks if the multisegment is a subset of the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment <= multisegment
        True
        >>> multisegment <= Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                               Segment(Point(0, 1), Point(1, 1)),
        ...                               Segment(Point(0, 0), Point(1, 1))])
        True
        >>> multisegment <= Multisegment([Segment(Point(0, 1), Point(1, 1)),
        ...                               Segment(Point(0, 0), Point(1, 0))])
        True
        """
        return (self == other
                or not isinstance(other, Multipoint)
                and (self.relate(other) in (Relation.EQUAL, Relation.COMPOSITE)
                     if isinstance(other, Linear)
                     else NotImplemented))

    def __lt__(self, other: Compound[Scalar]) -> bool:
        """
        Checks if the multisegment is a strict subset of the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment < multisegment
        False
        >>> multisegment < Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1)),
        ...                              Segment(Point(0, 0), Point(1, 1))])
        True
        >>> multisegment < Multisegment([Segment(Point(0, 1), Point(1, 1)),
        ...                              Segment(Point(0, 0), Point(1, 0))])
        False
        """
        return (self != other
                and not isinstance(other, Multipoint)
                and (self.relate(other) is Relation.COMPOSITE
                     if isinstance(other, Linear)
                     else NotImplemented))

    def __or__(self, other: Compound[Scalar]) -> Compound[Scalar]:
        """
        Returns union of the multisegment with the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment | multisegment == multisegment
        True
        """
        return (self._unite_with_multipoint(other)
                if isinstance(other, Multipoint)
                else (unite_segment_with_multisegment(other, self,
                                                      context=self._context)
                      if isinstance(other, Segment)
                      else (unite_multisegments(self, other,
                                                context=self._context)
                            if isinstance(other, Multisegment)
                            else NotImplemented)))

    __ror__ = __or__

    def __rsub__(self, other: Compound[Scalar]) -> Compound[Scalar]:
        """
        Returns difference of the other geometry with the multisegment.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.
        """
        return (subtract_multisegment_from_segment(other, self,
                                                   context=self._context)
                if isinstance(other, Segment)
                else NotImplemented)

    def __sub__(self, other: Compound[Scalar]) -> Compound[Scalar]:
        """
        Returns difference of the multisegment with the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> from gon.base import EMPTY, Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment - multisegment is EMPTY
        True
        """
        return (self
                if isinstance(other, Multipoint)
                else (subtract_segment_from_multisegment(self, other,
                                                         context=self._context)
                      if isinstance(other, Segment)
                      else (subtract_multisegments(self, other,
                                                   context=self._context)
                            if isinstance(other, Multisegment)
                            else NotImplemented)))

    def __xor__(self, other: Compound[Scalar]) -> Compound[Scalar]:
        """
        Returns symmetric difference of the multisegment
        with the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> from gon.base import EMPTY, Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment ^ multisegment is EMPTY
        True
        """
        if isinstance(other, Multipoint):
            return self._unite_with_multipoint(other)
        elif isinstance(other, Segment):
            return symmetric_subtract_multisegment_from_segment(
                    other, self,
                    context=self._context
            )
        else:
            return (symmetric_subtract_multisegments(self, other,
                                                     context=self._context)
                    if isinstance(other, Multisegment)
                    else NotImplemented)

    __rxor__ = __xor__

    @property
    def centroid(self) -> Point[Scalar]:
        """
        Returns centroid of the multisegment.

        Time complexity:
            ``O(len(self.segments))``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(2, 0)),
        ...                              Segment(Point(0, 2), Point(2, 2))])
        >>> multisegment.centroid == Point(1, 1)
        True
        """
        return self._context.multisegment_centroid(self)

    @property
    def length(self) -> Scalar:
        """
        Returns length of the multisegment.

        Time complexity:
            ``O(len(self.segments))``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment.length == 2
        True
        """
        return self._context.multisegment_length(self)

    @property
    def segments(self) -> Sequence[Segment[Scalar]]:
        """
        Returns segments of the multisegment.

        Time complexity:
            ``O(segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment.segments == [Segment(Point(0, 0), Point(1, 0)),
        ...                           Segment(Point(0, 1), Point(1, 1))]
        True
        """
        return list(self._segments)

    def distance_to(self, other: Geometry[Scalar]) -> Scalar:
        """
        Returns distance between the multisegment and the other geometry.

        Time complexity:
            ``O(len(self.segments))``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment.distance_to(multisegment) == 0
        True
        """
        return (self._distance_to_point(other)
                if isinstance(other, Point)
                else
                (non_negative_min(self._distance_to_point(point)
                                  for point in other.points)
                 if isinstance(other, Multipoint)
                 else
                 (self._distance_to_segment(other)
                  if isinstance(other, Segment)
                  else (non_negative_min(self._distance_to_segment(segment)
                                         for segment in other.segments)
                        if isinstance(other, Multisegment)
                        else other.distance_to(self)))))

    def index(self) -> None:
        """
        Pre-processes the multisegment to potentially improve queries.

        Time complexity:
            ``O(segments_count * log segments_count)`` expected,
            ``O(segments_count ** 2)`` worst
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment.index()
        """
        self._locate = Graph.from_multisegment(self,
                                               context=self._context).locate
        tree = segmental.Tree(self.segments)
        self._point_nearest_segment = tree.nearest_to_point_segment
        self._segment_nearest_segment = tree.nearest_segment

    def locate(self, point: Point[Scalar]) -> Location:
        """
        Finds location of the point relative to the multisegment.

        Time complexity:
            ``O(log segments_count)`` expected after indexing,
            ``O(segments_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where ``segments_count = len(self.segments)``.

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> all(multisegment.locate(segment.start)
        ...     is multisegment.locate(segment.end)
        ...     is Location.BOUNDARY
        ...     for segment in multisegment.segments)
        True
        """
        return self._locate(point)

    def relate(self, other: Compound[Scalar]) -> Relation:
        """
        Finds relation between the multisegment and the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment.relate(multisegment) is Relation.EQUAL
        True
        """
        return (relate_multipoint_to_linear_compound(other, self)
                if isinstance(other, Multipoint)
                else (segment_in_multisegment(other, self)
                      if isinstance(other, Segment)
                      else (multisegment_in_multisegment(other, self)
                            if isinstance(other, Multisegment)
                            else other.relate(self).complement)))

    def rotate(self,
               angle: Angle,
               point: Optional[Point[Scalar]] = None
               ) -> 'Multisegment[Scalar]':
        """
        Rotates the multisegment by given angle around given point.

        Time complexity:
            ``O(segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> from gon.base import Angle, Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment.rotate(Angle(1, 0)) == multisegment
        True
        >>> (multisegment.rotate(Angle(0, 1), Point(1, 1))
        ...  == Multisegment([Segment(Point(2, 0), Point(2, 1)),
        ...                   Segment(Point(1, 0), Point(1, 1))]))
        True
        """
        if point is None:
            return self._context.rotate_multisegment_around_origin(
                    self, angle.cosine, angle.sine
            )
        else:
            return self._context.rotate_multisegment(self, angle.cosine,
                                                     angle.sine, point)

    def scale(self,
              factor_x: Scalar,
              factor_y: Optional[Scalar] = None) -> Compound[Scalar]:
        """
        Scales the multisegment by given factor.

        Time complexity:
            ``O(segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment.scale(1) == multisegment
        True
        >>> (multisegment.scale(1, 2)
        ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                   Segment(Point(0, 2), Point(1, 2))]))
        True
        """
        return self._context.scale_multisegment(
                self, factor_x, factor_x if factor_y is None else factor_y
        )

    def translate(self,
                  step_x: Scalar,
                  step_y: Scalar) -> 'Multisegment[Scalar]':
        """
        Translates the multisegment by given step.

        Time complexity:
            ``O(segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> (multisegment.translate(1, 2)
        ...  == Multisegment([Segment(Point(1, 2), Point(2, 2)),
        ...                   Segment(Point(1, 3), Point(2, 3))]))
        True
        """
        return self._context.translate_multisegment(self, step_x, step_y)

    def validate(self) -> None:
        """
        Checks if the multisegment is valid.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> from gon.base import Multisegment, Point, Segment
        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment.validate()
        """
        segments = self.segments
        if len(segments) < MIN_MULTISEGMENT_SEGMENTS_COUNT:
            raise ValueError('Multisegment should have '
                             'at least {min_size} segments, '
                             'but found {size}.'
                             .format(min_size=MIN_MULTISEGMENT_SEGMENTS_COUNT,
                                     size=len(segments)))
        elif len(segments) > len(self._segments_set):
            raise ValueError('Duplicate segments found.')
        for segment in segments:
            segment.validate()
        if segments_cross_or_overlap(segments,
                                     context=self._context):
            raise ValueError('Crossing or overlapping segments found.')

    def _distance_to_point(self, other: Point[Scalar]) -> Scalar:
        return self._context.sqrt(self._context.segment_point_squared_distance(
                self._point_nearest_segment(other), other
        ))

    def _distance_to_segment(self, other: Segment[Scalar]) -> Scalar:
        return self._context.sqrt(self._context.segments_squared_distance(
                self._segment_nearest_segment(other), other
        ))

    def _unite_with_multipoint(self, other: Multipoint[Scalar]
                               ) -> Compound[Scalar]:
        return pack_mix(other - self, self, self._context.empty,
                        self._context.empty, self._context.mix_cls)
