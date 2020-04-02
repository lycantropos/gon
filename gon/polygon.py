from typing import (Iterable,
                    List,
                    Optional,
                    Sequence,
                    Tuple)
from weakref import WeakKeyDictionary

from memoir import cached
from orient.planar import (PointLocation,
                           contours_in_contour,
                           point_in_polygon)
from reprit.base import generate_repr
from sect.triangulation import constrained_delaunay_triangles

from .angular import (Orientation,
                      to_orientation)
from .contour import (Contour,
                      RawContour,
                      forms_convex_polygon,
                      to_area)
from .geometry import Geometry
from .hints import Coordinate
from .point import Point

RawPolygon = Tuple[RawContour, List[RawContour]]


class Polygon(Geometry):
    __slots__ = ('_border', '_holes')

    def __init__(self, border: Contour,
                 holes: Optional[Sequence[Contour]] = None) -> None:
        self._border = border
        self._holes = tuple(holes or ())

    __repr__ = generate_repr(__init__)

    @cached.map_(WeakKeyDictionary())
    def raw(self) -> RawPolygon:
        return self._border.raw(), [hole.raw() for hole in self._holes]

    @classmethod
    def from_raw(cls, raw: RawPolygon) -> 'Polygon':
        raw_border, raw_holes = raw
        return cls(Contour.from_raw(raw_border),
                   [Contour.from_raw(raw_hole) for raw_hole in raw_holes])

    def validate(self) -> None:
        raw_border, raw_holes = self.raw()
        if not contours_in_contour(raw_holes, raw_border):
            raise ValueError('Holes should lie inside border.')

    def __contains__(self, point: Point) -> bool:
        """Checks if the point lies inside the polygon or on its boundary."""
        return (point_in_polygon(point.raw(), self.raw())
                is not PointLocation.EXTERNAL)

    def __eq__(self, other: 'Polygon') -> bool:
        """
        Checks if polygons are equal.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon == polygon
        True
        """
        return (self._border == other._border and self._holes == other._holes
                if isinstance(other, Polygon)
                else NotImplemented)

    def __hash__(self) -> int:
        """
        Returns hash value of the polygon.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (4, 2), (4, 4), (2, 4)]]))
        >>> hash(polygon) == hash(polygon)
        True
        """
        return hash((self._border, self._holes))

    @property
    def border(self) -> Contour:
        """Returns border of the polygon."""
        return self._border

    @property
    def holes(self) -> Sequence[Contour]:
        """Returns holes of the polygon."""
        return self._holes

    @cached.property_
    def normalized(self) -> 'Polygon':
        return Polygon(self._border.normalized.to_counterclockwise(),
                       sorted([hole.normalized.to_clockwise()
                               for hole in self._holes],
                              key=lambda contour: contour.vertices[0]))

    @cached.property_
    def area(self) -> Coordinate:
        """
        Returns area of the polygon.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (4, 2), (4, 4), (2, 4)]]))
        >>> polygon.area == 32
        True
        """
        return to_area(self._border) - sum(to_area(hole)
                                           for hole in self._holes)

    @cached.property_
    def convex_hull(self) -> 'Polygon':
        """
        Returns convex hull of the polygon.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (4, 2), (4, 4), (2, 4)]]))
        >>> polygon.convex_hull == Polygon(polygon.border, [])
        True
        """
        if len(self._border.vertices) == 3 and not self._holes:
            return Polygon(self._border, self._holes)
        return Polygon(Contour(_to_convex_hull(self._border.vertices)), [])

    @cached.property_
    def is_convex(self) -> bool:
        """
        Checks if the polygon is convex.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (4, 2), (4, 4), (2, 4)]]))
        >>> polygon.is_convex
        False
        >>> polygon.convex_hull.is_convex
        True
        """
        return not self._holes and forms_convex_polygon(self._border)

    @property
    def triangulation(self) -> Sequence['Polygon']:
        """
        Returns triangulation of the polygon.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (4, 2), (4, 4), (2, 4)]]))
        >>> (polygon.triangulation 
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
        return [Polygon(Contour.from_raw(vertices), [])
                for vertices in constrained_delaunay_triangles(*self.raw())]


def _to_convex_hull(points: Sequence[Point]) -> List[Point]:
    points = sorted(points)
    lower = _to_sub_hull(points)
    upper = _to_sub_hull(reversed(points))
    return lower[:-1] + upper[:-1]


def _to_sub_hull(points: Iterable[Point]) -> List[Point]:
    result = []
    for point in points:
        while len(result) >= 2:
            if to_orientation(result[-1], result[-2],
                              point) is not Orientation.COUNTERCLOCKWISE:
                del result[-1]
            else:
                break
        result.append(point)
    return result
