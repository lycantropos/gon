from functools import partial
from typing import (Iterable,
                    List,
                    Optional,
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
from ground.base import (Context,
                         get_context)
from locus import segmental
from orient.planar import (multisegment_in_multisegment,
                           point_in_multisegment,
                           segment_in_multisegment)
from reprit.base import generate_repr
from sect.decomposition import Graph

from .compound import (Compound,
                       Indexable,
                       Linear,
                       Location,
                       Relation)
from .empty import EMPTY
from .geometry import Geometry
from .hints import Scalar
from .iterable import (non_negative_min,
                       unique_ever_seen)
from .mix import from_mix_components
from .multipoint import (Multipoint,
                         pack_points)
from .point import (Point,
                    point_to_step,
                    scale_point)
from .segment import (Segment,
                      rotate_segment_around_origin,
                      rotate_translate_segment,
                      scale_segment)
from .utils import (relate_multipoint_to_linear_compound,
                    to_point_nearest_segment,
                    to_segment_nearest_segment)

MIN_MULTISEGMENT_SEGMENTS_COUNT = 2


class Multisegment(Indexable, Linear):
    __slots__ = ('_context', '_locate', '_point_nearest_segment',
                 '_segment_nearest_segment', '_segments', '_segments_set')

    def __init__(self, segments: Sequence[Segment],
                 *,
                 context: Optional[Context] = None) -> None:
        """
        Initializes multisegment.

        Time complexity:
            ``O(segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(segments)``.
        """
        if context is None:
            context = get_context()
        self._context = context
        self._segments, self._segments_set = segments, frozenset(segments)
        self._locate = partial(locate_point, self)
        self._point_nearest_segment, self._segment_nearest_segment = (
            partial(to_point_nearest_segment, context, segments),
            partial(to_segment_nearest_segment, context, segments))

    __repr__ = generate_repr(__init__)

    def __and__(self, other: Compound) -> Compound:
        """
        Returns intersection of the multisegment with the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment & multisegment == multisegment
        True
        """
        return (complete_intersect_segment_with_multisegment(
                other, self,
                context=self.context)
                if isinstance(other, Segment)
                else (complete_intersect_multisegments(self, other,
                                                       context=self.context)
                      if isinstance(other, Multisegment)
                      else NotImplemented))

    __rand__ = __and__

    def __contains__(self, point: Point) -> bool:
        """
        Checks if the multisegment contains the point.

        Time complexity:
            ``O(log segments_count)`` expected after indexing,
            ``O(segments_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> all(segment.start in multisegment and segment.end in multisegment
        ...     for segment in multisegment.segments)
        True
        """
        return bool(self.locate(point))

    def __eq__(self, other: 'Multisegment') -> bool:
        """
        Checks if multisegments are equal.

        Time complexity:
            ``O(len(self.segments))``
        Memory complexity:
            ``O(1)``

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

    def __ge__(self, other: Compound) -> bool:
        """
        Checks if the multisegment is a superset of the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

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
        return (other is EMPTY
                or self == other
                or ((self.relate(other) is Relation.COMPONENT
                     if isinstance(other, (Multipoint, Multisegment, Segment))
                     else (other <= self
                           if isinstance(other, Linear)
                           # multisegment cannot be superset of shaped
                           else False))
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __gt__(self, other: Compound) -> bool:
        """
        Checks if the multisegment is a strict superset of the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

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
        return (other is EMPTY
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

        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> hash(multisegment) == hash(multisegment)
        True
        """
        return hash(self._segments_set)

    def __le__(self, other: Compound) -> bool:
        """
        Checks if the multisegment is a subset of the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

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

    def __lt__(self, other: Compound) -> bool:
        """
        Checks if the multisegment is a strict subset of the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

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

    def __or__(self, other: Compound) -> Compound:
        """
        Returns union of the multisegment with the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment | multisegment == multisegment
        True
        """
        return (self._unite_with_multipoint(other)
                if isinstance(other, Multipoint)
                else (unite_segment_with_multisegment(other, self,
                                                      context=self.context)
                      if isinstance(other, Segment)
                      else (unite_multisegments(self, other,
                                                context=self.context)
                            if isinstance(other, Multisegment)
                            else NotImplemented)))

    __ror__ = __or__

    def __rsub__(self, other: Compound) -> Compound:
        """
        Returns difference of the other geometry with the multisegment.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.
        """
        return (subtract_multisegment_from_segment(other, self,
                                                   context=self.context)
                if isinstance(other, Segment)
                else NotImplemented)

    def __sub__(self, other: Compound) -> Compound:
        """
        Returns difference of the multisegment with the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment - multisegment is EMPTY
        True
        """
        return (self
                if isinstance(other, Multipoint)
                else (subtract_segment_from_multisegment(self, other,
                                                         context=self.context)
                      if isinstance(other, Segment)
                      else (subtract_multisegments(self, other,
                                                   context=self.context)
                            if isinstance(other, Multisegment)
                            else NotImplemented)))

    def __xor__(self, other: Compound) -> Compound:
        """
        Returns symmetric difference of the multisegment
        with the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment ^ multisegment is EMPTY
        True
        """
        return (self._unite_with_multipoint(other)
                if isinstance(other, Multipoint)
                else
                (symmetric_subtract_multisegment_from_segment(
                        other, self,
                        context=self.context)
                 if isinstance(other, Segment)
                 else (symmetric_subtract_multisegments(self, other,
                                                        context=self.context)
                       if isinstance(other, Multisegment)
                       else NotImplemented)))

    __rxor__ = __xor__

    @property
    def centroid(self) -> Point:
        """
        Returns centroid of the multisegment.

        Time complexity:
            ``O(len(self.segments))``
        Memory complexity:
            ``O(1)``

        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(2, 0)),
        ...                              Segment(Point(0, 2), Point(2, 2))])
        >>> multisegment.centroid == Point(1, 1)
        True
        """
        return self.context.multisegment_centroid(self)

    @property
    def context(self) -> Context:
        """
        Returns context of the multisegment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(2, 0)),
        ...                              Segment(Point(0, 2), Point(2, 2))])
        >>> isinstance(multisegment.context, Context)
        True
        """
        return self._context

    @property
    def length(self) -> Scalar:
        """
        Returns length of the multisegment.

        Time complexity:
            ``O(len(self.segments))``
        Memory complexity:
            ``O(1)``

        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment.length == 2
        True
        """
        return sum(segment.length for segment in self._segments)

    @property
    def segments(self) -> List[Segment]:
        """
        Returns segments of the multisegment.

        Time complexity:
            ``O(segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment.segments == [Segment(Point(0, 0), Point(1, 0)),
        ...                           Segment(Point(0, 1), Point(1, 1))]
        True
        """
        return list(self._segments)

    def distance_to(self, other: Geometry) -> Scalar:
        """
        Returns distance between the multisegment and the other geometry.

        Time complexity:
            ``O(len(self.segments))``
        Memory complexity:
            ``O(1)``

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

        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment.index()
        """
        if len(self._segments) > 1:
            self._locate = Graph.from_multisegment(self,
                                                   context=self.context).locate
            tree = segmental.Tree(self._segments)
            self._point_nearest_segment = tree.nearest_to_point_segment
            self._segment_nearest_segment = tree.nearest_segment

    def locate(self, point: Point) -> Location:
        """
        Finds location of the point relative to the multisegment.

        Time complexity:
            ``O(log segments_count)`` expected after indexing,
            ``O(segments_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> all(multisegment.locate(segment.start)
        ...     is multisegment.locate(segment.end)
        ...     is Location.BOUNDARY
        ...     for segment in multisegment.segments)
        True
        """
        return self._locate(point)

    def relate(self, other: Compound) -> Relation:
        """
        Finds relation between the multisegment and the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

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
               cosine: Scalar,
               sine: Scalar,
               point: Optional[Point] = None) -> 'Multisegment':
        """
        Rotates the multisegment by given cosine & sine around given point.

        Time complexity:
            ``O(segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment.rotate(1, 0) == multisegment
        True
        >>> (multisegment.rotate(0, 1, Point(1, 1))
        ...  == Multisegment([Segment(Point(2, 0), Point(2, 1)),
        ...                   Segment(Point(1, 0), Point(1, 1))]))
        True
        """
        return (Multisegment([rotate_segment_around_origin(segment, cosine,
                                                           sine)
                              for segment in self._segments])
                if point is None
                else Multisegment(
                [rotate_translate_segment(segment, cosine, sine,
                                          *point_to_step(point, cosine, sine))
                 for segment in self._segments]))

    def scale(self,
              factor_x: Scalar,
              factor_y: Optional[Scalar] = None) -> Compound:
        """
        Scales the multisegment by given factor.

        Time complexity:
            ``O(segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment.scale(1) == multisegment
        True
        >>> (multisegment.scale(1, 2)
        ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                   Segment(Point(0, 2), Point(1, 2))]))
        True
        """
        if factor_y is None:
            factor_y = factor_x
        return (Multisegment([scale_segment(segment, factor_x, factor_y)
                              for segment in self._segments])
                if factor_x and factor_y
                else (_scale_segments(self._segments, factor_x, factor_y)
                      if factor_x or factor_y
                      else Multipoint([Point(factor_x, factor_y)])))

    def translate(self,
                  step_x: Scalar,
                  step_y: Scalar) -> 'Multisegment':
        """
        Translates the multisegment by given step.

        Time complexity:
            ``O(segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> (multisegment.translate(1, 2)
        ...  == Multisegment([Segment(Point(1, 2), Point(2, 2)),
        ...                   Segment(Point(1, 3), Point(2, 3))]))
        True
        """
        return Multisegment([segment.translate(step_x, step_y)
                             for segment in self._segments])

    def validate(self) -> None:
        """
        Checks if the multisegment is valid.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1))])
        >>> multisegment.validate()
        """
        segments = self._segments
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
        if segments_cross_or_overlap(segments):
            raise ValueError('Crossing or overlapping segments found.')

    def _distance_to_point(self, other: Point) -> Scalar:
        return self.context.sqrt(self.context.segment_point_squared_distance(
                self._point_nearest_segment(other), other))

    def _distance_to_segment(self, other: Segment) -> Scalar:
        return self.context.sqrt(self.context.segments_squared_distance(
                self._segment_nearest_segment(other), other))

    def _unite_with_multipoint(self, other: Multipoint) -> Compound:
        return from_mix_components(other - self, self, EMPTY)


def locate_point(multisegment: Multisegment, point: Point) -> Location:
    return (Location.EXTERIOR
            if point_in_multisegment(point, multisegment) is Relation.DISJOINT
            else Location.BOUNDARY)


def _scale_segments(segments: Iterable[Segment],
                    factor_x: Scalar,
                    factor_y: Scalar) -> Compound:
    scaled_points, scaled_segments = [], []
    for segment in segments:
        if ((factor_x or not segment.is_horizontal) and factor_y
                or factor_x and not segment.is_vertical):
            scaled_segments.append(segment.scale(factor_x, factor_y))
        else:
            scaled_points.append(scale_point(segment.start, factor_x,
                                             factor_y))
    return (pack_points(unique_ever_seen(scaled_points))
            | Multisegment(scaled_segments))
