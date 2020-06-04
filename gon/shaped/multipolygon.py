from functools import partial
from typing import (List,
                    Sequence)

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
                        Segment)
from gon.primitive import Point
from .hints import RawMultipolygon
from .polygon import Polygon


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
            ``O(min(len(self.polygons), len(other.polygons)))``
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
                or (not isinstance(other, (Multipoint, Linear))
                    and self.relate(other) in (Relation.COVER,
                                               Relation.ENCLOSES,
                                               Relation.COMPOSITE,
                                               Relation.EQUAL)
                    if isinstance(other, Compound)
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
                and (not isinstance(other, (Multipoint, Linear))
                     and self.relate(other) in (Relation.COVER,
                                                Relation.ENCLOSES,
                                                Relation.COMPOSITE)
                     if isinstance(other, Compound)
                     else NotImplemented))

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
        return [(raw_border, [raw_hole[:] for raw_hole in raw_holes])
                for raw_border, raw_holes in self._raw]

    def relate(self, other: Compound) -> Relation:
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

    def validate(self) -> None:
        if not self._polygons:
            raise ValueError('Multipolygon is empty.')
        elif len(self._polygons) > len(self._polygons_set):
            raise ValueError('Duplicate polygons found.')
        for polygon in self._polygons:
            polygon.validate()


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
