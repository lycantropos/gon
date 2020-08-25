from functools import partial
from typing import Optional

from bentley_ottmann.planar import edges_intersect
from clipping.planar import (complete_intersect_multisegments,
                             subtract_multisegments,
                             symmetric_subtract_multisegments,
                             unite_multisegments)
from orient.planar import (contour_in_contour,
                           multisegment_in_contour,
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
                          Location,
                          Relation)
from gon.degenerate import EMPTY
from gon.discrete import (Multipoint,
                          _robust_divide,
                          _rotate_points_around_origin,
                          _rotate_translate_points)
from gon.geometry import Geometry
from gon.hints import Coordinate
from gon.primitive import (Point,
                           RawPoint,
                           _point_to_step)
from . import vertices as _vertices
from .hints import (RawContour,
                    RawMultisegment,
                    Vertices)
from .multisegment import Multisegment
from .segment import Segment
from .utils import (from_raw_mix_components,
                    from_raw_multisegment,
                    relate_multipoint_to_linear_compound,
                    robust_sqrt,
                    shift_sequence,
                    to_pairs_chain)


class Contour(Indexable, Linear):
    __slots__ = '_raw_locate', '_min_index', '_raw', '_vertices'

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
        self._raw_locate = partial(raw_locate_point, self._raw)

    __repr__ = generate_repr(__init__)

    def __and__(self, other: Compound) -> Compound:
        """
        Returns intersection of the contour with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> (contour & contour
        ...  == Multisegment.from_raw([((0, 0), (1, 0)), ((1, 0), (0, 1)),
        ...                            ((0, 1), (0, 0))]))
        True
        """
        return (self._intersect_with_raw_multisegment([other.raw()])
                if isinstance(other, Segment)
                else (self._intersect_with_raw_multisegment(other.raw())
                      if isinstance(other, Multisegment)
                      else
                      (self._intersect_with_raw_multisegment(
                              to_pairs_chain(other._raw))
                       if isinstance(other, Contour)
                       else NotImplemented)))

    __rand__ = __and__

    def __contains__(self, other: Geometry) -> bool:
        """
        Checks if the contour contains the other geometry.

        Time complexity:
            ``O(log vertices_count)`` expected after indexing,
            ``O(vertices_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> all(vertex in contour for vertex in contour.vertices)
        True
        """
        return isinstance(other, Point) and bool(self.locate(other))

    def __eq__(self, other: 'Contour') -> bool:
        """
        Checks if contours are equal.

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
                     if isinstance(other, (Linear, Multipoint))
                     else other <= self)
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
                      if isinstance(other, (Linear, Multipoint))
                      else other < self)
                     if isinstance(other, Compound)
                     else NotImplemented))

    def __hash__(self) -> int:
        """
        Returns hash value of the contour.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(1)`` if contour is counterclockwise
            and starts from the bottom leftmost vertex,
            ``O(vertices_count)`` otherwise

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> hash(contour) == hash(contour)
        True
        """
        vertices = shift_sequence(self._vertices, self._min_index)
        return hash(vertices
                    if (to_orientation(vertices[0], vertices[- 1], vertices[1])
                        is Orientation.COUNTERCLOCKWISE)
                    else _vertices.rotate_positions(vertices))

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
                or not isinstance(other, Multipoint)
                and (not isinstance(other, Segment)
                     and self.relate(other) in (Relation.EQUAL,
                                                Relation.COMPOSITE)
                     if isinstance(other, Linear)
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
                and not isinstance(other, Multipoint)
                and (not isinstance(other, Segment)
                     and self.relate(other) is Relation.COMPOSITE
                     if isinstance(other, Linear)
                     else NotImplemented))

    def __or__(self, other: Compound) -> Compound:
        """
        Returns union of the contour with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> (contour | contour
        ...  == Multisegment.from_raw([((0, 0), (1, 0)), ((1, 0), (0, 1)),
        ...                            ((0, 1), (0, 0))]))
        True
        """
        return (self._unite_with_multipoint(other)
                if isinstance(other, Multipoint)
                else (self._unite_with_raw_multisegment([other.raw()])
                      if isinstance(other, Segment)
                      else (self._unite_with_raw_multisegment(other.raw())
                            if isinstance(other, Multisegment)
                            else
                            (self._unite_with_raw_multisegment(
                                    to_pairs_chain(other._raw))
                             if isinstance(other, Contour)
                             else NotImplemented))))

    __ror__ = __or__

    def __rsub__(self, other: Compound) -> Compound:
        """
        Returns difference of the other geometry with the contour.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.
        """
        return (self._subtract_from_raw_multisegment([other.raw()])
                if isinstance(other, Segment)
                else (self._subtract_from_raw_multisegment(other.raw())
                      if isinstance(other, Multisegment)
                      else NotImplemented))

    def __sub__(self, other: Compound) -> Compound:
        """
        Returns difference of the contour with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour - contour is EMPTY
        True
        """
        return (self
                if isinstance(other, Multipoint)
                else (self._subtract_raw_multisegment([other.raw()])
                      if isinstance(other, Segment)
                      else (self._subtract_raw_multisegment(other.raw())
                            if isinstance(other, Multisegment)
                            else
                            (self._subtract_raw_multisegment(
                                    to_pairs_chain(other._raw))
                             if isinstance(other, Contour)
                             else NotImplemented))))

    def __xor__(self, other: Compound) -> Compound:
        """
        Returns symmetric difference of the contour with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour ^ contour is EMPTY
        True
        """
        return (self._unite_with_multipoint(other)
                if isinstance(other, Multipoint)
                else (self._symmetric_subtract_raw_multisegment([other.raw()])
                      if isinstance(other, Segment)
                      else
                      (self._symmetric_subtract_raw_multisegment(other.raw())
                       if isinstance(other, Multisegment)
                       else
                       (self._symmetric_subtract_raw_multisegment(
                               to_pairs_chain(other._raw))
                        if isinstance(other, Contour)
                        else NotImplemented))))

    __rxor__ = __xor__

    @classmethod
    def from_raw(cls, raw: RawContour) -> 'Contour':
        """
        Constructs contour from the combination of Python built-ins.

        Time complexity:
            ``O(raw_vertices_count)``
        Memory complexity:
            ``O(raw_vertices_count)``

        where ``raw_vertices_count = len(raw)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour == Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        True
        """
        return cls([Point.from_raw(raw_vertex) for raw_vertex in raw])

    @property
    def centroid(self) -> Point:
        """
        Returns centroid of the contour.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(1)``

        >>> contour = Contour.from_raw([(0, 0), (2, 0), (2, 2), (0, 2)])
        >>> contour.centroid == Point(1, 1)
        True
        """
        accumulated_x = accumulated_y = accumulated_length = 0
        start_x, start_y = self._raw[-1]
        for end_x, end_y in self._raw:
            length = robust_sqrt((end_x - start_x) ** 2
                                 + (end_y - start_y) ** 2)
            accumulated_x += (start_x + end_x) * length
            accumulated_y += (start_y + end_y) * length
            accumulated_length += length
            start_x, start_y = end_x, end_y
        divisor = 2 * accumulated_length
        return Point(_robust_divide(accumulated_x, divisor),
                     _robust_divide(accumulated_y, divisor))

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
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.vertices
        [Point(0, 0), Point(1, 0), Point(0, 1)]
        """
        return list(self._vertices)

    def index(self) -> None:
        """
        Pre-processes contour to potentially improve queries.

        Time complexity:
            ``O(vertices_count * log vertices_count)`` expected,
            ``O(vertices_count ** 2)`` worst
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.index()
        """
        graph = multisegment_trapezoidal(to_pairs_chain(self._raw))
        self._raw_locate = graph.locate

    def locate(self, point: Point) -> Location:
        """
        Finds location of the point relative to the contour.

        Time complexity:
            ``O(log vertices_count)`` expected after indexing,
            ``O(vertices_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> all(vertex in contour for vertex in contour.vertices)
        True
        """
        return self._raw_locate(point.raw())

    def raw(self) -> RawContour:
        """
        Returns the contour as combination of Python built-ins.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.raw()
        [(0, 0), (1, 0), (0, 1)]
        """
        return self._raw[:]

    def relate(self, other: Compound) -> Relation:
        """
        Finds relation between the contour and the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.relate(contour) is Relation.EQUAL
        True
        """
        return (relate_multipoint_to_linear_compound(other, self)
                if isinstance(other, Multipoint)
                else (segment_in_contour(other.raw(), self._raw)
                      if isinstance(other, Segment)
                      else (multisegment_in_contour(other.raw(), self._raw)
                            if isinstance(other, Multisegment)
                            else (contour_in_contour(other._raw, self._raw)
                                  if isinstance(other, Contour)
                                  else other.relate(self).complement))))

    def reverse(self) -> 'Contour':
        """
        Returns the reversed contour.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.reverse().reverse() == contour
        True
        """
        return Contour(_vertices.rotate_positions(self._vertices))

    def rotate(self,
               cosine: Coordinate,
               sine: Coordinate,
               point: Optional[Point] = None) -> 'Contour':
        """
        Rotates the contour by given cosine & sine around given point.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.rotate(1, 0) == contour
        True
        >>> (contour.rotate(0, 1, Point(1, 1))
        ...  == Contour.from_raw([(2, 0), (2, 1), (1, 0)]))
        True
        """
        return (rotate_contour_around_origin(self, cosine, sine)
                if point is None
                else _rotate_translate_contour(self, cosine, sine,
                                               *_point_to_step(point, cosine,
                                                               sine)))

    def scale(self,
              factor_x: Coordinate,
              factor_y: Optional[Coordinate] = None) -> Compound:
        """
        Scales the contour by given factor.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.scale(1) == contour
        True
        >>> (contour.scale(1, 2)
        ...  == Contour.from_raw([(0, 0), (1, 0), (0, 2)]))
        True
        """
        if factor_y is None:
            factor_y = factor_x
        return (_scale_contour(self, factor_x, factor_y)
                if factor_x and factor_y
                else _scale_contour_degenerate(self, factor_x, factor_y))

    def to_clockwise(self) -> 'Contour':
        """
        Returns the clockwise contour.

        Time complexity:
            ``O(1)`` if clockwise already,
            ``O(vertices_count)`` -- otherwise
        Memory complexity:
            ``O(1)`` if clockwise already,
            ``O(vertices_count)`` -- otherwise

        where ``vertices_count = len(self.vertices)``.

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
            ``O(1)`` if counterclockwise already,
            ``O(vertices_count)`` -- otherwise
        Memory complexity:
            ``O(1)`` if counterclockwise already,
            ``O(vertices_count)`` -- otherwise

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> (contour.to_counterclockwise().orientation
        ...  is Orientation.COUNTERCLOCKWISE)
        True
        """
        return (self
                if self.orientation is Orientation.COUNTERCLOCKWISE
                else self.reverse())

    def translate(self, step_x: Coordinate, step_y: Coordinate) -> 'Contour':
        """
        Translates the contour by given step.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> (contour.translate(1, 2)
        ...  == Contour.from_raw([(1, 2), (2, 2), (1, 3)]))
        True
        """
        return Contour([vertex.translate(step_x, step_y)
                        for vertex in self._vertices])

    def validate(self) -> None:
        """
        Checks if the contour is valid.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

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

    def _intersect_with_raw_multisegment(self, other_raw: RawMultisegment
                                         ) -> Compound:
        raw_multipoint, raw_multisegment, _ = complete_intersect_multisegments(
                to_pairs_chain(self._raw), other_raw,
                accurate=False)
        return from_raw_mix_components(raw_multipoint, raw_multisegment)

    def _subtract_raw_multisegment(self, other_raw: RawMultisegment
                                   ) -> Compound:
        return from_raw_multisegment(subtract_multisegments(
                to_pairs_chain(self._raw), other_raw,
                accurate=False))

    def _subtract_from_raw_multisegment(self, other_raw: RawMultisegment
                                        ) -> Compound:
        return from_raw_multisegment(subtract_multisegments(
                other_raw, to_pairs_chain(self._raw),
                accurate=False))

    def _symmetric_subtract_raw_multisegment(self, other_raw: RawMultisegment
                                             ) -> Compound:
        return from_raw_multisegment(symmetric_subtract_multisegments(
                to_pairs_chain(self._raw), other_raw,
                accurate=False))

    def _unite_with_multipoint(self, other: Multipoint) -> Compound:
        # importing here to avoid cyclic imports
        from gon.mixed.mix import from_mix_components
        return from_mix_components(other - self, self, EMPTY)

    def _unite_with_raw_multisegment(self, other_raw: RawMultisegment
                                     ) -> Compound:
        return from_raw_multisegment(unite_multisegments(
                to_pairs_chain(self._raw), other_raw,
                accurate=False))


def raw_locate_point(raw_contour: RawContour, raw_point: RawPoint) -> Location:
    return (Location.BOUNDARY
            if point_in_contour(raw_point, raw_contour)
            else Location.EXTERIOR)


def rotate_contour_around_origin(contour: Contour,
                                 cosine: Coordinate,
                                 sine: Coordinate) -> Contour:
    return Contour(_rotate_points_around_origin(contour._vertices, cosine,
                                                sine))


def _rotate_translate_contour(contour: Contour,
                              cosine: Coordinate,
                              sine: Coordinate,
                              step_x: Coordinate,
                              step_y: Coordinate) -> Contour:
    return Contour(_rotate_translate_points(contour._vertices, cosine, sine,
                                            step_x, step_y))


def _scale_contour(contour: Contour,
                   factor_x: Coordinate,
                   factor_y: Coordinate) -> Contour:
    return Contour(_vertices.scale(contour._vertices, factor_x, factor_y))


def _scale_contour_degenerate(contour: Contour,
                              factor_x: Coordinate,
                              factor_y: Coordinate) -> Compound:
    return _vertices.scale_degenerate(contour._vertices, factor_x, factor_y)
