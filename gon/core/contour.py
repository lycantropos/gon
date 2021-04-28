from functools import partial
from typing import (Optional,
                    Sequence)

from bentley_ottmann.planar import edges_intersect
from clipping.planar import (complete_intersect_multisegments,
                             subtract_multisegments,
                             symmetric_subtract_multisegments,
                             unite_multisegments)
from ground.base import (Context,
                         get_context)
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
from .empty import EMPTY
from .geometry import Geometry
from .hints import Coordinate
from .iterable import (non_negative_min,
                       shift_sequence)
from .linear_utils import (from_mix_components,
                           relate_multipoint_to_linear_compound,
                           to_point_nearest_segment,
                           to_segment_nearest_segment,
                           unpack_multisegment)
from .multipoint import (Multipoint,
                         rotate_points_around_origin,
                         rotate_translate_points)
from .multisegment import Multisegment
from .point import (Point,
                    point_to_step,
                    scale_point)
from .segment import Segment
from .vertices import Vertices


class Contour(Indexable, Linear):
    __slots__ = ('_context', '_edges', '_locate', '_min_index',
                 '_point_nearest_edge', '_segment_nearest_edge', '_vertices')

    def __init__(self, vertices: Vertices) -> None:
        """
        Initializes contour.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(vertices)``.
        """
        context = get_context()
        self._context = context
        self._vertices = vertices = tuple(vertices)
        self._min_index = min(range(len(vertices)),
                              key=vertices.__getitem__)
        self._locate = partial(locate_point, self)
        self._edges = edges = context.contour_edges(vertices)
        self._point_nearest_edge, self._segment_nearest_edge = (
            partial(to_point_nearest_segment, context, edges),
            partial(to_segment_nearest_segment, context, edges))

    __repr__ = generate_repr(__init__)

    def __and__(self, other: Compound) -> Compound:
        """
        Returns intersection of the contour with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> (contour & contour
        ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                   Segment(Point(1, 0), Point(0, 1)),
        ...                   Segment(Point(0, 1), Point(0, 0))]))
        True
        """
        return (self._intersect_with_multisegment(
                self.context.multisegment_cls([other]))
                if isinstance(other, Segment)
                else (self._intersect_with_multisegment(other)
                      if isinstance(other, Multisegment)
                      else
                      (self._intersect_with_multisegment(
                              self.context.multisegment_cls(other.edges))
                       if isinstance(other, Contour)
                       else NotImplemented)))

    __rand__ = __and__

    def __contains__(self, point: Point) -> bool:
        """
        Checks if the contour contains the point.

        Time complexity:
            ``O(log vertices_count)`` expected after indexing,
            ``O(vertices_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> all(vertex in contour for vertex in contour.vertices)
        True
        """
        return bool(self.locate(point))

    def __eq__(self, other: 'Contour') -> bool:
        """
        Checks if contours are equal.

        Time complexity:
            ``O(min(len(self.vertices), len(other.vertices)))``
        Memory complexity:
            ``O(1)``

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
                or (isinstance(other, Contour)
                    and _vertices.equal(self._vertices, other._vertices,
                                        self.orientation is other.orientation)
                    if isinstance(other, Geometry)
                    else NotImplemented))

    def __ge__(self, other: Compound) -> bool:
        """
        Checks if the contour is a superset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

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

    def __gt__(self, other: Compound) -> bool:
        """
        Checks if the contour is a strict superset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

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

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> hash(contour) == hash(contour)
        True
        """
        vertices = shift_sequence(self._vertices, self._min_index)
        return hash(vertices
                    if (self.context.angle_orientation(vertices[-1],
                                                       vertices[0],
                                                       vertices[1])
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

    def __lt__(self, other: Compound) -> bool:
        """
        Checks if the contour is a strict subset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

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

    def __or__(self, other: Compound) -> Compound:
        """
        Returns union of the contour with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> (contour | contour
        ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
        ...                   Segment(Point(1, 0), Point(0, 1)),
        ...                   Segment(Point(0, 1), Point(0, 0))]))
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
                       else
                       (self._unite_with_multisegment(
                               self.context.multisegment_cls(other._edges))
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
        return (self._subtract_from_multisegment(
                self.context.multisegment_cls([other]))
                if isinstance(other, Segment)
                else (self._subtract_from_multisegment(other)
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

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour - contour is EMPTY
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
                       else
                       (self._subtract_multisegment(
                               self.context.multisegment_cls(other._edges))
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

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour ^ contour is EMPTY
        True
        """
        return (self._unite_with_multipoint(other)
                if isinstance(other, Multipoint)
                else
                (self._symmetric_subtract_multisegment(
                        self.context.multisegment_cls([other]))
                 if isinstance(other, Segment)
                 else
                 (self._symmetric_subtract_multisegment(other)
                  if isinstance(other, Multisegment)
                  else (self._symmetric_subtract_multisegment(
                         self.context.multisegment_cls(other._edges))
                        if isinstance(other, Contour)
                        else NotImplemented))))

    __rxor__ = __xor__

    @property
    def centroid(self) -> Point:
        """
        Returns centroid of the contour.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(1)``

        >>> contour = Contour([Point(0, 0), Point(2, 0), Point(2, 2),
        ...                    Point(0, 2)])
        >>> contour.centroid == Point(1, 1)
        True
        """
        return get_context().contour_centroid(self._vertices)

    @property
    def context(self) -> Context:
        """
        Returns context of the contour.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> contour = Contour([Point(0, 0), Point(2, 0), Point(2, 2),
        ...                    Point(0, 2)])
        >>> isinstance(contour.context, Context)
        True
        """
        return self._context

    @property
    def edges(self) -> Sequence[Segment]:
        """
        Returns vertices of the contour.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour.edges == [Segment(Point(0, 1), Point(0, 0)),
        ...                   Segment(Point(0, 0), Point(1, 0)),
        ...                   Segment(Point(1, 0), Point(0, 1))]
        True
        """
        return list(self._edges)

    @property
    def length(self) -> Coordinate:
        """
        Returns length of the contour.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(1)``

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(1, 1),
        ...                    Point(0, 1)])
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

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour.orientation is Orientation.COUNTERCLOCKWISE
        True
        """
        vertices, min_index = self._vertices, self._min_index
        return self.context.angle_orientation(
                vertices[min_index - 1], vertices[min_index],
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

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour.vertices
        [Point(0, 0), Point(1, 0), Point(0, 1)]
        """
        return list(self._vertices)

    def distance_to(self, other: Geometry) -> Coordinate:
        """
        Returns distance between the contour and the other geometry.

        Time complexity:
            ``O(len(self.vertices))``
        Memory complexity:
            ``O(1)``

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
                                               for edge in other.edges)
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

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour.index()
        """
        graph = Graph.from_multisegment(self._as_multisegment(),
                                        context=self.context)
        self._locate = graph.locate
        tree = segmental.Tree(self._edges)
        self._point_nearest_edge = tree.nearest_to_point_segment
        self._segment_nearest_edge = tree.nearest_segment

    def locate(self, point: Point) -> Location:
        """
        Finds location of the point relative to the contour.

        Time complexity:
            ``O(log vertices_count)`` expected after indexing,
            ``O(vertices_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> all(vertex in contour for vertex in contour.vertices)
        True
        """
        return self._locate(point)

    def relate(self, other: Compound) -> Relation:
        """
        Finds relation between the contour and the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

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

    def reverse(self) -> 'Contour':
        """
        Returns the reversed contour.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.vertices)``.

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
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

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour.rotate(1, 0) == contour
        True
        >>> (contour.rotate(0, 1, Point(1, 1))
        ...  == Contour([Point(2, 0), Point(2, 1), Point(1, 0)]))
        True
        """
        return (rotate_contour_around_origin(self, cosine, sine)
                if point is None
                else rotate_translate_contour(self, cosine, sine,
                                              *point_to_step(point, cosine,
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

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour.scale(1) == contour
        True
        >>> (contour.scale(1, 2)
        ...  == Contour([Point(0, 0), Point(1, 0), Point(0, 2)]))
        True
        """
        if factor_y is None:
            factor_y = factor_x
        return (scale_contour(self, factor_x, factor_y)
                if factor_x and factor_y
                else scale_contour_degenerate(self, factor_x, factor_y))

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

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
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

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
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

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> (contour.translate(1, 2)
        ...  == Contour([Point(1, 2), Point(2, 2), Point(1, 3)]))
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

        >>> contour = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
        >>> contour.validate()
        """
        vertices = self._vertices
        for vertex in vertices:
            vertex.validate()
        vertices_count = len(vertices)
        if vertices_count < _vertices.MIN_COUNT:
            raise ValueError('Contour should have '
                             'at least {expected} vertices, '
                             'but found {actual}.'
                             .format(expected=_vertices.MIN_COUNT,
                                     actual=vertices_count))
        orienteer = self.context.angle_orientation
        if any(orienteer(vertices[index - 1], vertices[index],
                         vertices[(index + 1) % vertices_count])
               is Orientation.COLLINEAR
               for index in range(vertices_count)):
            raise ValueError('Consecutive vertices triplets '
                             'should not be on the same line.')
        if edges_intersect(self):
            raise ValueError('Contour should not be self-intersecting.')

    def _as_multisegment(self) -> Multisegment:
        return self.context.multisegment_cls(self._edges)

    def _distance_to_point(self, other: Point) -> Coordinate:
        nearest_edge = self._point_nearest_edge(other)
        return self.context.sqrt(self.context.segment_point_squared_distance(
                nearest_edge.start, nearest_edge.end, other))

    def _distance_to_segment(self, other: Segment) -> Coordinate:
        nearest_edge = self._segment_nearest_edge(other)
        return self.context.sqrt(self.context.segments_squared_distance(
                nearest_edge.start, nearest_edge.end, other.start, other.end))

    def _intersect_with_multisegment(self, other: Multisegment) -> Compound:
        multipoint, multisegment = complete_intersect_multisegments(
                self._as_multisegment(), other,
                context=self.context)
        return from_mix_components(multipoint, multisegment)

    def _subtract_multisegment(self, other: Multisegment) -> Compound:
        return unpack_multisegment(
                subtract_multisegments(self._as_multisegment(), other,
                                       context=self.context))

    def _subtract_from_multisegment(self, other: Multisegment) -> Compound:
        return unpack_multisegment(
                subtract_multisegments(other, self._as_multisegment(),
                                       context=self.context))

    def _symmetric_subtract_multisegment(self, other: Multisegment
                                         ) -> Compound:
        return unpack_multisegment(symmetric_subtract_multisegments(
                self._as_multisegment(), other,
                context=self.context))

    def _unite_with_multipoint(self, other: Multipoint) -> Compound:
        # importing here to avoid cyclic imports
        from .mix import from_mix_components
        return from_mix_components(other - self, self, EMPTY)

    def _unite_with_multisegment(self, other: Multisegment) -> Compound:
        return unite_multisegments(self._as_multisegment(), other,
                                   context=self.context)


def locate_point(contour: Contour, point: Point) -> Location:
    return (Location.BOUNDARY
            if point_in_contour(point, contour)
            else Location.EXTERIOR)


def rotate_contour_around_origin(contour: Contour,
                                 cosine: Coordinate,
                                 sine: Coordinate) -> Contour:
    return Contour(rotate_points_around_origin(contour.vertices, cosine,
                                               sine))


def rotate_translate_contour(contour: Contour,
                             cosine: Coordinate,
                             sine: Coordinate,
                             step_x: Coordinate,
                             step_y: Coordinate) -> Contour:
    return Contour(rotate_translate_points(contour.vertices, cosine, sine,
                                           step_x, step_y))


def scale_contour(contour: Contour,
                  factor_x: Coordinate,
                  factor_y: Coordinate) -> Contour:
    return Contour([scale_point(vertex, factor_x, factor_y)
                    for vertex in contour.vertices])


def scale_contour_degenerate(contour: Contour,
                             factor_x: Coordinate,
                             factor_y: Coordinate) -> Compound:
    return _vertices.scale_degenerate(contour.vertices, factor_x, factor_y)
