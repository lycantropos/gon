from functools import partial
from itertools import chain
from typing import (List,
                    Sequence)

from clipping.planar import (complete_intersect_multipolygons,
                             complete_intersect_multisegment_with_multipolygon,
                             subtract_multipolygon_from_multisegment,
                             subtract_multipolygons,
                             symmetric_subtract_multipolygons,
                             unite_multipolygons)
from locus import r
from orient.planar import (contour_in_multipolygon,
                           multipolygon_in_multipolygon,
                           multisegment_in_multipolygon,
                           polygon_in_multipolygon,
                           segment_in_multipolygon)
from reprit.base import generate_repr
from sect.decomposition import Location

from gon.compound import (Compound,
                          Indexable,
                          Linear,
                          Relation,
                          Shaped)
from gon.degenerate import EMPTY
from gon.discrete import Multipoint
from gon.geometry import Geometry
from gon.hints import Coordinate
from gon.linear import (Contour,
                        Multisegment,
                        RawMultisegment,
                        Segment)
from gon.linear.utils import (from_raw_multisegment,
                              to_pairs_chain)
from gon.primitive import Point
from .hints import RawMultipolygon
from .polygon import Polygon
from .utils import (from_raw_mix_components,
                    from_raw_multipolygon)


class Multipolygon(Indexable, Shaped):
    __slots__ = '_polygons', '_polygons_set', '_raw', '_locate'

    def __init__(self, *polygons: Polygon) -> None:
        """
        Initializes multipolygon.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in polygons)``.
        """
        self._polygons = polygons
        self._polygons_set = frozenset(polygons)
        self._raw = [polygon.raw() for polygon in polygons]
        self._locate = partial(locate_point_in_polygons, self._polygons)

    __repr__ = generate_repr(__init__)

    def __and__(self, other: Compound) -> Compound:
        """
        Returns intersection of the multipolygon with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in self.polygons)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> (multipolygon & multipolygon
        ...  == Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                      [[(2, 2), (2, 4), (4, 4), (4, 2)]])))
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
                       else
                       (self._intersect_with_raw_multipolygon([other.raw()])
                        if isinstance(other, Polygon)
                        else (self._intersect_with_raw_multipolygon(other._raw)
                              if isinstance(other, Multipolygon)
                              else NotImplemented)))))

    __rand__ = __and__

    def __contains__(self, other: Geometry) -> bool:
        """
        Checks if the multipolygon contains the other geometry.

        Time complexity:
            ``O(log vertices_count)`` expected after indexing,
            ``O(vertices_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in self.polygons)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> Point(0, 0) in multipolygon
        True
        >>> Point(1, 1) in multipolygon
        True
        >>> Point(2, 2) in multipolygon
        True
        >>> Point(3, 3) in multipolygon
        False
        >>> Point(4, 3) in multipolygon
        True
        >>> Point(5, 2) in multipolygon
        True
        >>> Point(6, 1) in multipolygon
        True
        >>> Point(7, 0) in multipolygon
        False
        """
        return isinstance(other, Point) and bool(self._locate(other))

    def __eq__(self, other: 'Multipolygon') -> bool:
        """
        Checks if multipolygons are equal.

        Time complexity:
            ``O(len(self.polygons))``
        Memory complexity:
            ``O(1)``

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> multipolygon == multipolygon
        True
        """
        return (self is other
                or (self._polygons_set == other._polygons_set
                    if isinstance(other, Multipolygon)
                    else (False
                          if isinstance(other, Geometry)
                          else NotImplemented)))

    def __ge__(self, other: Compound) -> bool:
        """
        Checks if the multipolygon is a superset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(1)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in self.polygons)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> multipolygon >= multipolygon
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
        Checks if the multipolygon is a strict superset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(1)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in self.polygons)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> multipolygon > multipolygon
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
            ``O(len(self.polygons))``
        Memory complexity:
            ``O(1)``

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> hash(multipolygon) == hash(multipolygon)
        True
        """
        return hash(self._polygons_set)

    def __le__(self, other: Compound) -> bool:
        """
        Checks if the multipolygon is a subset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(1)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in self.polygons)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> multipolygon <= multipolygon
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
        Checks if the multipolygon is a strict subset of the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(1)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in self.polygons)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> multipolygon < multipolygon
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
        Returns union of the multipolygon with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in self.polygons)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> (multipolygon | multipolygon
        ...  == Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                      [[(2, 2), (2, 4), (4, 4), (4, 2)]])))
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
                         else (self._unite_with_raw_multipolygon(other._raw)
                               if isinstance(other, Multipolygon)
                               else NotImplemented))))))

    __ror__ = __or__

    def __rsub__(self, other: Compound) -> Compound:
        """
        Returns difference of the other geometry with the multipolygon.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in self.polygons)``.
        """
        return (self._subtract_from_raw_multisegment([other.raw()])
                if isinstance(other, Segment)
                else (self._subtract_from_raw_multisegment(other.raw())
                      if isinstance(other, Multisegment)
                      else
                      (self._subtract_from_raw_multisegment(
                              to_pairs_chain(other.raw()))
                       if isinstance(other, Contour)
                       else (self._subtract_from_raw_multipolygon(
                              [other.raw()])
                             if isinstance(other, Polygon)
                             else NotImplemented))))

    def __sub__(self, other: Compound) -> Compound:
        """
        Returns difference of the multipolygon with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in self.polygons)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> multipolygon - multipolygon is EMPTY
        True
        """
        return (self
                if isinstance(other, (Linear, Multipoint))
                else (self._subtract_raw_multipolygon([other.raw()])
                      if isinstance(other, Polygon)
                      else (self._subtract_raw_multipolygon(other._raw)
                            if isinstance(other, Multipolygon)
                            else NotImplemented)))

    def __xor__(self, other: Compound) -> Compound:
        """
        Returns symmetric difference of the multipolygon
        with the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in self.polygons)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> multipolygon ^ multipolygon is EMPTY
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
                    else (self._symmetric_subtract_raw_multipolygon(other._raw)
                          if isinstance(other, Multipolygon)
                          else NotImplemented))))))

    __rxor__ = __xor__

    @classmethod
    def from_raw(cls, raw: RawMultipolygon) -> 'Multipolygon':
        """
        Constructs multipolygon from the combination of Python built-ins.

        Time complexity:
            ``O(raw_vertices_count)``
        Memory complexity:
            ``O(raw_vertices_count)``

        where ``raw_vertices_count = sum(len(raw_border)\
 + sum(len(raw_hole) for raw_hole in raw_holes)\
 for raw_border, raw_holes in raw)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> (multipolygon
        ...  == Multipolygon(Polygon(Contour([Point(0, 0), Point(6, 0),
        ...                                   Point(6, 6), Point(0, 6)]),
        ...                          [Contour([Point(2, 2), Point(2, 4),
        ...                                    Point(4, 4), Point(4, 2)])])))
        True
        """
        return cls(*map(Polygon.from_raw, raw))

    @property
    def area(self) -> Coordinate:
        """
        Returns area of the multipolygon.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(1)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in self.polygons)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> multipolygon.area == 32
        True
        """
        return sum(polygon.area for polygon in self._polygons)

    @property
    def perimeter(self) -> Coordinate:
        """
        Returns perimeter of the multipolygon.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(1)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in self.polygons)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> multipolygon.perimeter == 32
        True
        """
        return sum(polygon.perimeter for polygon in self._polygons)

    @property
    def polygons(self) -> List[Polygon]:
        """
        Returns polygons of the multipolygon.

        Time complexity:
            ``O(polygons_count)``
        Memory complexity:
            ``O(polygons_count)``

        where ``polygons_count = len(self.polygons)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> multipolygon.polygons
        [Polygon(Contour([Point(0, 0), Point(6, 0), Point(6, 6),\
 Point(0, 6)]), [Contour([Point(2, 2), Point(2, 4), Point(4, 4),\
 Point(4, 2)])])]
        """
        return list(self._polygons)

    def index(self) -> None:
        """
        Pre-processes multipolygon to potentially improve queries.

        Time complexity:
            ``O(vertices_count * log vertices_count)`` expected,
            ``O(vertices_count ** 2)`` worst
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in self.polygons)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> multipolygon.index()
        """
        polygons = self._polygons
        for polygon in polygons:
            polygon.index()

        def polygon_to_interval(polygon: Polygon) -> r.Interval:
            vertices = iter(polygon.border.vertices)
            first_vertex = next(vertices)
            x_min = x_max = first_vertex.x
            y_min = y_max = first_vertex.y
            for vertex in vertices:
                x_min, x_max = min(x_min, vertex.x), max(x_max, vertex.x)
                y_min, y_max = min(y_min, vertex.y), max(y_max, vertex.y)
            return (x_min, x_max), (y_min, y_max)

        tree = r.Tree([polygon_to_interval(polygon) for polygon in polygons])
        self._locate = partial(locate_point_in_indexed_polygons,
                               tree, polygons)

    def locate(self, point: Point) -> Location:
        """
        Finds location of the point relative to the multipolygon.

        Time complexity:
            ``O(log vertices_count)`` expected after indexing,
            ``O(vertices_count)`` worst after indexing or without it
        Memory complexity:
            ``O(1)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in self.polygons)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> multipolygon.locate(Point(0, 0)) is Location.BOUNDARY
        True
        >>> multipolygon.locate(Point(1, 1)) is Location.INTERIOR
        True
        >>> multipolygon.locate(Point(2, 2)) is Location.BOUNDARY
        True
        >>> multipolygon.locate(Point(3, 3)) is Location.EXTERIOR
        True
        >>> multipolygon.locate(Point(4, 3)) is Location.BOUNDARY
        True
        >>> multipolygon.locate(Point(5, 2)) is Location.INTERIOR
        True
        >>> multipolygon.locate(Point(6, 1)) is Location.BOUNDARY
        True
        >>> multipolygon.locate(Point(7, 0)) is Location.EXTERIOR
        True
        """
        return self._locate(point)

    def raw(self) -> RawMultipolygon:
        """
        Returns the multipolygon as combination of Python built-ins.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in self.polygons)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> multipolygon.raw()
        [([(0, 0), (6, 0), (6, 6), (0, 6)],\
 [[(2, 2), (2, 4), (4, 4), (4, 2)]])]
        """
        return [(raw_border, [raw_hole[:] for raw_hole in raw_holes])
                for raw_border, raw_holes in self._raw]

    def relate(self, other: Compound) -> Relation:
        """
        Finds relation between the multipolygon and the other geometry.

        Time complexity:
            ``O(vertices_count * log vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in self.polygons)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> multipolygon.relate(multipolygon) is Relation.EQUAL
        True
        """
        return (segment_in_multipolygon(other.raw(), self._raw)
                if isinstance(other, Segment)
                else
                (multisegment_in_multipolygon(other.raw(), self._raw)
                 if isinstance(other, Multisegment)
                 else
                 (contour_in_multipolygon(other.raw(), self._raw)
                  if isinstance(other, Contour)
                  else
                  (polygon_in_multipolygon(other.raw(), self._raw)
                   if isinstance(other, Polygon)
                   else (multipolygon_in_multipolygon(other._raw, self._raw)
                         if isinstance(other, Multipolygon)
                         else other.relate(self).complement)))))

    def triangulate(self) -> List[Polygon]:
        """
        Returns triangulation of the multipolygon.

        Time complexity:
            ``O(vertices_count ** 2)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in self.polygons)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> (multipolygon.triangulate()
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
        return list(chain.from_iterable(polygon.triangulate()
                                        for polygon in self._polygons))

    def validate(self) -> None:
        """
        Checks if the multipolygon is valid.

        Time complexity:
            ``O(vertices_count * log (vertices_count))``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in self.polygons)``.

        >>> multipolygon = Multipolygon.from_raw(
        ...         [([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...           [[(2, 2), (2, 4), (4, 4), (4, 2)]])])
        >>> multipolygon.validate()
        """
        if not self._polygons:
            raise ValueError('Multipolygon is empty.')
        elif len(self._polygons) > len(self._polygons_set):
            raise ValueError('Duplicate polygons found.')
        for polygon in self._polygons:
            polygon.validate()

    def _intersect_with_raw_multipolygon(self, other_raw: RawMultipolygon
                                         ) -> Compound:
        return from_raw_mix_components(
                *complete_intersect_multipolygons(self._raw, other_raw,
                                                  accurate=False))

    def _intersect_with_raw_multisegment(self,
                                         raw_multisegment: RawMultisegment
                                         ) -> Compound:
        return from_raw_mix_components(
                *complete_intersect_multisegment_with_multipolygon(
                        raw_multisegment, self._raw,
                        accurate=False))

    def _subtract_from_raw_multipolygon(self, other_raw: RawMultipolygon
                                        ) -> Compound:
        return from_raw_multipolygon(subtract_multipolygons(other_raw,
                                                            self._raw,
                                                            accurate=False))

    def _subtract_from_raw_multisegment(self, other_raw: RawMultisegment
                                        ) -> Compound:
        return from_raw_multisegment(subtract_multipolygon_from_multisegment(
                other_raw, self._raw,
                accurate=False))

    def _subtract_raw_multipolygon(self, other_raw: RawMultipolygon
                                   ) -> Compound:
        return from_raw_multipolygon(subtract_multipolygons(self._raw,
                                                            other_raw,
                                                            accurate=False))

    def _symmetric_subtract_raw_multipolygon(self, other_raw: RawMultipolygon
                                             ) -> Compound:
        return from_raw_multipolygon(symmetric_subtract_multipolygons(
                self._raw, other_raw,
                accurate=False))

    def _unite_with_multipoint(self, other: Multipoint) -> Compound:
        # importing here to avoid cyclic imports
        from gon.mixed.mix import from_mix_components
        return from_mix_components(other - self, EMPTY, self)

    def _unite_with_raw_multisegment(self, other_raw: RawMultisegment
                                     ) -> Compound:
        raw_multisegment = subtract_multipolygon_from_multisegment(
                other_raw, self._raw,
                accurate=False)
        return from_raw_mix_components([], raw_multisegment, self._raw)

    def _unite_with_raw_multipolygon(self, other_raw: RawMultipolygon
                                     ) -> Compound:
        return from_raw_multipolygon(unite_multipolygons(self._raw, other_raw,
                                                         accurate=False))


def locate_point_in_polygons(polygons: Sequence[Polygon],
                             point: Point) -> Location:
    for polygon in polygons:
        location = polygon.locate(point)
        if location is not Location.EXTERIOR:
            return location
    return Location.EXTERIOR


def locate_point_in_indexed_polygons(tree: r.Tree, polygons: Sequence[Polygon],
                                     point: Point) -> Location:
    candidates_indices = tree.find_supersets_indices(((point.x, point.x),
                                                      (point.y, point.y)))
    for candidate_index in candidates_indices:
        location = polygons[candidate_index].locate(point)
        if location is not Location.EXTERIOR:
            return location
    return Location.EXTERIOR
