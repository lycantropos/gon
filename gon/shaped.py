from typing import (Iterable,
                    List,
                    Optional,
                    Sequence,
                    Tuple)

from orient.planar import (PointLocation,
                           contours_in_contour,
                           point_in_polygon)
from reprit.base import generate_repr
from sect.triangulation import constrained_delaunay_triangles

from .angular import (Orientation,
                      to_orientation)
from .geometry import Geometry
from .hints import Coordinate
from .linear import (Contour,
                     RawContour,
                     forms_convex_polygon,
                     to_area)
from .primitive import Point

RawPolygon = Tuple[RawContour, List[RawContour]]


class Polygon(Geometry):
    __slots__ = '_border', '_holes', '_raw_border', '_raw_holes'

    def __init__(self, border: Contour,
                 holes: Optional[Sequence[Contour]] = None) -> None:
        holes = tuple(holes or ())
        self._border, self._holes = border, holes
        self._raw_border, self._raw_holes = border.raw(), [hole.raw()
                                                           for hole in holes]

    __repr__ = generate_repr(__init__)

    def raw(self) -> RawPolygon:
        return self._raw_border[:], [raw_hole[:]
                                     for raw_hole in self._raw_holes]

    @classmethod
    def from_raw(cls, raw: RawPolygon) -> 'Polygon':
        raw_border, raw_holes = raw
        return cls(Contour.from_raw(raw_border),
                   [Contour.from_raw(raw_hole) for raw_hole in raw_holes])

    def validate(self) -> None:
        self._border.validate()
        for hole in self._holes:
            hole.validate()
        if not contours_in_contour(self._raw_holes, self._raw_border):
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
        if self is other:
            return True
        return (self._border == other._border and self._holes == other._holes
                if isinstance(other, Polygon)
                else NotImplemented)

    def __hash__(self) -> int:
        """
        Returns hash value of the polygon.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> hash(polygon) == hash(polygon)
        True
        """
        return hash((self._border, self._holes))

    @property
    def border(self) -> Contour:
        """Returns border of the polygon."""
        return self._border

    @property
    def holes(self) -> List[Contour]:
        """Returns holes of the polygon."""
        return list(self._holes)

    @property
    def normalized(self) -> 'Polygon':
        """
        Returns polygon in normalized form.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.normalized == polygon
        True
        """
        return Polygon(self._border.normalized.to_counterclockwise(),
                       sorted([hole.normalized.to_clockwise()
                               for hole in self._holes],
                              key=lambda contour: contour._vertices[:2]))

    @property
    def area(self) -> Coordinate:
        """
        Returns area of the polygon.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.area == 32
        True
        """
        return to_area(self._border) - sum(to_area(hole)
                                           for hole in self._holes)

    @property
    def convex_hull(self) -> 'Polygon':
        """
        Returns convex hull of the polygon.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.convex_hull == Polygon(polygon.border, [])
        True
        """
        return (self
                if self.is_convex
                else Polygon(Contour(_to_convex_hull(self._border.vertices))))

    @property
    def is_convex(self) -> bool:
        """
        Checks if the polygon is convex.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
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
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
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
        return [Polygon(Contour.from_raw(raw_contour))
                for raw_contour in constrained_delaunay_triangles(
                    self._raw_border, self._raw_holes)]


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
