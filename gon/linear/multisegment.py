from functools import partial
from math import inf
from typing import (Iterable,
                    List,
                    Optional)

from bentley_ottmann.planar import segments_cross_or_overlap
from clipping.planar import (complete_intersect_multisegments,
                             segments_to_multisegment,
                             subtract_multisegments,
                             symmetric_subtract_multisegments,
                             unite_multisegments)
from locus import segmental
from orient.planar import (multisegment_in_multisegment,
                           point_in_multisegment,
                           segment_in_multisegment)
from reprit.base import generate_repr
from sect.decomposition import multisegment_trapezoidal

from gon.compound import (Compound,
                          Indexable,
                          Linear,
                          Location,
                          Relation)
from gon.core.arithmetic import (non_negative_min,
                                 robust_divide,
                                 robust_sqrt)
from gon.core.iterable import unique_ever_seen
from gon.degenerate import EMPTY
from gon.discrete import Multipoint
from gon.discrete.multipoint import from_points
from gon.geometry import Geometry
from gon.hints import Coordinate
from gon.primitive import (Point,
                           RawPoint)
from gon.primitive.point import (point_to_step,
                                 scale_point)
from gon.primitive.raw import scale_raw_point
from .hints import (RawMultisegment,
                    RawSegment)
from .raw import (raw_segment_point_distance,
                  squared_raw_interval_point_distance,
                  squared_raw_point_segment_distance,
                  squared_raw_segment_interval_distance,
                  squared_raw_segments_distance)
from .segment import (Segment,
                      rotate_segment_around_origin,
                      rotate_translate_segment,
                      scale_segment)
from .utils import (from_raw_mix_components,
                    from_raw_multisegment,
                    relate_multipoint_to_linear_compound)


class Multisegment(Indexable, Linear):
    __slots__ = ('_segments', '_segments_set', '_raw', '_raw_locate',
                 '_raw_point_nearest_index', '_raw_segment_nearest_index')

    def __init__(self, *segments: Segment) -> None:
        """
        Initializes multisegment.

        Time complexity:
            ``O(segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(segments)``.
        """
        self._segments = segments
        self._raw = [segment.raw() for segment in segments]
        self._segments_set = frozenset(segments)
        self._raw_locate = partial(raw_locate_point, self._raw)
        self._raw_segment_nearest_index = partial(
                _to_raw_segment_nearest_index, self._raw)
        self._raw_point_nearest_index = partial(_to_raw_point_nearest_index,
                                                self._raw)

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
        return (self._intersect_with_raw_multisegment([other.raw()])
                if isinstance(other, Segment)
                else (self._intersect_with_raw_multisegment(other._raw)
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
        return isinstance(other, Point) and bool(self._raw_locate(other.raw()))

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
                else (self._unite_with_raw_multisegment([other.raw()])
                      if isinstance(other, Segment)
                      else (self._unite_with_raw_multisegment(other._raw)
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
        return (self._subtract_from_raw_multisegment([other.raw()])
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
                else (self._subtract_raw_multisegment([other.raw()])
                      if isinstance(other, Segment)
                      else (self._subtract_raw_multisegment(other._raw)
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
                else (self._symmetric_subtract_raw_multisegment([other.raw()])
                      if isinstance(other, Segment)
                      else
                      (self._symmetric_subtract_raw_multisegment(other._raw)
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
        >>> multisegment == Multisegment(Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1)))
        True
        """
        return Multisegment(*map(Segment.from_raw, raw))

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
        accumulated_x = accumulated_y = accumulated_length = 0
        for (start_x, start_y), (end_x, end_y) in self._raw:
            length = robust_sqrt((end_x - start_x) ** 2
                                 + (end_y - start_y) ** 2)
            accumulated_x += (start_x + end_x) * length
            accumulated_y += (start_y + end_y) * length
            accumulated_length += length
        divisor = 2 * accumulated_length
        return Point(robust_divide(accumulated_x, divisor),
                     robust_divide(accumulated_y, divisor))

    @property
    def length(self) -> Coordinate:
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
        return (self._distance_to_raw_point(other.raw())
                if isinstance(other, Point)
                else
                (non_negative_min(self._distance_to_raw_point(raw_point)
                                  for raw_point in other._raw)
                 if isinstance(other, Multipoint)
                 else
                 (self._distance_to_raw_segment(other._raw)
                  if isinstance(other, Segment)
                  else
                  (non_negative_min(self._distance_to_raw_segment(raw_segment)
                                    for raw_segment in other._raw)
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
            raw_segments = self._raw
            graph = multisegment_trapezoidal(raw_segments)
            self._raw_locate = graph.locate
            tree = segmental.Tree(raw_segments,
                                  node_cls=SegmentalSquaredDistanceNode)
            self._raw_point_nearest_index = tree.nearest_to_point_index
            self._raw_segment_nearest_index = tree.nearest_index

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
        return self._raw_locate(point.raw())

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
                else (segment_in_multisegment(other.raw(), self._raw)
                      if isinstance(other, Segment)
                      else (multisegment_in_multisegment(other._raw, self._raw)
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
        return (Multisegment(*[rotate_segment_around_origin(segment, cosine,
                                                            sine)
                               for segment in self._segments])
                if point is None
                else Multisegment(
                *[rotate_translate_segment(segment, cosine, sine,
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
        return (Multisegment(*[scale_segment(segment, factor_x, factor_y)
                               for segment in self._segments])
                if factor_x and factor_y
                else (_scale_segments(self._segments, factor_x, factor_y)
                      if factor_x or factor_y
                      else Multipoint(Point(factor_x, factor_y))))

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
        return Multisegment(*[segment.translate(step_x, step_y)
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
        elif len(self._segments) > len(self._segments_set):
            raise ValueError('Duplicate segments found.')
        for segment in self._segments:
            segment.validate()
        if segments_cross_or_overlap(self._raw):
            raise ValueError('Crossing or overlapping segments found.')

    def _distance_to_raw_point(self, other: RawPoint) -> Coordinate:
        return raw_segment_point_distance(
                self._raw[self._raw_point_nearest_index(other)], other)

    def _distance_to_raw_segment(self, other: RawSegment) -> Coordinate:
        return robust_sqrt(squared_raw_segments_distance(
                self._raw[self._raw_segment_nearest_index(other)], other))

    def _intersect_with_raw_multisegment(self, other_raw: RawMultisegment
                                         ) -> Compound:
        raw_multipoint, raw_multisegment, _ = complete_intersect_multisegments(
                self._raw, other_raw,
                accurate=False)
        return from_raw_mix_components(raw_multipoint, raw_multisegment)

    def _subtract_raw_multisegment(self, other_raw: RawMultisegment
                                   ) -> Compound:
        return from_raw_multisegment(subtract_multisegments(self._raw,
                                                            other_raw,
                                                            accurate=False))

    def _subtract_from_raw_multisegment(self, other_raw: RawMultisegment
                                        ) -> Compound:
        return from_raw_multisegment(subtract_multisegments(other_raw,
                                                            self._raw,
                                                            accurate=False))

    def _symmetric_subtract_raw_multisegment(self, other_raw: RawMultisegment
                                             ) -> Compound:
        return from_raw_multisegment(
                symmetric_subtract_multisegments(self._raw, other_raw,
                                                 accurate=False))

    def _unite_with_multipoint(self, other: Multipoint) -> Compound:
        # importing here to avoid cyclic imports
        from gon.mixed.mix import from_mix_components
        return from_mix_components(other - self, self, EMPTY)

    def _unite_with_raw_multisegment(self, other_raw: RawMultisegment
                                     ) -> Compound:
        return from_raw_multisegment(unite_multisegments(self._raw, other_raw,
                                                         accurate=False))


class SegmentalSquaredDistanceNode(segmental.Node):
    def distance_to_point(self, point: RawPoint,
                          *,
                          _minus_inf: Coordinate = -inf) -> Coordinate:
        return (squared_raw_point_segment_distance(point, self.segment)
                or _minus_inf
                if self.is_leaf
                else squared_raw_interval_point_distance(self.interval, point))

    def distance_to_segment(self, segment: RawSegment,
                            *,
                            _minus_inf: Coordinate = -inf) -> Coordinate:
        return (squared_raw_segments_distance(self.segment, segment)
                or _minus_inf
                if self.is_leaf
                else squared_raw_segment_interval_distance(segment,
                                                           self.interval))


def from_raw_segments(raw_segments: List[RawSegment]) -> Compound:
    return (Multisegment.from_raw(segments_to_multisegment(raw_segments,
                                                           accurate=False))
            if raw_segments
            else EMPTY)


def raw_locate_point(raw_multisegment: RawMultisegment,
                     raw_point: RawPoint) -> Location:
    relation = point_in_multisegment(raw_point, raw_multisegment)
    return (Location.EXTERIOR
            if relation is Relation.DISJOINT
            else Location.BOUNDARY)


def _scale_segments(segments: Iterable[Segment],
                    factor_x: Coordinate,
                    factor_y: Coordinate) -> Compound:
    scaled_points, scaled_raw_segments = [], []
    for segment in segments:
        if ((factor_x or not segment.is_horizontal) and factor_y
                or factor_x and not segment.is_vertical):
            scaled_raw_segments.append((scale_raw_point(segment.start.raw(),
                                                        factor_x, factor_y),
                                        scale_raw_point(segment.end.raw(),
                                                        factor_x, factor_y)))
        else:
            scaled_points.append(scale_point(segment.start, factor_x,
                                             factor_y))
    return (from_points(unique_ever_seen(scaled_points))
            | from_raw_segments(scaled_raw_segments))


def _to_raw_point_nearest_index(raw_multisegment: RawMultisegment,
                                raw_point: RawPoint) -> int:
    enumerated_candidates = enumerate(raw_multisegment)
    result, candidate = next(enumerated_candidates)
    squared_distance_to_point = partial(squared_raw_point_segment_distance,
                                        raw_point)
    min_squared_distance = squared_distance_to_point(candidate)
    for index, candidate in enumerated_candidates:
        candidate_squared_distance = squared_distance_to_point(candidate)
        if candidate_squared_distance < min_squared_distance:
            result, min_squared_distance = index, candidate_squared_distance
    return result


def _to_raw_segment_nearest_index(raw_multisegment: RawMultisegment,
                                  raw_segment: RawSegment) -> int:
    enumerated_candidates = enumerate(raw_multisegment)
    result, candidate = next(enumerated_candidates)
    squared_distance_to_segment = partial(squared_raw_segments_distance,
                                          raw_segment)
    min_squared_distance = squared_distance_to_segment(candidate)
    for index, candidate in enumerated_candidates:
        candidate_squared_distance = squared_distance_to_segment(candidate)
        if candidate_squared_distance < min_squared_distance:
            result, min_squared_distance = index, candidate_squared_distance
    return result
