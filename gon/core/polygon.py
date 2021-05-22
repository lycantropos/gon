from functools import partial
from itertools import chain
from typing import (Optional,
                    Sequence)

from clipping.planar import (complete_intersect_multisegment_with_polygon,
                             complete_intersect_polygons,
                             complete_intersect_regions,
                             complete_intersect_segment_with_polygon,
                             subtract_multipolygon_from_polygon,
                             subtract_polygon_from_multisegment,
                             subtract_polygon_from_segment,
                             subtract_polygons,
                             symmetric_subtract_polygon_from_multisegment,
                             symmetric_subtract_polygon_from_segment,
                             symmetric_subtract_polygons,
                             unite_multisegment_with_polygon,
                             unite_polygons,
                             unite_segment_with_polygon)
from ground.base import Context
from ground.hints import Scalar
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

from .compound import (Compound,
                       Indexable,
                       Linear,
                       Location,
                       Relation,
                       Shaped)
from .contour import Contour
from .geometry import (Coordinate,
                       Geometry)
from .iterable import (flatten,
                       non_negative_min)
from .multipoint import Multipoint
from .multisegment import Multisegment
from .packing import pack_mix
from .point import Point
from .rotating import (point_to_step,
                       rotate_polygon_around_origin,
                       rotate_translate_polygon)
from .scaling import (scale_contour_degenerate,
                      scale_polygon)
from .segment import Segment
from .utils import (to_point_nearest_segment,
                    to_segment_nearest_segment)

Triangulation = Triangulation


class Polygon(Indexable[Coordinate], Shaped[Coordinate]):
    __slots__ = ('_border', '_holes', '_holes_set', '_locate',
                 '_point_nearest_edge', '_segment_nearest_edge')

    def __init__(self,
                 border: Contour[Coordinate],
                 holes: Optional[Sequence[Contour[Coordinate]]] = None
                 ) -> None:
        """
        Initializes polygon.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))
        """
        if holes is None:
            holes = []
        self._border, self._holes, self._holes_set = (border, holes,
                                                      frozenset(holes))
        context = self._context
        self._locate = partial(_locate_point, self,
                               context=context)
        edges = self.edges
        self._point_nearest_edge, self._segment_nearest_edge = (
            partial(to_point_nearest_segment, context, edges),
            partial(to_segment_nearest_segment, context, edges))

    __repr__ = generate_repr(__init__)

    def __and__(self, other: Compound) -> Compound:
        """
        Returns intersection of the polygon with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> polygon & polygon == polygon
        True
        """
        return (complete_intersect_segment_with_polygon(other, self,
                                                        context=self._context)
                if isinstance(other, Segment)
                else
                (complete_intersect_multisegment_with_polygon(
                        other, self,
                        context=self._context)
                 if isinstance(other, Linear)
                 else ((complete_intersect_polygons(self, other,
                                                    context=self._context)
                        if self.holes or other.holes
                        else complete_intersect_regions(self.border,
                                                        other.border,
                                                        context=self._context))
                       if isinstance(other, Polygon)
                       else NotImplemented)))

    __rand__ = __and__

    def __contains__(self, point: Point) -> bool:
        """
        Checks if the polygon contains the point.

        Time complexity:
            ``O(log vertices_count)`` expected after indexing,
            ``O(vertices_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
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
        return bool(self.locate(point))

    def __eq__(self, other: 'Polygon') -> bool:
        """
        Checks if polygons are equal.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(1)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> polygon == polygon
        True
        """
        return self is other or (self.border == other.border
                                 and self._holes_set == other._holes_set
                                 if isinstance(other, Polygon)
                                 else NotImplemented)

    def __ge__(self, other: Compound) -> bool:
        """
        Checks if the polygon is a superset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(1)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> polygon >= polygon
        True
        """
        return (other is self._context.empty
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

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> polygon > polygon
        False
        """
        return (other is self._context.empty
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

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> hash(polygon) == hash(polygon)
        True
        """
        return hash((self.border, self._holes_set))

    def __le__(self, other: Compound) -> bool:
        """
        Checks if the polygon is a subset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(1)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
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

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
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

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Multipolygon
        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> polygon | polygon == polygon
        True
        """
        return (self._unite_with_multipoint(other)
                if isinstance(other, Multipoint)
                else (unite_segment_with_polygon(other, self,
                                                 context=self._context)
                      if isinstance(other, Segment)
                      else
                      (unite_multisegment_with_polygon(other, self,
                                                       context=self._context)
                       if isinstance(other, Linear)
                       else (unite_polygons(self, other,
                                            context=self._context)
                             if isinstance(other, Polygon)
                             else NotImplemented))))

    __ror__ = __or__

    def __rsub__(self, other: Compound) -> Compound:
        """
        Returns difference of the other geometry with the polygon.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))
        """
        return (subtract_polygon_from_segment(other, self,
                                              context=self._context)
                if isinstance(other, Segment)
                else (subtract_polygon_from_multisegment(other, self,
                                                         context=self._context)
                      if isinstance(other, Linear)
                      else NotImplemented))

    def __sub__(self, other: Compound) -> Compound:
        """
        Returns difference of the polygon with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import EMPTY, Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> polygon - polygon is EMPTY
        True
        """
        return (self
                if isinstance(other, (Linear, Multipoint))
                else (subtract_polygons(self, other,
                                        context=self._context)
                      if isinstance(other, Polygon)
                      else NotImplemented))

    def __xor__(self, other: Compound) -> Compound:
        """
        Returns symmetric difference of the polygon with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import EMPTY, Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> polygon ^ polygon is EMPTY
        True
        """
        return (self._unite_with_multipoint(other)
                if isinstance(other, Multipoint)
                else
                (symmetric_subtract_polygon_from_segment(other, self,
                                                         context=self._context)
                 if isinstance(other, Segment)
                 else
                 (symmetric_subtract_polygon_from_multisegment(
                         other, self,
                         context=self._context)
                  if isinstance(other, Linear)
                  else (symmetric_subtract_polygons(self, other,
                                                    context=self._context)
                        if isinstance(other, Polygon)
                        else NotImplemented))))

    __rxor__ = __xor__

    @property
    def area(self) -> Coordinate:
        """
        Returns area of the polygon.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(1)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> polygon.area == 32
        True
        """
        region_signed_measure = self._context.region_signed_area
        return (abs(region_signed_measure(self.border))
                - sum(abs(region_signed_measure(hole))
                      for hole in self.holes))

    @property
    def border(self) -> Contour:
        """
        Returns border of the polygon.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
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

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> polygon.centroid == Point(3, 3)
        True
        """
        return self._context.polygon_centroid(self)

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

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> polygon.convex_hull == Polygon(polygon.border, [])
        True
        """
        context = self._context
        return (self
                if self.is_convex
                else
                context.polygon_cls(
                        context.contour_cls(context.points_convex_hull(
                                self.border.vertices)),
                        []))

    @property
    def edges(self) -> Sequence[Segment]:
        """
        Returns edges of the polygon.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon, Segment
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> polygon.edges == [Segment(Point(0, 6), Point(0, 0)),
        ...                   Segment(Point(0, 0), Point(6, 0)),
        ...                   Segment(Point(6, 0), Point(6, 6)),
        ...                   Segment(Point(6, 6), Point(0, 6)),
        ...                   Segment(Point(4, 2), Point(2, 2)),
        ...                   Segment(Point(2, 2), Point(2, 4)),
        ...                   Segment(Point(2, 4), Point(4, 4)),
        ...                   Segment(Point(4, 4), Point(4, 2))]
        True
        """
        return list(chain(self.border.segments,
                          flatten(hole.segments for hole in self.holes)))

    @property
    def holes(self) -> Sequence[Contour]:
        """
        Returns holes of the polygon.

        Time complexity:
            ``O(holes_count)``
        Memory complexity:
            ``O(holes_count)``

        where ``holes_count = len(self.holes)``.

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
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

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> polygon.is_convex
        False
        >>> polygon.convex_hull.is_convex
        True
        """
        return not self.holes and self._context.is_region_convex(self.border)

    @property
    def perimeter(self) -> Scalar:
        """
        Returns perimeter of the polygon.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(1)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> polygon.perimeter == 32
        True
        """
        return self.border.length + sum(hole.length for hole in self.holes)

    def distance_to(self, other: Geometry) -> Scalar:
        """
        Returns distance between the polygon and the other geometry.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(1)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
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
                   if isinstance(other, Linear)
                   else
                   ((non_negative_min(self._linear_distance_to_segment(edge)
                                      for edge in other.edges)
                     if self.disjoint(other)
                     else 0)
                    if isinstance(other, Polygon)
                    else other.distance_to(self))))))

    def index(self) -> None:
        """
        Pre-processes the polygon to potentially improve queries.

        Time complexity:
            ``O(vertices_count * log vertices_count)`` expected,
            ``O(vertices_count ** 2)`` worst
        Memory complexity:
            ``O(vertices_count)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> polygon.index()
        """
        self._locate = Graph.from_polygon(self,
                                          context=self._context).locate
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

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
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

    def relate(self, other: Compound) -> Relation:
        """
        Finds relation between the polygon and the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
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
               cosine: Scalar,
               sine: Scalar,
               point: Optional[Point] = None) -> 'Polygon':
        """
        Rotates the polygon by given cosine & sine around given point.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> polygon.rotate(1, 0) == polygon
        True
        >>> (polygon.rotate(0, 1, Point(1, 1))
        ...  == Polygon(Contour([Point(2, 0), Point(2, 6), Point(-4, 6),
        ...                      Point(-4, 0)]),
        ...             [Contour([Point(0, 2), Point(-2, 2), Point(-2, 4),
        ...                       Point(0, 4)])]))
        True
        """
        context = self._context
        return (rotate_polygon_around_origin(self, cosine, sine,
                                             context.contour_cls,
                                             context.point_cls,
                                             context.polygon_cls)
                if point is None
                else rotate_translate_polygon(
                self, cosine, sine, *point_to_step(point, cosine, sine),
                context.contour_cls, context.point_cls, context.polygon_cls))

    def scale(self,
              factor_x: Scalar,
              factor_y: Optional[Scalar] = None) -> 'Polygon':
        """
        Scales the polygon by given factor.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> polygon.scale(1) == polygon
        True
        >>> (polygon.scale(1, 2)
        ...  == Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 12),
        ...                      Point(0, 12)]),
        ...             [Contour([Point(2, 4), Point(2, 8), Point(4, 8),
        ...                       Point(4, 4)])]))
        True
        """
        if factor_y is None:
            factor_y = factor_x
        context = self._context
        return (scale_polygon(self, factor_x, factor_y, context.contour_cls,
                              context.point_cls, context.polygon_cls)
                if factor_x and factor_y
                else scale_contour_degenerate(self.border, factor_x,
                                              factor_y, context.multipoint_cls,
                                              context.point_cls,
                                              context.segment_cls))

    def translate(self, step_x: Scalar, step_y: Scalar) -> 'Polygon':
        """
        Translates the polygon by given step.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> (polygon.translate(1, 2)
        ...  == Polygon(Contour([Point(1, 2), Point(7, 2), Point(7, 8),
        ...                      Point(1, 8)]),
        ...             [Contour([Point(3, 4), Point(3, 6), Point(5, 6),
        ...                       Point(5, 4)])]))
        True
        """
        return self._context.polygon_cls(self.border.translate(step_x, step_y),
                                         [hole.translate(step_x, step_y)
                                          for hole in self.holes])

    def triangulate(self) -> Triangulation:
        """
        Returns triangulation of the polygon.

        Time complexity:
            ``O(vertices_count ** 2)``
        Memory complexity:
            ``O(vertices_count)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> triangulation = polygon.triangulate()
        >>> (triangulation.triangles()
        ...  == [Contour([Point(4, 4), Point(6, 0), Point(6, 6)]),
        ...      Contour([Point(4, 2), Point(6, 0), Point(4, 4)]),
        ...      Contour([Point(0, 6), Point(4, 4), Point(6, 6)]),
        ...      Contour([Point(0, 0), Point(2, 2), Point(0, 6)]),
        ...      Contour([Point(0, 0), Point(6, 0), Point(4, 2)]),
        ...      Contour([Point(0, 6), Point(2, 4), Point(4, 4)]),
        ...      Contour([Point(0, 6), Point(2, 2), Point(2, 4)]),
        ...      Contour([Point(0, 0), Point(4, 2), Point(2, 2)])])
        True
        """
        return Triangulation.constrained_delaunay(self,
                                                  context=self._context)

    def validate(self) -> None:
        """
        Checks if the polygon is valid.

        Time complexity:
            ``O(vertices_count * log (vertices_count))``
        Memory complexity:
            ``O(vertices_count)``

        where

            .. code-block:: python

                vertices_count = (len(self.border.vertices)
                                  + sum(len(hole.vertices)\
 for hole in self.holes))

        >>> from gon.base import Contour, Point, Polygon
        >>> polygon = Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),
        ...                            Point(0, 6)]),
        ...                   [Contour([Point(2, 2), Point(2, 4), Point(4, 4),
        ...                             Point(4, 2)])])
        >>> polygon.validate()
        """
        self.border.validate()
        if self.holes:
            for hole in self.holes:
                hole.validate()
            context = self._context
            relation = region_in_multiregion(self.border, self.holes,
                                             context=context)
            if not (relation is Relation.COVER
                    or relation is Relation.ENCLOSES):
                raise ValueError('Holes should lie inside the border.')
            border_minus_holes = (
                subtract_multipolygon_from_polygon(
                        context.polygon_cls(self.border, []),
                        context.multipolygon_cls([context.polygon_cls(hole, [])
                                                  for hole in self.holes]))
                if len(self.holes) > 1
                else subtract_polygons(
                        context.polygon_cls(self.border, []),
                        context.polygon_cls(self.holes[0], [])))
            if border_minus_holes != self:
                raise ValueError('Holes should not tear polygon apart.')

    def _distance_to_point(self, other: Point) -> Scalar:
        return self._context.sqrt(
                self._squared_distance_to_exterior_point(other)
                if self._locate(other) is Location.EXTERIOR
                else 0)

    def _distance_to_segment(self, other: Segment) -> Scalar:
        return (self._linear_distance_to_segment(other)
                if (self._locate(other.start) is Location.EXTERIOR
                    and self._locate(other.end) is Location.EXTERIOR)
                else 0)

    def _linear_distance_to_segment(self, other: Segment) -> Scalar:
        return self._context.segments_squared_distance(
                self._segment_nearest_edge(other), other)

    def _squared_distance_to_exterior_point(self, other: Point) -> Scalar:
        return self._context.segment_point_squared_distance(
                self._point_nearest_edge(other), other)

    def _unite_with_multipoint(self, other: Multipoint) -> Compound:
        return pack_mix(other - self, self._context.empty, self,
                        self._context.empty, self._context.mix_cls)


def _locate_point(polygon: Polygon,
                  point: Point,
                  context: Context) -> Location:
    relation = point_in_polygon(point, polygon,
                                context=context)
    return (Location.EXTERIOR
            if relation is Relation.DISJOINT
            else (Location.BOUNDARY
                  if relation is Relation.COMPONENT
                  else Location.INTERIOR))
