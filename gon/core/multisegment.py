from functools import partial
from typing import (Iterable,
                    List,
                    Optional,
                    Sequence)

from bentley_ottmann.planar import segments_cross_or_overlap
from clipping.planar import (complete_intersect_multisegments,
                             subtract_multisegments,
                             symmetric_subtract_multisegments,
                             unite_multisegments)
from ground.base import (Context,
                         get_context)
from locus import segmental
from orient.planar import (multisegment_in_multisegment,
                           point_in_multisegment,
                           segment_in_multisegment)
from reprit.base import generate_repr
from sect.decomposition import Graph
from symba.base import Expression

from .arithmetic import non_negative_min
from .compound import (Compound,
                       Indexable,
                       Linear,
                       Location,
                       Relation)
from .degenerate import EMPTY
from .geometry import Geometry
from .hints import Coordinate
from .iterable import unique_ever_seen
from .linear_utils import (from_mix_components,
                           relate_multipoint_to_linear_compound,
                           to_point_nearest_segment,
                           to_segment_nearest_segment,
                           unfold_multisegment)
from .multipoint import (Multipoint,
                         from_points)
from .point import (Point,
                    point_to_step,
                    scale_point)
from .raw import RawMultisegment
from .segment import (Segment,
                      rotate_segment_around_origin,
                      rotate_translate_segment,
                      scale_segment)


class Multisegment(Indexable, Linear):
    __slots__ = ('_context', '_segments', '_segments_set', '_raw',
                 '_locate', '_point_nearest_segment',
                 '_segment_nearest_segment')

    def __init__(self, segments: Sequence[Segment]) -> None:
        """
        Initializes multisegment.

        Time complexity:
            ``O(segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(segments)``.
        """
        context = get_context()
        self._context = context
        self._segments = segments
        self._raw = [segment.raw() for segment in segments]
        self._segments_set = frozenset(segments)
        self._locate = partial(locate_point, self)
        self._segment_nearest_segment = partial(to_segment_nearest_segment,
                                                segments,
                                                context=context)
        self._point_nearest_segment = partial(to_point_nearest_segment,
                                              segments,
                                              context=context)

    __repr__ = generate_repr(__init__)

    def __and__(self, other: Compound) -> Compound:
        """
        Returns intersection of the multisegment with the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> multisegment & multisegment == multisegment
        True
        """
        return (self._intersect_with_multisegment(
                self.context.multisegment_cls([other]))
                if isinstance(other, Segment)
                else (self._intersect_with_multisegment(other)
                      if isinstance(other, Multisegment)
                      else NotImplemented))

    __rand__ = __and__

    def __contains__(self, other: Geometry) -> bool:
        """
        Checks if the multisegment contains the other geometry.

        Time complexity:
            ``O(log segments_count)`` expected after indexing,
            ``O(segments_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> all(segment.start in multisegment and segment.end in multisegment
        ...     for segment in multisegment.segments)
        True
        """
        return isinstance(other, Point) and bool(self._locate(other))

    def __eq__(self, other: 'Multisegment') -> bool:
        """
        Checks if multisegments are equal.

        Time complexity:
            ``O(len(self.segments))``
        Memory complexity:
            ``O(1)``

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> multisegment == multisegment
        True
        >>> multisegment == Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                        ((0, 1), (1, 1)),
        ...                                        ((0, 0), (1, 1))])
        False
        >>> multisegment == Multisegment.from_raw([((0, 1), (1, 1)),
        ...                                        ((0, 0), (1, 0))])
        True
        """
        return (self is other
                or (self._segments_set == other._segments_set
                    if isinstance(other, Multisegment)
                    else (False
                          if isinstance(other, Geometry)
                          else NotImplemented)))

    def __ge__(self, other: Compound) -> bool:
        """
        Checks if the multisegment is a superset of the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> multisegment >= multisegment
        True
        >>> multisegment >= Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                        ((0, 1), (1, 1)),
        ...                                        ((0, 0), (1, 1))])
        False
        >>> multisegment >= Multisegment.from_raw([((0, 1), (1, 1)),
        ...                                        ((0, 0), (1, 0))])
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

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> multisegment > multisegment
        False
        >>> multisegment > Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1)),
        ...                                       ((0, 0), (1, 1))])
        False
        >>> multisegment > Multisegment.from_raw([((0, 1), (1, 1)),
        ...                                       ((0, 0), (1, 0))])
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

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
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

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> multisegment <= multisegment
        True
        >>> multisegment <= Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                        ((0, 1), (1, 1)),
        ...                                        ((0, 0), (1, 1))])
        True
        >>> multisegment <= Multisegment.from_raw([((0, 1), (1, 1)),
        ...                                        ((0, 0), (1, 0))])
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

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> multisegment < multisegment
        False
        >>> multisegment < Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1)),
        ...                                       ((0, 0), (1, 1))])
        True
        >>> multisegment < Multisegment.from_raw([((0, 1), (1, 1)),
        ...                                       ((0, 0), (1, 0))])
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

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> multisegment | multisegment == multisegment
        True
        """
        return (self._unite_with_multipoint(other)
                if isinstance(other, Multipoint)
                else
                (self._unite_with_multisegment(
                        self.context.multisegment_cls([other]))
                 if isinstance(other, Segment)
                 else (self._unite_with_multisegment(other)
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
        return (self._subtract_from_multisegment(
                self.context.multisegment_cls([other]))
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

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> multisegment - multisegment is EMPTY
        True
        """
        return (self
                if isinstance(other, Multipoint)
                else
                (self._subtract_multisegment(
                        self.context.multisegment_cls([other]))
                 if isinstance(other, Segment)
                 else (self._subtract_multisegment(other)
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

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> multisegment ^ multisegment is EMPTY
        True
        """
        return (self._unite_with_multipoint(other)
                if isinstance(other, Multipoint)
                else
                (self._symmetric_subtract_multisegment(
                        self.context.multisegment_cls([other]))
                 if isinstance(other, Segment)
                 else (self._symmetric_subtract_multisegment(other)
                       if isinstance(other, Multisegment)
                       else NotImplemented)))

    __rxor__ = __xor__

    @classmethod
    def from_raw(cls, raw: RawMultisegment) -> 'Multisegment':
        """
        Constructs multisegment from the combination of Python built-ins.

        Time complexity:
            ``O(raw_segments_count)``
        Memory complexity:
            ``O(raw_segments_count)``

        where ``raw_segments_count = len(raw)``.

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> multisegment == Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                               Segment(Point(0, 1), Point(1, 1))])
        True
        """
        return Multisegment([Segment.from_raw(raw_segment)
                             for raw_segment in raw])

    @property
    def centroid(self) -> Point:
        """
        Returns centroid of the multisegment.

        Time complexity:
            ``O(len(self.segments))``
        Memory complexity:
            ``O(1)``

        >>> multisegment = Multisegment.from_raw([((0, 0), (2, 0)),
        ...                                       ((0, 2), (2, 2))])
        >>> multisegment.centroid == Point(1, 1)
        True
        """
        return self.context.multisegment_centroid(self.segments)

    @property
    def context(self) -> Context:
        """
        Returns context of the multisegment.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> multisegment = Multisegment.from_raw([((0, 0), (2, 0)),
        ...                                       ((0, 2), (2, 2))])
        >>> isinstance(multisegment.context, Context)
        True
        """
        return self._context

    @property
    def length(self) -> Expression:
        """
        Returns length of the multisegment.

        Time complexity:
            ``O(len(self.segments))``
        Memory complexity:
            ``O(1)``

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
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

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> multisegment.segments
        [Segment(Point(0, 0), Point(1, 0)), Segment(Point(0, 1), Point(1, 1))]
        """
        return list(self._segments)

    def distance_to(self, other: Geometry) -> Coordinate:
        """
        Returns distance between the multisegment and the other geometry.

        Time complexity:
            ``O(len(self.segments))``
        Memory complexity:
            ``O(1)``

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
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

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
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

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> all(multisegment.locate(segment.start)
        ...     is multisegment.locate(segment.end)
        ...     is Location.BOUNDARY
        ...     for segment in multisegment.segments)
        True
        """
        return self._locate(point)

    def raw(self) -> RawMultisegment:
        """
        Returns the multisegment as combination of Python built-ins.

        Time complexity:
            ``O(segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> multisegment.raw()
        [((0, 0), (1, 0)), ((0, 1), (1, 1))]
        """
        return self._raw[:]

    def relate(self, other: Compound) -> Relation:
        """
        Finds relation between the multisegment and the other geometry.

        Time complexity:
            ``O(segments_count * log segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
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
               cosine: Coordinate,
               sine: Coordinate,
               point: Optional[Point] = None) -> 'Multisegment':
        """
        Rotates the multisegment by given cosine & sine around given point.

        Time complexity:
            ``O(segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> multisegment.rotate(1, 0) == multisegment
        True
        >>> (multisegment.rotate(0, 1, Point(1, 1))
        ...  == Multisegment.from_raw([((2, 0), (2, 1)), ((1, 0), (1, 1))]))
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
              factor_x: Coordinate,
              factor_y: Optional[Coordinate] = None) -> Compound:
        """
        Scales the multisegment by given factor.

        Time complexity:
            ``O(segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> multisegment.scale(1) == multisegment
        True
        >>> (multisegment.scale(1, 2)
        ...  == Multisegment.from_raw([((0, 0), (1, 0)), ((0, 2), (1, 2))]))
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
                  step_x: Coordinate,
                  step_y: Coordinate) -> 'Multisegment':
        """
        Translates the multisegment by given step.

        Time complexity:
            ``O(segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(self.segments)``.

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> (multisegment.translate(1, 2)
        ...  == Multisegment.from_raw([((1, 2), (2, 2)), ((1, 3), (2, 3))]))
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

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> multisegment.validate()
        """
        if not self._segments:
            raise ValueError('Multisegment is empty.')
        elif len(self.segments) > len(self._segments_set):
            raise ValueError('Duplicate segments found.')
        for segment in self._segments:
            segment.validate()
        if segments_cross_or_overlap(self._segments):
            raise ValueError('Crossing or overlapping segments found.')

    def _distance_to_point(self, other: Point) -> Coordinate:
        nearest_segment = self._point_nearest_segment(other)
        return self.context.sqrt(self.context.segment_point_squared_distance(
                nearest_segment.start, nearest_segment.end, other))

    def _distance_to_segment(self, other: Segment) -> Coordinate:
        nearest_segment = self._segment_nearest_segment(other)
        return self.context.sqrt(self.context.segments_squared_distance(
                nearest_segment.start, nearest_segment.end, other.start,
                other.end))

    def _intersect_with_multisegment(self, other: 'Multisegment') -> Compound:
        multipoint, multisegment = complete_intersect_multisegments(self,
                                                                    other)
        return from_mix_components(multipoint, multisegment)

    def _subtract_multisegment(self, other: 'Multisegment') -> Compound:
        return unfold_multisegment(subtract_multisegments(self, other))

    def _subtract_from_multisegment(self, other: 'Multisegment') -> Compound:
        return unfold_multisegment(subtract_multisegments(other, self))

    def _symmetric_subtract_multisegment(self, other: 'Multisegment'
                                         ) -> Compound:
        return unfold_multisegment(symmetric_subtract_multisegments(
                self, other,
                context=self.context))

    def _unite_with_multipoint(self, other: Multipoint) -> Compound:
        # importing here to avoid cyclic imports
        from gon.core.mix import from_mix_components
        return from_mix_components(other - self, self, EMPTY)

    def _unite_with_multisegment(self, other: 'Multisegment') -> Compound:
        return unite_multisegments(self, other)


def locate_point(multisegment: Multisegment, point: Point) -> Location:
    return (Location.EXTERIOR
            if point_in_multisegment(point, multisegment) is Relation.DISJOINT
            else Location.BOUNDARY)


def _scale_segments(segments: Iterable[Segment],
                    factor_x: Coordinate,
                    factor_y: Coordinate) -> Compound:
    scaled_points, scaled_segments = [], []
    for segment in segments:
        if ((factor_x or not segment.is_horizontal) and factor_y
                or factor_x and not segment.is_vertical):
            scaled_segments.append(segment.scale(factor_x, factor_y))
        else:
            scaled_points.append(scale_point(segment.start, factor_x,
                                             factor_y))
    return (from_points(unique_ever_seen(scaled_points))
            | Multisegment(scaled_segments))
