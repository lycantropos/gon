from bisect import bisect
from functools import partial
from itertools import (accumulate,
                       chain)
from typing import (Iterator,
                    List,
                    Optional,
                    Sequence,
                    Tuple)

from clipping.planar import (complete_intersect_multipolygons,
                             complete_intersect_multiregions,
                             complete_intersect_multisegment_with_multipolygon,
                             subtract_multipolygon_from_multisegment,
                             subtract_multipolygons,
                             symmetric_subtract_multipolygons,
                             unite_multipolygons)
from locus import segmental
from orient.planar import (contour_in_polygon,
                           multisegment_in_polygon,
                           point_in_polygon,
                           polygon_in_polygon,
                           region_in_multiregion,
                           segment_in_polygon)
from reprit.base import generate_repr
from robust.hints import Expansion
from robust.utils import (scale_expansion,
                          sum_expansions,
                          two_product,
                          two_two_diff)
from sect.decomposition import polygon_trapezoidal
from sect.triangulation import constrained_delaunay_triangles

from gon.compound import (Compound,
                          Indexable,
                          Linear,
                          Location,
                          Relation,
                          Shaped)
from gon.core.arithmetic import (non_negative_min,
                                 robust_divide)
from gon.degenerate import EMPTY
from gon.discrete import Multipoint
from gon.geometry import Geometry
from gon.hints import Coordinate
from gon.linear import (Contour,
                        Multisegment,
                        RawContour,
                        RawMultisegment,
                        RawSegment,
                        Segment,
                        vertices)
from gon.linear.contour import (rotate_contour_around_origin,
                                rotate_translate_contour,
                                scale_contour,
                                scale_contour_degenerate)
from gon.linear.multisegment import SegmentalSquaredDistanceNode
from gon.linear.raw import (raw_segment_point_distance,
                            raw_segments_distance,
                            squared_raw_point_segment_distance,
                            squared_raw_segments_distance)
from gon.linear.utils import (from_raw_multisegment,
                              to_pairs_iterable,
                              to_pairs_sequence)
from gon.primitive import (Point,
                           RawPoint)
from gon.primitive.point import point_to_step
from .hints import (RawMultipolygon,
                    RawPolygon)
from .utils import (flatten,
                    from_raw_holeless_mix_components,
                    from_raw_mix_components,
                    from_raw_multipolygon,
                    to_convex_hull)


class Polygon(Indexable, Shaped):
    __slots__ = ('_border', '_holes', '_holes_set', '_raw_border',
                 '_raw_holes', '_raw_locate', '_raw_point_nearest_path',
                 '_raw_segment_nearest_path')

    def __init__(self, border: Contour,
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
        holes = tuple(holes or ())
        self._border, self._holes, self._holes_set = (border, holes,
                                                      frozenset(holes))
        self._raw_border, self._raw_holes = border.raw(), [hole.raw()
                                                           for hole in holes]
        self._raw_locate = partial(raw_locate_point,
                                   (self._raw_border, self._raw_holes))
        self._raw_segment_nearest_path = partial(_to_raw_segment_nearest_path,
                                                 self._raw_border,
                                                 self._raw_holes)
        self._raw_point_nearest_path = partial(_to_raw_point_nearest_path,
                                               self._raw_border,
                                               self._raw_holes)

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

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon & polygon == polygon
        True
        """
        return (self._intersect_with_raw_multisegment([other.raw()])
                if isinstance(other, Segment)
                else (self._intersect_with_raw_multisegment(other.raw())
                      if isinstance(other, Multisegment)
                      else
                      (self._intersect_with_raw_multisegment(
                              to_pairs_sequence(other.raw()))
                       if isinstance(other, Contour)
                       else
                       ((from_raw_mix_components(
                               *complete_intersect_multipolygons(
                                       [(self._raw_border, self._raw_holes)],
                                       [(other._raw_border, other._raw_holes)],
                                       accurate=False))
                         if self._holes or other._holes
                         else from_raw_holeless_mix_components(
                               *complete_intersect_multiregions(
                                       [self._raw_border], [other._raw_border],
                                       accurate=False)))
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
        return isinstance(other, Point) and bool(self._raw_locate(other.raw()))

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

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon | polygon == polygon
        True
        """
        return (self._unite_with_multipoint(other)
                if isinstance(other, Multipoint)
                else
                (self._unite_with_raw_multisegment([other.raw()])
                 if isinstance(other, Segment)
                 else
                 (self._unite_with_raw_multisegment(other.raw())
                  if isinstance(other, Multisegment)
                  else
                  (self._unite_with_raw_multisegment(
                          to_pairs_sequence(other.raw()))
                   if isinstance(other, Contour)
                   else (self._unite_with_raw_multipolygon([other.raw()])
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
        return (self._subtract_from_raw_multisegment([other.raw()])
                if isinstance(other, Segment)
                else (self._subtract_from_raw_multisegment(other.raw())
                      if isinstance(other, Multisegment)
                      else
                      (self._subtract_from_raw_multisegment(
                              to_pairs_sequence(other.raw()))
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
                else (self._subtract_raw_multipolygon([(other._raw_border,
                                                        other._raw_holes)])
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
                (self._unite_with_raw_multisegment([other.raw()])
                 if isinstance(other, Segment)
                 else
                 (self._unite_with_raw_multisegment(other.raw())
                  if isinstance(other, Multisegment)
                  else
                  (self._unite_with_raw_multisegment(
                          to_pairs_sequence(other.raw()))
                   if isinstance(other, Contour)
                   else
                   (self._symmetric_subtract_raw_multipolygon([other.raw()])
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
        return (abs(vertices.region_signed_area(self._border._vertices))
                - sum(abs(vertices.region_signed_area(hole._vertices))
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
        >>> polygon.border
        Contour([Point(0, 0), Point(6, 0), Point(6, 6), Point(0, 6)])
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
        x_numerator, y_numerator, double_area = polygon_to_centroid_components(
                self)
        divisor = 3 * double_area[-1]
        return Point(robust_divide(x_numerator[-1], divisor),
                     robust_divide(y_numerator[-1], divisor))

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
                else Polygon(Contour(to_convex_hull(self._border.vertices))))

    @property
    def holes(self) -> List[Contour]:
        """
        Returns holes of the polygon.

        Time complexity:
            ``O(holes_count)``
        Memory complexity:
            ``O(holes_count)``

        where ``holes_count = len(self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.holes
        [Contour([Point(2, 2), Point(2, 4), Point(4, 4), Point(4, 2)])]
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
                and vertices.form_convex_polygon(self._border._vertices))

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
        return (self._distance_to_raw_point(other.raw())
                if isinstance(other, Point)
                else
                (non_negative_min(self._distance_to_raw_point(raw_point)
                                  for raw_point in other._raw)
                 if isinstance(other, Multipoint)
                 else
                 (self._distance_to_raw_segment(other.raw())
                  if isinstance(other, Segment)
                  else
                  (non_negative_min(self._distance_to_raw_segment(raw_segment)
                                    for raw_segment in other._raw)
                   if isinstance(other, Multisegment)
                   else
                   (non_negative_min(
                           self._distance_to_raw_segment(raw_segment)
                           for raw_segment in to_pairs_iterable(other._raw))
                    if isinstance(other, Contour)
                    else
                    ((non_negative_min(
                            self._linear_distance_to_raw_segment(raw_segment)
                            for raw_segment in polygon_to_raw_edges(other))
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
        graph = polygon_trapezoidal(self._raw_border, self._raw_holes)
        self._raw_locate = graph.locate
        tree = segmental.Tree(list(polygon_to_raw_edges(self)),
                              node_cls=SegmentalSquaredDistanceNode)
        if self._raw_holes:
            contours_offsets = tuple(
                    accumulate(chain((0, len(self._raw_border)),
                                     map(len, self._raw_holes))))
            self._raw_point_nearest_path, self._raw_segment_nearest_path = (
                partial(_tree_to_raw_point_nearest_path, tree,
                        contours_offsets),
                partial(_tree_to_raw_segment_nearest_path, tree,
                        contours_offsets))
        else:
            self._raw_point_nearest_path, self._raw_segment_nearest_path = (
                partial(_tree_to_holeless_raw_point_nearest_path, tree),
                partial(_tree_to_holeless_raw_segment_nearest_path, tree))

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
        return self._raw_locate(point.raw())

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
        raw = self._raw_border, self._raw_holes
        return (segment_in_polygon(other.raw(), raw)
                if isinstance(other, Segment)
                else (multisegment_in_polygon(other.raw(), raw)
                      if isinstance(other, Multisegment)
                      else (contour_in_polygon(other.raw(), raw)
                            if isinstance(other, Contour)
                            else (polygon_in_polygon((other._raw_border,
                                                      other._raw_holes),
                                                     raw)
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

    def triangulate(self) -> List['Polygon']:
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
        >>> (polygon.triangulate()
        ...  == [Polygon.from_raw(([(4, 4), (6, 0), (6, 6)], [])),
        ...      Polygon.from_raw(([(4, 2), (6, 0), (4, 4)], [])),
        ...      Polygon.from_raw(([(0, 6), (4, 4), (6, 6)], [])),
        ...      Polygon.from_raw(([(0, 0), (2, 2), (0, 6)], [])),
        ...      Polygon.from_raw(([(0, 0), (6, 0), (4, 2)], [])),
        ...      Polygon.from_raw(([(0, 6), (2, 4), (4, 4)], [])),
        ...      Polygon.from_raw(([(0, 6), (2, 2), (2, 4)], [])),
        ...      Polygon.from_raw(([(0, 0), (4, 2), (2, 2)], []))])
        True
        """
        return [Polygon(Contour.from_raw(raw_contour))
                for raw_contour in constrained_delaunay_triangles(
                    self._raw_border, self._raw_holes)]

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
            relation = region_in_multiregion(self._raw_border, self._raw_holes)
            if (relation is not Relation.COVER
                    and relation is not Relation.ENCLOSES):
                raise ValueError('Holes should lie inside border.')

    def _distance_to_raw_point(self, other: RawPoint) -> Coordinate:
        return (raw_segment_point_distance(
                self._path_to_raw_edge(self._raw_point_nearest_path(other)),
                other)
                if self._raw_locate(other) is Location.EXTERIOR
                else 0)

    def _distance_to_raw_segment(self, other: RawSegment) -> Coordinate:
        other_start, other_end = other
        return (self._linear_distance_to_raw_segment(other)
                if (self._raw_locate(other_start) is Location.EXTERIOR
                    and self._raw_locate(other_end) is Location.EXTERIOR)
                else 0)

    def _intersect_with_raw_multisegment(self,
                                         raw_multisegment: RawMultisegment
                                         ) -> Compound:
        return from_raw_mix_components(
                *complete_intersect_multisegment_with_multipolygon(
                        raw_multisegment,
                        [(self._raw_border, self._raw_holes)],
                        accurate=False))

    def _linear_distance_to_raw_segment(self, other: RawSegment
                                        ) -> Coordinate:
        return raw_segments_distance(
                self._path_to_raw_edge(self._raw_segment_nearest_path(other)),
                other)

    def _path_to_raw_edge(self, path: Tuple[int, int]) -> RawSegment:
        contour_id, edge_index = path
        raw_contour = (self._holes[contour_id - 1]
                       if contour_id
                       else self._border)._raw
        return raw_contour[edge_index - 1], raw_contour[edge_index]

    def _subtract_from_raw_multisegment(self, other_raw: RawMultisegment
                                        ) -> Compound:
        return from_raw_multisegment(subtract_multipolygon_from_multisegment(
                other_raw, [(self._raw_border, self._raw_holes)],
                accurate=False))

    def _subtract_raw_multipolygon(self, raw_multipolygon: RawMultipolygon
                                   ) -> Compound:
        return from_raw_multipolygon(subtract_multipolygons(
                [(self._raw_border, self._raw_holes)], raw_multipolygon,
                accurate=False))

    def _symmetric_subtract_raw_multipolygon(self,
                                             raw_multipolygon: RawMultipolygon
                                             ) -> Compound:
        return from_raw_multipolygon(symmetric_subtract_multipolygons(
                [(self._raw_border, self._raw_holes)], raw_multipolygon,
                accurate=False))

    def _unite_with_multipoint(self, other: Multipoint) -> Compound:
        # importing here to avoid cyclic imports
        from gon.mixed.mix import from_mix_components
        return from_mix_components(other - self, EMPTY, self)

    def _unite_with_raw_multisegment(self, other_raw: RawMultisegment
                                     ) -> Compound:
        raw_multipolygon = [(self._raw_border, self._raw_holes)]
        raw_multisegment = subtract_multipolygon_from_multisegment(
                other_raw, raw_multipolygon,
                accurate=False)
        return from_raw_mix_components([], raw_multisegment, raw_multipolygon)

    def _unite_with_raw_multipolygon(self, raw_multipolygon: RawMultipolygon
                                     ) -> Compound:
        return from_raw_multipolygon(unite_multipolygons([(self._raw_border,
                                                           self._raw_holes)],
                                                         raw_multipolygon,
                                                         accurate=False))


def polygon_to_centroid_components(polygon: Polygon
                                   ) -> Tuple[Expansion, Expansion, Expansion]:
    (x_numerator, y_numerator,
     double_area) = _raw_contour_to_centroid_components(
            polygon._border.to_counterclockwise().raw())
    for hole in polygon._holes:
        (hole_x_numerator, hole_y_numerator,
         hole_double_area) = _raw_contour_to_centroid_components(
                hole.to_clockwise().raw())
        x_numerator, y_numerator, double_area = (
            sum_expansions(x_numerator, hole_x_numerator),
            sum_expansions(y_numerator, hole_y_numerator),
            sum_expansions(double_area, hole_double_area))
    return x_numerator, y_numerator, double_area


def polygon_to_raw_edges(polygon: Polygon) -> Iterator[RawSegment]:
    return chain(to_pairs_iterable(polygon._raw_border),
                 flatten(to_pairs_iterable(raw_hole)
                         for raw_hole in polygon._raw_holes))


def raw_locate_point(raw_polygon: RawPolygon, raw_point: RawPoint) -> Location:
    relation = point_in_polygon(raw_point, raw_polygon)
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


def _raw_contour_to_centroid_components(contour: RawContour
                                        ) -> Tuple[Expansion, Expansion,
                                                   Expansion]:
    double_area = x_numerator = y_numerator = (0,)
    prev_x, prev_y = contour[-1]
    for x, y in contour:
        area_component = _to_endpoints_cross_product_z(prev_x, prev_y, x, y)
        x_numerator, y_numerator, double_area = (
            sum_expansions(x_numerator,
                           scale_expansion(area_component, prev_x + x)),
            sum_expansions(y_numerator,
                           scale_expansion(area_component, prev_y + y)),
            sum_expansions(double_area, area_component))
        prev_x, prev_y = x, y
    return x_numerator, y_numerator, double_area


def _to_endpoints_cross_product_z(start_x: Coordinate,
                                  start_y: Coordinate,
                                  end_x: Coordinate,
                                  end_y: Coordinate) -> Expansion:
    minuend, minuend_tail = two_product(start_x, end_y)
    subtrahend, subtrahend_tail = two_product(start_y, end_x)
    return (two_two_diff(minuend, minuend_tail, subtrahend, subtrahend_tail)
            if minuend_tail or subtrahend_tail
            else (minuend - subtrahend,))


def _to_raw_point_nearest_path(raw_border: RawContour,
                               raw_holes: List[RawContour],
                               raw_point: RawPoint) -> Tuple[int, int]:
    vertex = raw_border[-1]
    enumerated_vertices = enumerate(raw_border)
    min_contour_index = 0
    min_edge_index, next_vertex = next(enumerated_vertices)
    squared_distance_to_point = partial(squared_raw_point_segment_distance,
                                        raw_point)
    min_squared_distance = squared_distance_to_point((vertex, next_vertex))
    vertex = next_vertex
    for edge_index, next_vertex in enumerated_vertices:
        candidate_squared_distance = squared_distance_to_point((vertex,
                                                                next_vertex))
        if candidate_squared_distance < min_squared_distance:
            min_edge_index, min_squared_distance = (edge_index,
                                                    candidate_squared_distance)
        vertex = next_vertex
    for contour_index, raw_hole in enumerate(raw_holes,
                                             start=1):
        vertex = raw_hole[-1]
        for edge_index, next_vertex in enumerate(raw_hole):
            candidate_squared_distance = squared_distance_to_point(
                    (vertex, next_vertex))
            if candidate_squared_distance < min_squared_distance:
                (min_contour_index, min_edge_index, min_squared_distance) = (
                    contour_index, edge_index, candidate_squared_distance)
            vertex = next_vertex
    return min_contour_index, min_edge_index


def _to_raw_segment_nearest_path(raw_border: RawContour,
                                 raw_holes: List[RawContour],
                                 raw_segment: RawSegment) -> Tuple[int, int]:
    vertex = raw_border[-1]
    enumerated_vertices = enumerate(raw_border)
    min_contour_index = 0
    min_edge_index, next_vertex = next(enumerated_vertices)
    squared_distance_to_segment = partial(squared_raw_segments_distance,
                                          raw_segment)
    min_squared_distance = squared_distance_to_segment((vertex, next_vertex))
    vertex = next_vertex
    for index, next_vertex in enumerated_vertices:
        candidate_squared_distance = squared_distance_to_segment((vertex,
                                                                  next_vertex))
        if candidate_squared_distance < min_squared_distance:
            min_edge_index, min_squared_distance = (index,
                                                    candidate_squared_distance)
        vertex = next_vertex
    for contour_index, raw_hole in enumerate(raw_holes,
                                             start=1):
        vertex = raw_hole[-1]
        for edge_index, next_vertex in enumerate(raw_hole):
            candidate_squared_distance = squared_distance_to_segment(
                    (vertex, next_vertex))
            if candidate_squared_distance < min_squared_distance:
                (min_contour_index, min_edge_index, min_squared_distance) = (
                    contour_index, edge_index, candidate_squared_distance)
            vertex = next_vertex
    return min_contour_index, min_edge_index


def _tree_to_holeless_raw_point_nearest_path(tree: segmental.Tree,
                                             raw_point: RawPoint
                                             ) -> Tuple[int, int]:
    return 0, tree.nearest_to_point_index(raw_point)


def _tree_to_holeless_raw_segment_nearest_path(tree: segmental.Tree,
                                               raw_segment: RawSegment
                                               ) -> Tuple[int, int]:
    return 0, tree.nearest_index(raw_segment)


def _tree_to_raw_point_nearest_path(tree: segmental.Tree,
                                    contours_offsets: Tuple[int, ...],
                                    raw_point: RawPoint) -> Tuple[int, int]:
    index = tree.nearest_to_point_index(raw_point)
    contour_index = bisect(contours_offsets, index) - 1
    return contour_index, index - contours_offsets[contour_index]


def _tree_to_raw_segment_nearest_path(tree: segmental.Tree,
                                      contours_offsets: Tuple[int, ...],
                                      raw_segment: RawSegment
                                      ) -> Tuple[int, int]:
    index = tree.nearest_index(raw_segment)
    contour_index = bisect(contours_offsets, index) - 1
    return contour_index, index - contours_offsets[contour_index]
