from functools import partial
from typing import (Optional,
                    Sequence)

from clipping.planar import (complete_intersect_multipolygons,
                             complete_intersect_multiregions,
                             complete_intersect_multisegment_with_multipolygon,
                             subtract_multipolygon_from_multisegment,
                             subtract_multipolygons,
                             symmetric_subtract_multipolygons,
                             unite_multipolygons)
from ground.base import (Context,
                         get_context)
from ground.hints import Multipolygon
from locus import segmental
from orient.planar import (contour_in_polygon,
                           multisegment_in_polygon,
                           point_in_polygon,
                           polygon_in_polygon,
                           region_in_multiregion,
                           segment_in_polygon)
from reprit.base import generate_repr
from sect.decomposition import Graph
from sect.triangulation import Triangulation

from .arithmetic import non_negative_min
from .compound import (Compound,
                       Indexable,
                       Linear,
                       Location,
                       Relation,
                       Shaped)
from .contour import (Contour,
                      rotate_contour_around_origin,
                      rotate_translate_contour,
                      scale_contour,
                      scale_contour_degenerate)
from .empty import EMPTY
from .geometry import Geometry
from .hints import Coordinate
from .linear_utils import (from_mix_components,
                           to_point_nearest_segment,
                           to_segment_nearest_segment,
                           unfold_multisegment)
from .multipoint import Multipoint
from .multisegment import Multisegment
from .point import (Point,
                    point_to_step)
from .raw import RawPolygon
from .segment import Segment
from .shaped_utils import (from_holeless_mix_components,
                           mix_from_unfolded_components,
                           unfold_multipolygon)

Triangulation = Triangulation


class Polygon(Indexable, Shaped):
    __slots__ = ('_border', '_context', '_holes', '_holes_set', '_raw_border',
                 '_raw_holes', '_locate', '_point_nearest_edge',
                 '_segment_nearest_edge')

    def __init__(self,
                 border: Contour,
                 holes: Optional[Sequence[Contour]] = None) -> None:
        """
        Initializes polygon.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(border.vertices)\
 + sum(len(hole.vertices) for hole in holes)``.
        """
        context = get_context()
        self._context = context
        holes = tuple(holes or ())
        self._border, self._holes, self._holes_set = (border, holes,
                                                      frozenset(holes))
        self._raw_border, self._raw_holes = border.raw(), [hole.raw()
                                                           for hole in holes]
        self._locate = partial(locate_point, self)
        edges = self.edges
        self._segment_nearest_edge = partial(to_segment_nearest_segment, edges,
                                             context=context)
        self._point_nearest_edge = partial(to_point_nearest_segment, edges,
                                           context=context)

    __repr__ = generate_repr(__init__)

    def __and__(self, other: Compound) -> Compound:
        """
        Returns intersection of the polygon with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> from gon.base import Multipolygon
        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon & polygon == polygon
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
                       else
                       ((mix_from_unfolded_components(
                               *complete_intersect_multipolygons(
                                       self._as_multipolygon(),
                                       other._as_multipolygon()))
                         if self._holes or other._holes
                         else from_holeless_mix_components(
                               *complete_intersect_multiregions(
                                       [self.border], [other.border])))
                        if isinstance(other, Polygon)
                        else NotImplemented))))

    __rand__ = __and__

    def __contains__(self, other: Geometry) -> bool:
        """
        Checks if the polygon contains the other geometry.

        Time complexity:
            ``O(log vertices_count)`` expected after indexing,
            ``O(vertices_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> Point(0, 0) in polygon
        True
        >>> Point(1, 1) in polygon
        True
        >>> Point(2, 2) in polygon
        True
        >>> Point(3, 3) in polygon
        False
        >>> Point(4, 3) in polygon
        True
        >>> Point(5, 2) in polygon
        True
        >>> Point(6, 1) in polygon
        True
        >>> Point(7, 0) in polygon
        False
        """
        return isinstance(other, Point) and bool(self._locate(other))

    def __eq__(self, other: 'Polygon') -> bool:
        """
        Checks if polygons are equal.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon == polygon
        True
        """
        return (self is other
                or (self._border == other._border
                    and self._holes_set == other._holes_set
                    if isinstance(other, Polygon)
                    else (False
                          if isinstance(other, Geometry)
                          else NotImplemented)))

    def __ge__(self, other: Compound) -> bool:
        """
        Checks if the polygon is a superset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon >= polygon
        True
        """
        return (other is EMPTY
                or self == other
                or (self.relate(other) in (Relation.EQUAL, Relation.COMPONENT,
                                           Relation.ENCLOSED, Relation.WITHIN)
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __gt__(self, other: Compound) -> bool:
        """
        Checks if the polygon is a strict superset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon > polygon
        False
        """
        return (other is EMPTY
                or self != other
                and (self.relate(other) in (Relation.COMPONENT,
                                            Relation.ENCLOSED, Relation.WITHIN)
                     if isinstance(other, Compound)
                     else NotImplemented))

    def __hash__(self) -> int:
        """
        Returns hash value of the polygon.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> hash(polygon) == hash(polygon)
        True
        """
        return hash((self._border, self._holes_set))

    def __le__(self, other: Compound) -> bool:
        """
        Checks if the polygon is a subset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon <= polygon
        True
        """
        return (self == other
                or not isinstance(other, (Multipoint, Linear))
                and (self.relate(other) in (Relation.COVER,
                                            Relation.ENCLOSES,
                                            Relation.COMPOSITE,
                                            Relation.EQUAL)
                     if isinstance(other, Shaped)
                     else NotImplemented))

    def __lt__(self, other: Compound) -> bool:
        """
        Checks if the polygon is a strict subset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon < polygon
        False
        """
        return (self != other
                and not isinstance(other, (Multipoint, Linear))
                and (self.relate(other) in (Relation.COVER,
                                            Relation.ENCLOSES,
                                            Relation.COMPOSITE)
                     if isinstance(other, Shaped)
                     else NotImplemented))

    def __or__(self, other: Compound) -> Compound:
        """
        Returns union of the polygon with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> from gon.base import Multipolygon
        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon | polygon == polygon
        True
        """
        return (self._unite_with_multipoint(other)
                if isinstance(other, Multipoint)
                else
                (self._unite_with_multisegment(
                        self.context.multisegment_cls([other]))
                 if isinstance(other, Segment)
                 else
                 (self._unite_with_multisegment(other)
                  if isinstance(other, Multisegment)
                  else
                  (self._unite_with_multisegment(
                          self.context.multisegment_cls(other.edges))
                   if isinstance(other, Contour)
                   else (self._unite_with_multipolygon(
                          self.context.multipolygon_cls([other]))
                         if isinstance(other, Polygon)
                         else NotImplemented)))))

    __ror__ = __or__

    def __rsub__(self, other: Compound) -> Compound:
        """
        Returns difference of the other geometry with the polygon.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.
        """
        return (self._subtract_from_multisegment(
                self.context.multisegment_cls([other]))
                if isinstance(other, Segment)
                else (self._subtract_from_multisegment(other)
                      if isinstance(other, Multisegment)
                      else
                      (self._subtract_from_multisegment(
                              self.context.multisegment_cls(other.edges))
                       if isinstance(other, Contour)
                       else NotImplemented)))

    def __sub__(self, other: Compound) -> Compound:
        """
        Returns difference of the polygon with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon - polygon is EMPTY
        True
        """
        return (self
                if isinstance(other, (Linear, Multipoint))
                else (self._subtract_multipolygon(other._as_multipolygon())
                      if isinstance(other, Polygon)
                      else NotImplemented))

    def __xor__(self, other: Compound) -> Compound:
        """
        Returns symmetric difference of the polygon with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon ^ polygon is EMPTY
        True
        """
        return (self._unite_with_multipoint(other)
                if isinstance(other, Multipoint)
                else
                (self._unite_with_multisegment(
                        self.context.multisegment_cls([other]))
                 if isinstance(other, Segment)
                 else
                 (self._unite_with_multisegment(other)
                  if isinstance(other, Multisegment)
                  else
                  (self._unite_with_multisegment(
                          self.context.multisegment_cls(other.edges))
                   if isinstance(other, Contour)
                   else
                   (self._symmetric_subtract_multipolygon(
                           other._as_multipolygon())
                    if isinstance(other, Polygon)
                    else NotImplemented)))))

    __rxor__ = __xor__

    @classmethod
    def from_raw(cls, raw: RawPolygon) -> 'Polygon':
        """
        Constructs polygon from the combination of Python built-ins.

        Time complexity:
            ``O(raw_vertices_count)``
        Memory complexity:
            ``O(raw_vertices_count)``

        where ``raw_vertices_count = len(raw_border)\
 + sum(len(raw_hole) for raw_hole in raw_holes)``,
        ``raw_border, raw_holes = raw``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> (polygon
        ...  == Polygon(Contour([Point(0, 0), Point(6, 0),
        ...                      Point(6, 6), Point(0, 6)]),
        ...             [Contour([Point(2, 2), Point(2, 4),
        ...                       Point(4, 4), Point(4, 2)])]))
        True
        """
        raw_border, raw_holes = raw
        return cls(Contour.from_raw(raw_border),
                   [Contour.from_raw(raw_hole) for raw_hole in raw_holes])

    @property
    def area(self) -> Coordinate:
        """
        Returns area of the polygon.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.area == 32
        True
        """
        region_signed_measure = self.context.region_signed_area
        return (abs(region_signed_measure(self.border.vertices))
                - sum(abs(region_signed_measure(hole.vertices))
                      for hole in self._holes))

    @property
    def border(self) -> Contour:
        """
        Returns border of the polygon.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.border == Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)])
        True
        """
        return self._border

    @property
    def centroid(self) -> Point:
        """
        Returns centroid of the polygon.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.centroid == Point(3, 3)
        True
        """
        return self.context.polygon_centroid(self.border, self.holes)

    @property
    def context(self) -> Context:
        """
        Returns context of the polygon.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> isinstance(polygon.context, Context)
        True
        """
        return self._context

    @property
    def convex_hull(self) -> 'Polygon':
        """
        Returns convex hull of the polygon.

        Time complexity:
            ``O(border_vertices_count)`` if convex already,
            ``O(border_vertices_count * log border_vertices_count)``
            -- otherwise
        Memory complexity:
            ``O(1)`` if convex already,
            ``O(border_vertices_count)`` -- otherwise

        where ``border_vertices_count = len(self.border.vertices)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.convex_hull == Polygon(polygon.border, [])
        True
        """
        return (self
                if self.is_convex
                else
                Polygon(Contour(self.context.points_convex_hull(self.border
                                                                .vertices))))

    @property
    def edges(self) -> Sequence[Segment]:
        """
        Returns edges of the polygon.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.centroid == Point(3, 3)
        True
        """
        return sum([hole.edges for hole in self.holes], self.border.edges)

    @property
    def holes(self) -> Sequence[Contour]:
        """
        Returns holes of the polygon.

        Time complexity:
            ``O(holes_count)``
        Memory complexity:
            ``O(holes_count)``

        where ``holes_count = len(self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.holes == [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                            Point(4, 2)])]
        True
        """
        return list(self._holes)

    @property
    def is_convex(self) -> bool:
        """
        Checks if the polygon is convex.

        Time complexity:
            ``O(len(self.border.vertices))``
        Memory complexity:
            ``O(1)``

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.is_convex
        False
        >>> polygon.convex_hull.is_convex
        True
        """
        return (not self._holes
                and self.context.is_region_convex(self.border.vertices))

    @property
    def perimeter(self) -> Coordinate:
        """
        Returns perimeter of the polygon.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.perimeter == 32
        True
        """
        return self._border.length + sum(hole.length for hole in self._holes)

    def distance_to(self, other: Geometry) -> Coordinate:
        """
        Returns distance between the polygon and the other geometry.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.distance_to(polygon) == 0
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
                  else
                  (non_negative_min(self._distance_to_segment(segment)
                                    for segment in other.segments)
                   if isinstance(other, Multisegment)
                   else
                   (non_negative_min(self._distance_to_segment(edge)
                                     for edge in other.edges)
                    if isinstance(other, Contour)
                    else
                    ((non_negative_min(self._linear_distance_to_segment(edge)
                                       for edge in other.edges)
                      if self.disjoint(other)
                      else 0)
                     if isinstance(other, Polygon)
                     else other.distance_to(self)))))))

    def index(self) -> None:
        """
        Pre-processes the polygon to potentially improve queries.

        Time complexity:
            ``O(vertices_count * log vertices_count)`` expected,
            ``O(vertices_count ** 2)`` worst
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.index()
        """
        self._locate = Graph.from_polygon(self,
                                          context=self.context).locate
        tree = segmental.Tree(self.edges)
        self._point_nearest_edge, self._segment_nearest_edge = (
            tree.nearest_to_point_segment, tree.nearest_segment)

    def locate(self, point: Point) -> Location:
        """
        Finds location of the point relative to the polygon.

        Time complexity:
            ``O(log vertices_count)`` expected after indexing,
            ``O(vertices_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.locate(Point(0, 0)) is Location.BOUNDARY
        True
        >>> polygon.locate(Point(1, 1)) is Location.INTERIOR
        True
        >>> polygon.locate(Point(2, 2)) is Location.BOUNDARY
        True
        >>> polygon.locate(Point(3, 3)) is Location.EXTERIOR
        True
        >>> polygon.locate(Point(4, 3)) is Location.BOUNDARY
        True
        >>> polygon.locate(Point(5, 2)) is Location.INTERIOR
        True
        >>> polygon.locate(Point(6, 1)) is Location.BOUNDARY
        True
        >>> polygon.locate(Point(7, 0)) is Location.EXTERIOR
        True
        """
        return self._locate(point)

    def raw(self) -> RawPolygon:
        """
        Returns the polygon as combination of Python built-ins.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.raw()
        ([(0, 0), (6, 0), (6, 6), (0, 6)], [[(2, 2), (2, 4), (4, 4), (4, 2)]])
        """
        return self._raw_border[:], [raw_hole[:]
                                     for raw_hole in self._raw_holes]

    def relate(self, other: Compound) -> Relation:
        """
        Finds relation between the polygon and the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.relate(polygon) is Relation.EQUAL
        True
        """
        return (segment_in_polygon(other, self)
                if isinstance(other, Segment)
                else (multisegment_in_polygon(other, self)
                      if isinstance(other, Multisegment)
                      else (contour_in_polygon(other, self)
                            if isinstance(other, Contour)
                            else (polygon_in_polygon(other, self)
                                  if isinstance(other, Polygon)
                                  else other.relate(self).complement))))

    def rotate(self,
               cosine: Coordinate,
               sine: Coordinate,
               point: Optional[Point] = None) -> 'Polygon':
        """
        Rotates the polygon by given cosine & sine around given point.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.rotate(1, 0) == polygon
        True
        >>> (polygon.rotate(0, 1, Point(1, 1))
        ...  == Polygon.from_raw(([(2, 0), (2, 6), (-4, 6), (-4, 0)],
        ...                       [[(0, 2), (-2, 2), (-2, 4), (0, 4)]])))
        True
        """
        return (rotate_polygon_around_origin(self, cosine, sine)
                if point is None
                else rotate_translate_polygon(self, cosine, sine,
                                              *point_to_step(point, cosine,
                                                             sine)))

    def scale(self,
              factor_x: Coordinate,
              factor_y: Optional[Coordinate] = None) -> 'Polygon':
        """
        Scales the polygon by given factor.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.scale(1) == polygon
        True
        >>> (polygon.scale(1, 2)
        ...  == Polygon.from_raw(([(0, 0), (6, 0), (6, 12), (0, 12)],
        ...                       [[(2, 4), (2, 8), (4, 8), (4, 4)]])))
        True
        """
        if factor_y is None:
            factor_y = factor_x
        return (scale_polygon(self, factor_x, factor_y)
                if factor_x and factor_y
                else scale_contour_degenerate(self._border, factor_x,
                                              factor_y))

    def translate(self, step_x: Coordinate, step_y: Coordinate) -> 'Polygon':
        """
        Translates the polygon by given step.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> (polygon.translate(1, 2)
        ...  == Polygon.from_raw(([(1, 2), (7, 2), (7, 8), (1, 8)],
        ...                       [[(3, 4), (3, 6), (5, 6), (5, 4)]])))
        True
        """
        return Polygon(self._border.translate(step_x, step_y),
                       [hole.translate(step_x, step_y)
                        for hole in self._holes])

    def triangulate(self) -> Triangulation:
        """
        Returns triangulation of the polygon.

        Time complexity:
            ``O(vertices_count ** 2)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> triangulation = polygon.triangulate()
        >>> (triangulation.triangles()
        ...  == [Contour.from_raw([(4, 4), (6, 0), (6, 6)]),
        ...      Contour.from_raw([(4, 2), (6, 0), (4, 4)]),
        ...      Contour.from_raw([(0, 6), (4, 4), (6, 6)]),
        ...      Contour.from_raw([(0, 0), (2, 2), (0, 6)]),
        ...      Contour.from_raw([(0, 0), (6, 0), (4, 2)]),
        ...      Contour.from_raw([(0, 6), (2, 4), (4, 4)]),
        ...      Contour.from_raw([(0, 6), (2, 2), (2, 4)]),
        ...      Contour.from_raw([(0, 0), (4, 2), (2, 2)])])
        True
        """
        return Triangulation.constrained_delaunay(self,
                                                  context=self.context)

    def validate(self) -> None:
        """
        Checks if the polygon is valid.

        Time complexity:
            ``O(vertices_count * log (vertices_count))``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.validate()
        """
        self._border.validate()
        if self._holes:
            for hole in self._holes:
                hole.validate()
            relation = region_in_multiregion(self._border, self._holes)
            if not (relation is Relation.COVER
                    or relation is Relation.ENCLOSES):
                raise ValueError('Holes should lie inside the border.')
            context = self.context
            border_minus_holes = subtract_multipolygons(
                    context.multipolygon_cls(
                            [context.polygon_cls(self._border, [])]),
                    context.multipolygon_cls(
                            [context.polygon_cls(hole, [])
                             for hole in self._holes]))
            if (len(border_minus_holes.polygons) != 1
                    or border_minus_holes.polygons[0] != self):
                raise ValueError('Holes should not tear polygon apart.')

    def _as_multipolygon(self) -> Multipolygon:
        return self.context.multipolygon_cls([self])

    def _distance_to_point(self, other: Point) -> Coordinate:
        return self.context.sqrt(
                self._squared_distance_to_exterior_point(other)
                if self._locate(other) is Location.EXTERIOR
                else 0)

    def _distance_to_segment(self, other: Segment) -> Coordinate:
        return (self._linear_distance_to_segment(other)
                if (self._locate(other.start) is Location.EXTERIOR
                    and self._locate(other.end) is Location.EXTERIOR)
                else 0)

    def _intersect_with_multisegment(self, multisegment: Multisegment
                                     ) -> Compound:
        return from_mix_components(
                *complete_intersect_multisegment_with_multipolygon(
                        multisegment, self._as_multipolygon()))

    def _linear_distance_to_segment(self, other: Segment) -> Coordinate:
        nearest_edge = self._segment_nearest_edge(other)
        return self.context.segments_squared_distance(
                nearest_edge.start, nearest_edge.end, other.start, other.end)

    def _squared_distance_to_exterior_point(self, other: Point) -> Coordinate:
        nearest_edge = self._point_nearest_edge(other)
        return self.context.segment_point_squared_distance(
                nearest_edge.start, nearest_edge.end, other)

    def _subtract_from_multisegment(self, other: Multisegment) -> Compound:
        return unfold_multisegment(subtract_multipolygon_from_multisegment(
                other, self._as_multipolygon(),
                context=self.context))

    def _subtract_multipolygon(self, multipolygon: Multipolygon
                               ) -> Compound:
        return unfold_multipolygon(subtract_multipolygons(
                self._as_multipolygon(), multipolygon,
                context=self.context))

    def _symmetric_subtract_multipolygon(self, multipolygon: Multipolygon
                                         ) -> Compound:
        return unfold_multipolygon(symmetric_subtract_multipolygons(
                self._as_multipolygon(), multipolygon,
                context=self.context))

    def _unite_with_multipoint(self, other: Multipoint) -> Compound:
        # importing here to avoid cyclic imports
        from gon.core.mix import from_mix_components
        return from_mix_components(other - self, EMPTY, self)

    def _unite_with_multisegment(self, other: Multisegment) -> Compound:
        from gon.core.mix import from_mix_components
        multipolygon = self._as_multipolygon()
        return from_mix_components(
                EMPTY,
                unfold_multisegment(subtract_multipolygon_from_multisegment(
                        other, multipolygon,
                        context=self.context)),
                multipolygon)

    def _unite_with_multipolygon(self, multipolygon: Multipolygon) -> Compound:
        return unfold_multipolygon(unite_multipolygons(self._as_multipolygon(),
                                                       multipolygon,
                                                       context=self.context))


def locate_point(polygon: Polygon, point: Point) -> Location:
    relation = point_in_polygon(point, polygon)
    return (Location.EXTERIOR
            if relation is Relation.DISJOINT
            else (Location.BOUNDARY
                  if relation is Relation.COMPONENT
                  else Location.INTERIOR))


def scale_polygon(polygon: Polygon,
                  factor_x: Coordinate,
                  factor_y: Coordinate) -> Polygon:
    return Polygon(scale_contour(polygon._border, factor_x, factor_y),
                   [scale_contour(hole, factor_x, factor_y)
                    for hole in polygon._holes])


def rotate_polygon_around_origin(polygon: Polygon,
                                 cosine: Coordinate,
                                 sine: Coordinate) -> Polygon:
    return Polygon(rotate_contour_around_origin(polygon._border, cosine, sine),
                   [rotate_contour_around_origin(hole, cosine, sine)
                    for hole in polygon._holes])


def rotate_translate_polygon(polygon: Polygon,
                             cosine: Coordinate,
                             sine: Coordinate,
                             step_x: Coordinate,
                             step_y: Coordinate) -> Polygon:
    return Polygon(rotate_translate_contour(polygon._border, cosine, sine,
                                            step_x, step_y),
                   [rotate_translate_contour(hole, cosine, sine, step_x,
                                             step_y)
                    for hole in polygon._holes])
