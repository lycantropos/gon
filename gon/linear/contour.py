from functools import partial

from bentley_ottmann.planar import edges_intersect
from orient.planar import (contour_in_contour,
                           point_in_contour,
                           segment_in_contour)
from reprit.base import generate_repr
from robust.hints import Point
from sect.decomposition import multisegment_trapezoidal

from gon.angular import (Orientation,
                         to_orientation)
from gon.compound import (Compound,
                          Indexable,
                          Linear,
                          Relation)
from gon.geometry import Geometry
from gon.hints import Coordinate
from gon.primitive import (Point,
                           RawPoint)
from . import vertices as _vertices
from .hints import (RawContour,
                    Vertices)
from .segment import Segment


class Contour(Indexable, Linear):
    __slots__ = '_contains', '_min_index', '_raw', '_vertices'

    def __init__(self, vertices: Vertices) -> None:
        """
        Initializes contour.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(vertices)``.
        """
        self._vertices = tuple(vertices)
        self._min_index = min(range(len(vertices)),
                              key=vertices.__getitem__)
        self._raw = [vertex.raw() for vertex in vertices]
        self._contains = partial(_plain_contains, self._raw)

    __repr__ = generate_repr(__init__)

    def __contains__(self, other: Geometry) -> bool:
        """
        Checks if the contour contains the other geometry.

        Time complexity:
            ``O(log vertices_count)`` expected after indexing,
            ``O(vertices_count)`` worst after indexing or without it.
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> all(vertex in contour for vertex in contour.vertices)
        True
        """
        return isinstance(other, Point) and self._contains(other.raw())

    def __eq__(self, other: 'Contour') -> bool:
        """
        Checks if the contour is equal to the other.

        Time complexity:
            ``O(min(len(self.vertices), len(other.vertices)))``
        Memory complexity:
            ``O(1)``

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour == contour
        True
        >>> contour == Contour.from_raw([(0, 0), (1, 0), (1, 1), (0, 1)])
        False
        >>> contour == Contour.from_raw([(1, 0), (0, 0), (0, 1)])
        True
        """
        return (self is other
                or (_vertices.equal(self._vertices,
                                    other._vertices,
                                    self.orientation is other.orientation)
                    if isinstance(other, Contour)
                    else (False
                          if isinstance(other, Geometry)
                          else NotImplemented)))

    def __ge__(self, other: Compound) -> bool:
        """
        Checks if the contour is a superset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour >= contour
        True
        >>> contour >= Contour.from_raw([(0, 0), (1, 0), (1, 1), (0, 1)])
        False
        >>> contour >= Contour.from_raw([(1, 0), (0, 0), (0, 1)])
        True
        """
        return (self == other
                or ((self.relate(other) in (Relation.COMPONENT, Relation.EQUAL)
                     if isinstance(other, Linear)
                     # linear cannot be superset of shaped
                     else False)
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __gt__(self, other: Compound) -> bool:
        """
        Checks if the contour is a strict superset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour > contour
        False
        >>> contour > Contour.from_raw([(0, 0), (1, 0), (1, 1), (0, 1)])
        False
        >>> contour > Contour.from_raw([(1, 0), (0, 0), (0, 1)])
        False
        """
        return (self != other
                and ((self.relate(other) is Relation.COMPONENT
                      if isinstance(other, Linear)
                      # linear cannot be strict superset of shaped
                      else False)
                     if isinstance(other, Compound)
                     else NotImplemented))

    def __hash__(self) -> int:
        """
        Returns hash value of the contour.

        Time complexity:
            ``O(1)`` if contour is counterclockwise
            and starts from the bottom leftmost vertex,
            ``O(len(self.vertices))`` otherwise
        Memory complexity:
            ``O(1)`` if contour is counterclockwise
            and starts from the bottom leftmost vertex,
            ``O(len(self.vertices))`` otherwise

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> hash(contour) == hash(contour)
        True
        """
        vertices = _vertices.shift(self._vertices, self._min_index)
        return hash(vertices
                    if (to_orientation(vertices[0], vertices[- 1], vertices[1])
                        is Orientation.COUNTERCLOCKWISE)
                    else _vertices.rotate(vertices))

    def __le__(self, other: Compound) -> bool:
        """
        Checks if the contour is a subset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour <= contour
        True
        >>> contour <= Contour.from_raw([(0, 0), (1, 0), (1, 1), (0, 1)])
        False
        >>> contour <= Contour.from_raw([(1, 0), (0, 0), (0, 1)])
        True
        """
        return (self == other
                or (((self.relate(other) in (Relation.EQUAL,
                                             Relation.COMPOSITE)
                      if isinstance(other, Contour)
                      # contour cannot be subset of segment
                      else False)
                     if isinstance(other, Linear)
                     else other >= self)
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __lt__(self, other: Compound) -> bool:
        """
        Checks if the contour is a strict subset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour < contour
        False
        >>> contour < Contour.from_raw([(0, 0), (1, 0), (1, 1), (0, 1)])
        False
        >>> contour < Contour.from_raw([(1, 0), (0, 0), (0, 1)])
        False
        """
        return (self != other
                and (((self.relate(other) is Relation.COMPOSITE
                       if isinstance(other, Contour)
                       # contour cannot be strict subset of segment
                       else False)
                      if isinstance(other, Linear)
                      else other > self)
                     if isinstance(other, Compound)
                     else NotImplemented))

    @classmethod
    def from_raw(cls, raw: RawContour) -> 'Contour':
        """
        Constructs contour from the combination of Python built-ins.

        Time complexity:
            ``O(len(raw))``
        Memory complexity:
            ``O(len(raw))``

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour == Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        True
        """
        return cls([Point.from_raw(raw_vertex) for raw_vertex in raw])

    @property
    def length(self) -> Coordinate:
        """
        Returns length of the contour.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(1)``

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (1, 1), (0, 1)])
        >>> contour.length == 4
        True
        """
        return _vertices.length(self._vertices)

    @property
    def orientation(self) -> 'Orientation':
        """
        Returns orientation of the contour.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.orientation is Orientation.COUNTERCLOCKWISE
        True
        """
        vertices, min_index = self._vertices, self._min_index
        return to_orientation(vertices[min_index], vertices[min_index - 1],
                              vertices[(min_index + 1) % len(vertices)])

    @property
    def vertices(self) -> Vertices:
        """
        Returns vertices of the contour.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(len(self.vertices))``

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.vertices
        [Point(0, 0), Point(1, 0), Point(0, 1)]
        """
        return list(self._vertices)

    def index(self) -> None:
        """
        Pre-processes contour to potentially improve queries time complexity.

        Time complexity:
            ``O(vertices_count * log vertices_count)`` expected,
            ``O(vertices_count ** 2)`` worst
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.index()
        """
        raw = self._raw
        graph = multisegment_trapezoidal([(raw[index - 1], raw[index])
                                          for index in range(len(raw))])
        self._contains = graph.__contains__

    def raw(self) -> RawContour:
        """
        Returns the contour as combination of Python built-ins.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(len(self.vertices))``

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.raw()
        [(0, 0), (1, 0), (0, 1)]
        """
        return self._raw[:]

    def relate(self, other: Compound) -> Relation:
        return (segment_in_contour(other.raw(), self._raw)
                if isinstance(other, Segment)
                else (contour_in_contour(other._raw, self._raw)
                      if isinstance(other, Contour)
                      else other.relate(self).complement))

    def reverse(self) -> 'Contour':
        """
        Returns the reversed contour.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(len(self.vertices))``

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.reverse().reverse() == contour
        True
        """
        return Contour(_vertices.rotate(self._vertices))

    def to_clockwise(self) -> 'Contour':
        """
        Returns the clockwise contour.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(1)`` if clockwise already,
            ``O(len(self.vertices))`` -- otherwise

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.to_clockwise().orientation is Orientation.CLOCKWISE
        True
        """
        return (self
                if self.orientation is Orientation.CLOCKWISE
                else self.reverse())

    def to_counterclockwise(self) -> 'Contour':
        """
        Returns the counterclockwise contour.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(1)`` if counterclockwise already,
            ``O(len(self.vertices))`` -- otherwise

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> (contour.to_counterclockwise().orientation
        ...  is Orientation.COUNTERCLOCKWISE)
        True
        """
        return (self
                if self.orientation is Orientation.COUNTERCLOCKWISE
                else self.reverse())

    def validate(self) -> None:
        """
        Checks if the contour is valid.

        Time complexity:
            ``O(len(self.vertices) * log len(self.vertices))``
        Memory complexity:
            ``O(len(self.vertices))``

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.validate()
        """
        for vertex in self._vertices:
            vertex.validate()
        if len(self._vertices) < _vertices.MIN_COUNT:
            raise ValueError('Contour should have '
                             'at least {expected} vertices, '
                             'but found {actual}.'
                             .format(expected=_vertices.MIN_COUNT,
                                     actual=len(self._vertices)))
        if any(orientation is Orientation.COLLINEAR
               for orientation in _vertices.to_orientations(self._vertices)):
            raise ValueError('Consecutive vertices triplets '
                             'should not be on the same line.')
        if edges_intersect(self._raw):
            raise ValueError('Contour should not be self-intersecting.')


def _plain_contains(raw_contour: RawContour, raw_point: RawPoint) -> bool:
    return bool(point_in_contour(raw_point, raw_contour))
