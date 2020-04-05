from typing import (Iterable,
                    List,
                    Optional,
                    Sequence,
                    Tuple)

from orient.planar import (PointLocation,
                           contours_in_contour,
                           point_in_polygon,
                           polygon_in_polygon)
from reprit.base import generate_repr
from sect.triangulation import constrained_delaunay_triangles

from .angular import (Orientation,
                      to_orientation)
from .geometry import Geometry
from .hints import Coordinate
from .linear import (Contour,
                     RawContour,
                     forms_convex_polygon,
                     to_signed_area)
from .primitive import Point

RawPolygon = Tuple[RawContour, List[RawContour]]


class Polygon(Geometry):
    __slots__ = ('_border', '_holes', '_raw_border', '_raw_holes',
                 '_normalized_border', '_normalized_holes', '_is_normalized')

    def __init__(self, border: Contour,
                 holes: Optional[Sequence[Contour]] = None,
                 *,
                 _is_normalized: bool = False) -> None:
        """
        Initializes polygon.

        Time complexity:
            ``O(vertices_count + len(self.holes) * log len(self.holes))``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(border.vertices)\
 + sum(len(hole.vertices) for hole in holes)``.
        """
        holes = tuple(holes or ())
        self._border, self._holes = border, holes
        self._raw_border, self._raw_holes = border.raw(), [hole.raw()
                                                           for hole in holes]
        self._normalized_border, self._normalized_holes = (
            (border, holes)
            if _is_normalized
            else (border.normalized.to_counterclockwise(),
                  tuple(sorted([hole.normalized.to_clockwise()
                                for hole in holes],
                               key=lambda contour: contour._vertices[:2]))))
        self._is_normalized = _is_normalized

    __repr__ = generate_repr(__init__)

    def __contains__(self, point: Point) -> bool:
        """
        Checks if the point lies inside the polygon or on its boundary.

        Time complexity:
            ``O(vertices_count)``
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
        return (point_in_polygon(point.raw(),
                                 (self._raw_border, self._raw_holes))
                is not PointLocation.EXTERNAL)

    def __eq__(self, other: 'Polygon') -> bool:
        """
        Checks if polygons are equal.

        Time complexity:
            ``O(total_vertices_count)``
        Memory complexity:
            ``O(1)``

        where ``total_vertices_count = min_border_vertices_count\
 + min_holes_vertices_count``,
        ``min_border_vertices_count =\
 min(border_vertices_count, other_border_vertices_count)``
        ``min_holes_vertices_count =\
 min(holes_vertices_count, other_holes_vertices_count)``,
        ``border_vertices_count = len(self.border.vertices)``,
        ``other_border_vertices_count = len(other.border.vertices)``
        ``holes_vertices_count =\
 sum(len(hole.vertices) for hole in self.holes)``,
        ``other_holes_vertices_count =\
 sum(len(hole.vertices) for hole in other.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon == polygon
        True
        """
        return (self is other
                or (self._normalized_border == other._normalized_border
                    and self._normalized_holes == other._normalized_holes
                    if isinstance(other, Polygon)
                    else NotImplemented))

    def __ge__(self, other: 'Polygon') -> bool:
        """
        Checks if the polygon is a superset of the other.

        Time complexity:
            ``O(total_vertices_count * log total_vertices_count)``
        Memory complexity:
            ``O(total_vertices_count)``

        where ``vertices_count = total_border_vertices_count\
 + total_holes_vertices_count``,
        ``total_border_vertices_count =\
 border_vertices_count + other_border_vertices_count``
        ``total_holes_vertices_count =\
 holes_vertices_count + other_holes_vertices_count``,
        ``border_vertices_count = len(self.border.vertices)``,
        ``other_border_vertices_count = len(other.border.vertices)``
        ``holes_vertices_count =\
 sum(len(hole.vertices) for hole in self.holes)``,
        ``other_holes_vertices_count =\
 sum(len(hole.vertices) for hole in other.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon >= polygon
        True
        >>> polygon >= polygon.convex_hull
        False
        """
        return (polygon_in_polygon((other._raw_border, other._raw_holes),
                                   (self._raw_border, self._raw_holes))
                if isinstance(other, Polygon)
                else NotImplemented)

    def __gt__(self, other: 'Polygon') -> bool:
        """
        Checks if the polygon is a strict superset of the other.

        Time complexity:
            ``O(total_vertices_count * log total_vertices_count)``
        Memory complexity:
            ``O(total_vertices_count)``

        where ``vertices_count = total_border_vertices_count\
 + total_holes_vertices_count``,
        ``total_border_vertices_count =\
 border_vertices_count + other_border_vertices_count``
        ``total_holes_vertices_count =\
 holes_vertices_count + other_holes_vertices_count``,
        ``border_vertices_count = len(self.border.vertices)``,
        ``other_border_vertices_count = len(other.border.vertices)``
        ``holes_vertices_count =\
 sum(len(hole.vertices) for hole in self.holes)``,
        ``other_holes_vertices_count =\
 sum(len(hole.vertices) for hole in other.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon > polygon
        False
        >>> polygon > polygon.convex_hull
        False
        """
        return self != other and self >= other

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
        return hash((self._normalized_border, self._normalized_holes))

    def __le__(self, other: 'Polygon') -> bool:
        """
        Checks if the polygon is a subset of the other.

        Time complexity:
            ``O(total_vertices_count * log total_vertices_count)``
        Memory complexity:
            ``O(total_vertices_count)``

        where ``vertices_count = total_border_vertices_count\
 + total_holes_vertices_count``,
        ``total_border_vertices_count =\
 border_vertices_count + other_border_vertices_count``
        ``total_holes_vertices_count =\
 holes_vertices_count + other_holes_vertices_count``,
        ``border_vertices_count = len(self.border.vertices)``,
        ``other_border_vertices_count = len(other.border.vertices)``
        ``holes_vertices_count =\
 sum(len(hole.vertices) for hole in self.holes)``,
        ``other_holes_vertices_count =\
 sum(len(hole.vertices) for hole in other.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon <= polygon
        True
        >>> polygon <= polygon.convex_hull
        True
        """
        return (polygon_in_polygon((self._raw_border, self._raw_holes),
                                   (other._raw_border, other._raw_holes))
                if isinstance(other, Polygon)
                else NotImplemented)

    def __lt__(self, other: 'Polygon') -> bool:
        """
        Checks if the polygon is a strict subset of the other.

        Time complexity:
            ``O(total_vertices_count * log total_vertices_count)``
        Memory complexity:
            ``O(total_vertices_count)``

        where ``vertices_count = total_border_vertices_count\
 + total_holes_vertices_count``,
        ``total_border_vertices_count =\
 border_vertices_count + other_border_vertices_count``
        ``total_holes_vertices_count =\
 holes_vertices_count + other_holes_vertices_count``,
        ``border_vertices_count = len(self.border.vertices)``,
        ``other_border_vertices_count = len(other.border.vertices)``
        ``holes_vertices_count =\
 sum(len(hole.vertices) for hole in self.holes)``,
        ``other_holes_vertices_count =\
 sum(len(hole.vertices) for hole in other.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon < polygon
        False
        >>> polygon < polygon.convex_hull
        True
        """
        return self != other and self <= other

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
        return (to_signed_area(self._normalized_border)
                + sum(to_signed_area(hole) for hole in self._normalized_holes))

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
                else Polygon(Contour(_to_convex_hull(self._border.vertices))))

    @property
    def holes(self) -> List[Contour]:
        """
        Returns holes of the polygon.

        Time complexity:
            ``O(len(self.holes))``
        Memory complexity:
            ``O(len(self.holes))``

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
        return not self._holes and forms_convex_polygon(self._border)

    @property
    def normalized(self) -> 'Polygon':
        """
        Returns polygon in normalized form.

        Time complexity:
            ``O(1)`` if normalized already, ``O(vertices_count)`` -- otherwise
        Memory complexity:
            ``O(1)`` if normalized already, ``O(vertices_count)`` -- otherwise

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.normalized == polygon
        True
        """
        return (self
                if self._is_normalized
                else Polygon(self._normalized_border, self._normalized_holes,
                             _is_normalized=True))

    def raw(self) -> RawPolygon:
        """
        Returns the polygon as combination of Python built-ins.

        Time complexity:
            ``O(vertices_count)``
        Memory complexity:
            ``O(vertices_count)``

        where ``vertices_count = len(self.border.vertices)\
 + sum(len(hole.vertices) for hole in self.holes)``.

        >>> contour = Contour.from_raw([(0, 0), (1, 0), (0, 1)])
        >>> contour.raw()
        [(0, 0), (1, 0), (0, 1)]
        """
        return self._raw_border[:], [raw_hole[:]
                                     for raw_hole in self._raw_holes]

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
        Checks if contours are valid.

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
        for hole in self._holes:
            hole.validate()
        if not contours_in_contour(self._raw_holes, self._raw_border):
            raise ValueError('Holes should lie inside border.')


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
