import math

from orient.planar import (point_in_segment,
                           segment_in_segment)
from reprit.base import generate_repr
from robust.hints import Point

from gon.compound import (Compound,
                          Linear,
                          Relation)
from gon.geometry import Geometry
from gon.hints import Coordinate
from gon.primitive import Point
from .hints import RawSegment
from .utils import squared_points_distance


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

    def __contains__(self, other: Geometry) -> bool:
        """
        Checks if the segment contains the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        """
        return (isinstance(other, Point)
                and (point_in_segment(other.raw(), self._raw)
                     is Relation.COMPONENT))

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
        return (self._start == other._start and self._end == other._end
                or self._start == other._end and self._end == other._start
                if isinstance(other, Segment)
                else NotImplemented)

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
        return (self == other
                or ((self.relate(other) is Relation.COMPONENT
                     if isinstance(other, Segment)
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
        return (self != other
                and ((self.relate(other) is Relation.COMPONENT
                      if isinstance(other, Segment)
                      # linear cannot be strict superset of contour or shaped
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
                or ((self.relate(other) in (Relation.EQUAL, Relation.COMPOSITE)
                     if isinstance(other, Linear)
                     else other >= self)
                    if isinstance(other, Compound)
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
                and ((self.relate(other) is Relation.COMPOSITE
                      if isinstance(other, Linear)
                      else other > self)
                     if isinstance(other, Compound)
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
        return (segment_in_segment(other._raw, self._raw)
                if isinstance(other, Segment)
                else other.relate(self).complement)

    def validate(self) -> None:
        """
        Checks if endpoints are valid and unequal.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> Segment.from_raw(((0, 0), (2, 0))).validate()
        """
        self._start.validate()
        self._end.validate()
        if self._start == self._end:
            raise ValueError('Segment is degenerate.')
