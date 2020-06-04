from functools import partial
from typing import (List,
                    Sequence)

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
        return isinstance(other, Point) and bool(self._locate(other))

    def __eq__(self, other: 'Multipolygon') -> bool:
        return (self is other
                or (self._polygons_set == other._polygons_set
                    if isinstance(other, Multipolygon)
                    else (False
                          if isinstance(other, Geometry)
                          else NotImplemented)))

    def __ge__(self, other: Compound) -> bool:
        return (other is EMPTY
                or self == other
                or (self.relate(other) in (Relation.EQUAL, Relation.COMPONENT,
                                           Relation.ENCLOSED, Relation.WITHIN)
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __gt__(self, other: Compound) -> bool:
        return (other is EMPTY
                or self != other
                and (self.relate(other) in (Relation.COMPONENT,
                                            Relation.ENCLOSED, Relation.WITHIN)
                     if isinstance(other, Compound)
                     else NotImplemented))

    def __hash__(self) -> int:
        return hash(self._polygons_set)

    def __le__(self, other: Compound) -> bool:
        return (self == other
                or (not isinstance(other, (Multipoint, Linear))
                    and self.relate(other) in (Relation.COVER,
                                               Relation.ENCLOSES,
                                               Relation.COMPOSITE,
                                               Relation.EQUAL)
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __lt__(self, other: Compound) -> bool:
        return (self != other
                and (not isinstance(other, (Multipoint, Linear))
                     and self.relate(other) in (Relation.COVER,
                                                Relation.ENCLOSES,
                                                Relation.COMPOSITE)
                     if isinstance(other, Compound)
                     else NotImplemented))

    @classmethod
    def from_raw(cls, raw: RawMultipolygon) -> 'Multipolygon':
        return cls(*map(Polygon.from_raw, raw))

    @property
    def area(self) -> Coordinate:
        return sum(polygon.area for polygon in self._polygons)

    @property
    def perimeter(self) -> Coordinate:
        return sum(polygon.perimeter for polygon in self._polygons)

    @property
    def polygons(self) -> List[Polygon]:
        return list(self._polygons)

    def index(self) -> None:
        for polygon in self._polygons:
            polygon.index()

    def locate(self, point: Point) -> Location:
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
