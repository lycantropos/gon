from functools import partial
from typing import (Optional,
                    Sequence)

from bentley_ottmann.planar import edges_intersect
from clipping.planar import (complete_intersect_multisegments,
                             complete_intersect_segment_with_multisegment,
                             subtract_multisegment_from_segment,
                             subtract_multisegments,
                             subtract_segment_from_multisegment,
                             symmetric_subtract_multisegment_from_segment,
                             symmetric_subtract_multisegments,
                             unite_multisegments,
                             unite_segment_with_multisegment)
from ground.base import Context
from ground.hints import Scalar
from locus import segmental
from orient.planar import (contour_in_contour,
                           multisegment_in_contour,
                           point_in_contour,
                           segment_in_contour)
from reprit.base import generate_repr
from sect.decomposition import Graph

from . import vertices as _vertices
from .angular import Orientation
from .compound import (Compound,
                       Indexable,
                       Linear,
                       Location,
                       Relation)
from .geometry import (Coordinate,
                       Geometry)
from .iterable import (non_negative_min,
                       shift_sequence)
from .multipoint import Multipoint
from .multisegment import Multisegment
from .packing import pack_mix
from .point import Point
from .rotating import (point_to_step,
                       rotate_contour_around_origin,
                       rotate_translate_contour)
from .scaling import (scale_contour,
                      scale_contour_degenerate)
from .segment import Segment
from .utils import (relate_multipoint_to_linear_compound,
                    to_point_nearest_segment,
                    to_segment_nearest_segment)


class Contour(Indexable[Coordinate], Linear[Coordinate]):
    __slots__ = ('_locate', '_min_index', '_point_nearest_segment',
                 '_segment_nearest_segment', '_segments', '_vertices')

    def __init__(self, vertices: Sequence[Point[Coordinate]]) -> None:
        """
        Initializes contour.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(vertices)``.
        """
        self._vertices = vertices = tuple(vertices)
        self._min_index = min(range(len(vertices)),
                              key=vertices.__getitem__)
        context = self._context
        self._locate = partial(_locate_point, self,
                               context=context)
        self._segments = segments = context.contour_edges(self)
        self._point_nearest_segment, self._segment_nearest_segment = (
            partial(to_point_nearest_segment, context, segments),
            partial(to_segment_nearest_segment, context, segments))

    __repr__ = generate_repr(__init__)

    def __and__(self, other: Compound[Coordinate]) -> Compound[Coordinate]:
        """
        Returns intersection of the contour with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Multisegment, Point, Segment
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> (contour & contour
        ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                   Segment(Point(1, 0), Point(0, 1)),
        ...                   Segment(Point(0, 1), Point(0, 0))]))
        True
        """
        return (complete_intersect_segment_with_multisegment(
                other, self,
                context=self._context)
                if isinstance(other, Segment)
                else (complete_intersect_multisegments(self, other,
                                                       context=self._context)
                      if isinstance(other, Linear)
                      else NotImplemented))

    __rand__ = __and__

    def __contains__(self, point: Point[Coordinate]) -> bool:
        """
        Checks if the contour contains the point.

        Time complexity:
            ``O(log vertices_count)`` expected after indexing,
            ``O(vertices_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> all(vertex in contour for vertex in contour.vertices)
        True
        """
        return bool(self.locate(point))

    def __eq__(self, other: 'Contour[Coordinate]') -> bool:
        """
        Checks if contours are equal.

        Time complexity:
            ``O(min(len(self.vertices), len(other.vertices)))``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Contour, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour == contour
        True
        >>> contour == Contour([Point(0, 0), Point(1, 0), Point(1, 1),
        ...                     Point(0, 1)])
        False
        >>> contour == Contour([Point(1, 0), Point(0, 0), Point(0, 1)])
        True
        """
        return (self is other
                or (_vertices.equal(self._vertices, other._vertices,
                                    self.orientation is other.orientation)
                    if isinstance(other, Contour)
                    else NotImplemented))

    def __ge__(self, other: Compound[Coordinate]) -> bool:
        """
        Checks if the contour is a superset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour >= contour
        True
        >>> contour >= Contour([Point(0, 0), Point(1, 0), Point(1, 1),
        ...                     Point(0, 1)])
        False
        >>> contour >= Contour([Point(1, 0), Point(0, 0), Point(0, 1)])
        True
        """
        return (self == other
                or ((self.relate(other) in (Relation.COMPONENT, Relation.EQUAL)
                     if isinstance(other, (Linear, Multipoint))
                     else other <= self)
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __gt__(self, other: Compound[Coordinate]) -> bool:
        """
        Checks if the contour is a strict superset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour > contour
        False
        >>> contour > Contour([Point(0, 0), Point(1, 0), Point(1, 1),
        ...                    Point(0, 1)])
        False
        >>> contour > Contour([Point(1, 0), Point(0, 0), Point(0, 1)])
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

        >>> from gon.base import Contour, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> hash(contour) == hash(contour)
        True
        """
        vertices = shift_sequence(self._vertices, self._min_index)
        return hash(vertices
                    if (self._context.angle_orientation(vertices[-1],
                                                        vertices[0],
                                                        vertices[1])
                        is Orientation.COUNTERCLOCKWISE)
                    else _vertices.rotate_positions(vertices))

    def __le__(self, other: Compound[Coordinate]) -> bool:
        """
        Checks if the contour is a subset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour <= contour
        True
        >>> contour <= Contour([Point(0, 0), Point(1, 0), Point(1, 1),
        ...                     Point(0, 1)])
        False
        >>> contour <= Contour([Point(1, 0), Point(0, 0), Point(0, 1)])
        True
        """
        return (self == other
                or not isinstance(other, Multipoint)
                and (not isinstance(other, Segment)
                     and self.relate(other) in (Relation.EQUAL,
                                                Relation.COMPOSITE)
                     if isinstance(other, Linear)
                     else NotImplemented))

    def __lt__(self, other: Compound[Coordinate]) -> bool:
        """
        Checks if the contour is a strict subset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour < contour
        False
        >>> contour < Contour([Point(0, 0), Point(1, 0), Point(1, 1),
        ...                    Point(0, 1)])
        False
        >>> contour < Contour([Point(1, 0), Point(0, 0), Point(0, 1)])
        False
        """
        return (self != other
                and not isinstance(other, Multipoint)
                and (not isinstance(other, Segment)
                     and self.relate(other) is Relation.COMPOSITE
                     if isinstance(other, Linear)
                     else NotImplemented))

    def __or__(self, other: Compound[Coordinate]) -> Compound[Coordinate]:
        """
        Returns union of the contour with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Multisegment, Point, Segment
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> (contour | contour
        ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                   Segment(Point(1, 0), Point(0, 1)),
        ...                   Segment(Point(0, 1), Point(0, 0))]))
        True
        """
        return (self._unite_with_multipoint(other)
                if isinstance(other, Multipoint)
                else (unite_segment_with_multisegment(other, self,
                                                      context=self._context)
                      if isinstance(other, Segment)
                      else (unite_multisegments(self, other,
                                                context=self._context)
                            if isinstance(other, Linear)
                            else NotImplemented)))

    __ror__ = __or__

    def __rsub__(self, other: Compound[Coordinate]) -> Compound[Coordinate]:
        """
        Returns difference of the other geometry with the contour.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.
        """
        return (subtract_multisegment_from_segment(other,
                                                   self,
                                                   context=self._context)
                if isinstance(other, Segment)
                else (subtract_multisegments(other, self,
                                             context=self._context)
                      if isinstance(other, Multisegment)
                      else NotImplemented))

    def __sub__(self, other: Compound[Coordinate]) -> Compound[Coordinate]:
        """
        Returns difference of the contour with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import EMPTY, Contour, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour - contour is EMPTY
        True
        """
        return (self
                if isinstance(other, Multipoint)
                else (subtract_segment_from_multisegment(self, other,
                                                         context=self._context)
                      if isinstance(other, Segment)
                      else (subtract_multisegments(self, other,
                                                   context=self._context)
                            if isinstance(other, Linear)
                            else NotImplemented)))

    def __xor__(self, other: Compound[Coordinate]) -> Compound[Coordinate]:
        """
        Returns symmetric difference of the contour with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import EMPTY, Contour, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour ^ contour is EMPTY
        True
        """
        return (self._unite_with_multipoint(other)
                if isinstance(other, Multipoint)
                else
                (symmetric_subtract_multisegment_from_segment(
                        other, self,
                        context=self._context)
                 if isinstance(other, Segment)
                 else (symmetric_subtract_multisegments(self, other,
                                                        context=self._context)
                       if isinstance(other, Linear)
                       else NotImplemented)))

    __rxor__ = __xor__

    @property
    def centroid(self) -> Point[Scalar]:
        """
        Returns centroid of the contour.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Contour, Point
        >>> contour = Contour([Point(0, 0), Point(2, 0), Point(2, 2),
        ...                    Point(0, 2)])
        >>> contour.centroid == Point(1, 1)
        True
        """
        return self._context.contour_centroid(self)

    @property
    def segments(self) -> Sequence[Segment[Coordinate]]:
        """
        Returns segments of the contour.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Point, Segment
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour.segments == [Segment(Point(0, 1), Point(0, 0)),
        ...                      Segment(Point(0, 0), Point(1, 0)),
        ...                      Segment(Point(1, 0), Point(0, 1))]
        True
        """
        return list(self._segments)

    @property
    def length(self) -> Scalar:
        """
        Returns length of the contour.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Contour, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(1, 1),
        ...                    Point(0, 1)])
        >>> contour.length == 4
        True
        """
        vertices = self._vertices
        sqrt, points_squared_distance = (self._context.sqrt,
                                         self._context.points_squared_distance)
        return sum(sqrt(points_squared_distance(vertices[index],
                                                vertices[index - 1]))
                   for index in range(len(vertices)))

    @property
    def orientation(self) -> Orientation:
        """
        Returns orientation of the contour.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Contour, Orientation, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour.orientation is Orientation.COUNTERCLOCKWISE
        True
        """
        vertices, min_index = self._vertices, self._min_index
        return self._context.angle_orientation(
                vertices[min_index - 1], vertices[min_index],
                vertices[(min_index + 1) % len(vertices)])

    @property
    def vertices(self) -> Sequence[Point[Coordinate]]:
        """
        Returns vertices of the contour.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour.vertices == [Point(0, 0), Point(1, 0), Point(0, 1)]
        True
        """
        return list(self._vertices)

    def distance_to(self, other: Geometry[Coordinate]) -> Scalar:
        """
        Returns distance between the contour and the other geometry.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Contour, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour.distance_to(contour) == 0
        True
        """
        return (self._distance_to_point(other)
                if isinstance(other, Point)
                else (non_negative_min(self._distance_to_point(point)
                                       for point in other.points)
                      if isinstance(other, Multipoint)
                      else
                      (self._distance_to_segment(other)
                       if isinstance(other, Segment)
                       else
                       (non_negative_min(self._distance_to_segment(segment)
                                         for segment in other.segments)
                        if isinstance(other, Multisegment)
                        else (non_negative_min(self._distance_to_segment(edge)
                                               for edge in other.segments)
                              if isinstance(other, Contour)
                              else other.distance_to(self))))))

    def index(self) -> None:
        """
        Pre-processes the contour to potentially improve queries.

        Time complexity:
            ``O(vertices_count * log vertices_count)`` expected,
            ``O(vertices_count ** 2)`` worst
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour.index()
        """
        self._locate = Graph.from_multisegment(self,
                                               context=self._context).locate
        tree = segmental.Tree(self._segments)
        self._point_nearest_segment = tree.nearest_to_point_segment
        self._segment_nearest_segment = tree.nearest_segment

    def locate(self, point: Point[Coordinate]) -> Location:
        """
        Finds location of the point relative to the contour.

        Time complexity:
            ``O(log vertices_count)`` expected after indexing,
            ``O(vertices_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Location, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> all(contour.locate(vertex) is Location.BOUNDARY
        ...     for vertex in contour.vertices)
        True
        """
        return self._locate(point)

    def relate(self, other: Compound[Coordinate]) -> Relation:
        """
        Finds relation between the contour and the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Point, Relation
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour.relate(contour) is Relation.EQUAL
        True
        """
        return (relate_multipoint_to_linear_compound(other, self)
                if isinstance(other, Multipoint)
                else (segment_in_contour(other, self)
                      if isinstance(other, Segment)
                      else (multisegment_in_contour(other, self)
                            if isinstance(other, Multisegment)
                            else (contour_in_contour(other, self)
                                  if isinstance(other, Contour)
                                  else other.relate(self).complement))))

    def reverse(self) -> 'Contour[Coordinate]':
        """
        Returns the reversed contour.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour.reverse().reverse() == contour
        True
        """
        return self._context.contour_cls(
                _vertices.rotate_positions(self._vertices))

    def rotate(self,
               cosine: Coordinate,
               sine: Coordinate,
               point: Optional[Point[Coordinate]] = None
               ) -> 'Contour[Coordinate]':
        """
        Rotates the contour by given cosine & sine around given point.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour.rotate(1, 0) == contour
        True
        >>> (contour.rotate(0, 1, Point(1, 1))
        ...  == Contour([Point(2, 0), Point(2, 1), Point(1, 0)]))
        True
        """
        context = self._context
        return (rotate_contour_around_origin(
                self, cosine, sine, context.contour_cls, context.point_cls)
                if point is None
                else rotate_translate_contour(
                self, cosine, sine, *point_to_step(point, cosine, sine),
                context.contour_cls, context.point_cls))

    def scale(self,
              factor_x: Coordinate,
              factor_y: Optional[Coordinate] = None) -> Compound[Coordinate]:
        """
        Scales the contour by given factor.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour.scale(1) == contour
        True
        >>> (contour.scale(1, 2)
        ...  == Contour([Point(0, 0), Point(1, 0), Point(0, 2)]))
        True
        """
        if factor_y is None:
            factor_y = factor_x
        context = self._context
        return (scale_contour(self, factor_x, factor_y, context.contour_cls,
                              context.point_cls)
                if factor_x and factor_y
                else scale_contour_degenerate(self, factor_x, factor_y,
                                              context.multipoint_cls,
                                              context.point_cls,
                                              context.segment_cls))

    def to_clockwise(self) -> 'Contour[Coordinate]':
        """
        Returns the clockwise contour.

        Time complexity:
            ``O(1)`` if clockwise already,
            ``O(vertices_count)`` -- otherwise
        Memory complexity:
            ``O(1)`` if clockwise already,
            ``O(vertices_count)`` -- otherwise

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Orientation, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour.to_clockwise().orientation is Orientation.CLOCKWISE
        True
        """
        return (self
                if self.orientation is Orientation.CLOCKWISE
                else self.reverse())

    def to_counterclockwise(self) -> 'Contour[Coordinate]':
        """
        Returns the counterclockwise contour.

        Time complexity:
            ``O(1)`` if counterclockwise already,
            ``O(vertices_count)`` -- otherwise
        Memory complexity:
            ``O(1)`` if counterclockwise already,
            ``O(vertices_count)`` -- otherwise

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Orientation, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> (contour.to_counterclockwise().orientation
        ...  is Orientation.COUNTERCLOCKWISE)
        True
        """
        return (self
                if self.orientation is Orientation.COUNTERCLOCKWISE
                else self.reverse())

    def translate(self,
                  step_x: Coordinate,
                  step_y: Coordinate) -> 'Contour[Coordinate]':
        """
        Translates the contour by given step.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> (contour.translate(1, 2)
        ...  == Contour([Point(1, 2), Point(2, 2), Point(1, 3)]))
        True
        """
        return self._context.contour_cls([vertex.translate(step_x, step_y)
                                          for vertex in self._vertices])

    def validate(self) -> None:
        """
        Checks if the contour is valid.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> from gon.base import Contour, Point
        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour.validate()
        """
        vertices = self._vertices
        vertices_count = len(vertices)
        if vertices_count < _vertices.MIN_COUNT:
            raise ValueError('Contour should have '
                             'at least {expected} vertices, '
                             'but found {actual}.'
                             .format(expected=_vertices.MIN_COUNT,
                                     actual=vertices_count))
        for vertex in vertices:
            vertex.validate()
        orienteer = self._context.angle_orientation
        if any(orienteer(vertices[index - 1], vertices[index],
                         vertices[(index + 1) % vertices_count])
               is Orientation.COLLINEAR
               for index in range(vertices_count)):
            raise ValueError('Consecutive vertices triplets '
                             'should not be on the same line.')
        if edges_intersect(self):
            raise ValueError('Contour should not be self-intersecting.')

    def _distance_to_point(self, other: Point[Coordinate]) -> Scalar:
        return self._context.sqrt(self._context.segment_point_squared_distance(
                self._point_nearest_segment(other), other))

    def _distance_to_segment(self, other: Segment[Coordinate]) -> Scalar:
        return self._context.sqrt(self._context.segments_squared_distance(
                self._segment_nearest_segment(other), other))

    def _unite_with_multipoint(self, other: Multipoint[Coordinate]
                               ) -> Compound[Coordinate]:
        context = self._context
        return pack_mix(other - self, self, context.empty, context.empty,
                        context.mix_cls)


def _locate_point(contour: Contour[Coordinate],
                  point: Point[Coordinate],
                  context: Context) -> Location:
    return (Location.BOUNDARY
            if point_in_contour(point, contour,
                                context=context)
            else Location.EXTERIOR)
