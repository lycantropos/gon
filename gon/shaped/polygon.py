from functools import partial
from typing import (List,
                    Optional,
                    Sequence)

from clipping.planar import (complete_intersect_multipolygons,
                             complete_intersect_multisegment_with_multipolygon,
                             subtract_multipolygon_from_multisegment,
                             subtract_multipolygons,
                             symmetric_subtract_multipolygons,
                             unite_multipolygons)
from orient.planar import (contour_in_polygon,
                           multisegment_in_polygon,
                           point_in_polygon,
                           polygon_in_polygon,
                           region_in_multiregion,
                           segment_in_polygon)
from reprit.base import generate_repr
from sect.decomposition import polygon_trapezoidal
from sect.triangulation import constrained_delaunay_triangles

from gon.compound import (Compound,
                          Indexable,
                          Linear,
                          Location,
                          Relation,
                          Shaped)
from gon.degenerate import EMPTY
from gon.discrete import Multipoint
from gon.geometry import Geometry
from gon.hints import Coordinate
from gon.linear import (Contour,
                        Multisegment,
                        RawMultisegment,
                        Segment,
                        vertices)
from gon.linear.utils import (from_raw_multisegment,
                              to_pairs_chain)
from gon.primitive import (Point,
                           RawPoint)
from .hints import (RawMultipolygon,
                    RawPolygon)
from .utils import (from_raw_mix_components,
                    from_raw_multipolygon,
                    to_convex_hull)


class Polygon(Indexable, Shaped):
    __slots__ = ('_border', '_holes', '_holes_set',
                 '_raw_border', '_raw_holes', '_raw_locate')

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
                              to_pairs_chain(other.raw()))
                       if isinstance(other, Contour)
                       else (self._intersect_with_raw_multipolygon(
                              [(other._raw_border, other._raw_holes)])
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
                          to_pairs_chain(other.raw()))
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
                              to_pairs_chain(other.raw()))
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
                          to_pairs_chain(other.raw()))
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

    def index(self) -> None:
        """
        Pre-processes polygon to potentially improve queries.

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
        return isinstance(point, Point) and self._raw_locate(point.raw())

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

    def _intersect_with_raw_multipolygon(self,
                                         raw_multipolygon: RawMultipolygon
                                         ) -> Compound:
        return from_raw_mix_components(*complete_intersect_multipolygons(
                [(self._raw_border, self._raw_holes)], raw_multipolygon,
                accurate=False))

    def _intersect_with_raw_multisegment(self,
                                         raw_multisegment: RawMultisegment
                                         ) -> Compound:
        return from_raw_mix_components(
                *complete_intersect_multisegment_with_multipolygon(
                        raw_multisegment,
                        [(self._raw_border, self._raw_holes)],
                        accurate=False))

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


def raw_locate_point(raw_polygon: RawPolygon, raw_point: RawPoint) -> Location:
    relation = point_in_polygon(raw_point, raw_polygon)
    return (Location.EXTERIOR
            if relation is Relation.DISJOINT
            else (Location.BOUNDARY
                  if relation is Relation.COMPONENT
                  else Location.INTERIOR))
