from functools import partial
from typing import List

from bentley_ottmann.planar import segments_cross_or_overlap
from orient.planar import (multisegment_in_multisegment,
                           point_in_multisegment,
                           segment_in_multisegment)
from reprit.base import generate_repr
from sect.decomposition import (Location,
                                multisegment_trapezoidal)

from gon.compound import (Compound,
                          Indexable,
                          Linear,
                          Relation)
from gon.degenerate import EMPTY
from gon.discrete import Multipoint
from gon.geometry import Geometry
from gon.hints import (Coordinate,
                       Domain)
from gon.primitive import (Point,
                           RawPoint)
from .hints import RawMultisegment
from .segment import Segment
from .utils import relate_multipoint_to_linear_compound


class Multisegment(Indexable, Linear):
    __slots__ = '_segments', '_segments_set', '_raw', '_raw_locate'

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

    __repr__ = generate_repr(__init__)

    def __contains__(self, other: Geometry) -> bool:
        """
        Checks if the multisegment contains the other geometry.

        Time complexity:
            ``O(log segments_count)`` expected after indexing,
            ``O(segments_count)`` worst after indexing or without it.
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
            ``O(min(len(self.segments), len(other.segments)))``
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
                or ((self.relate(other) in (Relation.EQUAL, Relation.COMPOSITE)
                     if isinstance(other, Linear)
                     else other >= self)
                    if isinstance(other, Compound)
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
                and ((self.relate(other) is Relation.COMPOSITE
                      if isinstance(other, Linear)
                      else other > self)
                     if isinstance(other, Compound)
                     else NotImplemented))

    @classmethod
    def from_raw(cls, raw: RawMultisegment) -> Domain:
        """
        Constructs multisegment from the combination of Python built-ins.

        Time complexity:
            ``O(segments_count)``
        Memory complexity:
            ``O(segments_count)``

        where ``segments_count = len(raw)``.

        >>> multisegment = Multisegment.from_raw([((0, 0), (1, 0)),
        ...                                       ((0, 1), (1, 1))])
        >>> multisegment == Multisegment(Segment(Point(0, 0), Point(1, 0)),
        ...                              Segment(Point(0, 1), Point(1, 1)))
        True
        """
        return Multisegment(*map(Segment.from_raw, raw))

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

    def index(self) -> None:
        """
        Pre-processes multisegment to potentially improve queries.

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
            graph = multisegment_trapezoidal(self._raw)
            self._raw_locate = graph.locate

    def raw(self) -> RawMultisegment:
        """
        Returns the multisegment as combination of Python built-ins.

        Time complexity:
            ``O(len(self.segments))``
        Memory complexity:
            ``O(len(self.segments))``

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


def raw_locate_point(raw_multisegment: RawMultisegment,
                     raw_point: RawPoint) -> Location:
    relation = point_in_multisegment(raw_point, raw_multisegment)
    return (Location.EXTERIOR
            if relation is Relation.DISJOINT
            else Location.BOUNDARY)
