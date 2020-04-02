from typing import (Iterable,
                    List,
                    Optional,
                    Sequence,
                    Tuple)

from memoir import cached
from orient.planar import (PointLocation,
                           contours_in_contour,
                           point_in_polygon)
from reprit.base import generate_repr
from sect.triangulation import constrained_delaunay_triangles

from . import documentation
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


@documentation.setup(docstring='The Polygon constructor takes two parameters. '
                               'The first is a sequence of Point tuples. '
                               'The second is an optional sequence of '
                               'contours specifying the interior "holes" of '
                               'the polygon.',
                     reference='http://tiny.cc/n_gon')
class Polygon(Geometry):
    __slots__ = ('_border', '_holes')

    def __init__(self, border: Contour,
                 holes: Optional[Sequence[Contour]] = None) -> None:
        self._border = border
        self._holes = tuple(holes or ())

    __repr__ = generate_repr(__init__)

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

    @documentation.setup(docstring='Locates the point '
                                   'in relation to the polygon.')
    def locate(self, point: Point) -> PointLocation:
        """
        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon.locate(Point(0, 0)) is PointLocation.BOUNDARY
        True
        >>> polygon.locate(Point(1, 1)) is PointLocation.INTERNAL
        True
        >>> polygon.locate(Point(2, 2)) is PointLocation.BOUNDARY
        True
        >>> polygon.locate(Point(3, 3)) is PointLocation.EXTERNAL
        True
        >>> polygon.locate(Point(4, 4)) is PointLocation.BOUNDARY
        True
        >>> polygon.locate(Point(3, 5)) is PointLocation.INTERNAL
        True
        >>> polygon.locate(Point(2, 6)) is PointLocation.BOUNDARY
        True
        >>> polygon.locate(Point(1, 7)) is PointLocation.EXTERNAL
        True
        """
        return point_in_polygon(point.raw(), self.raw())

    def __contains__(self, point: Point) -> bool:
        """Checks if the point lies inside the polygon or on its boundary."""
        return self.locate(point) is not PointLocation.EXTERNAL

    @documentation.setup(docstring='Checks if polygons are equal.')
    def __eq__(self, other: 'Polygon') -> bool:
        """
        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (2, 4), (4, 4), (4, 2)]]))
        >>> polygon == polygon
        True
        """
        return (self._border == other._border and self._holes == other._holes
                if isinstance(other, Polygon)
                else NotImplemented)

    @documentation.setup(docstring='Returns hash value of the polygon.')
    def __hash__(self) -> int:
        """
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
    @documentation.setup(docstring='Returns area of the polygon.')
    def area(self) -> Coordinate:
        """
        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (4, 2), (4, 4), (2, 4)]]))
        >>> polygon.area == 32
        True
        """
        return to_area(self._border) - sum(to_area(hole)
                                           for hole in self._holes)

    @cached.property_
    @documentation.setup(docstring='Returns convex hull of the polygon.')
    def convex_hull(self) -> 'Polygon':
        """
        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (4, 2), (4, 4), (2, 4)]]))
        >>> polygon.convex_hull == Polygon(polygon.border, [])
        True
        """
        if len(self._border.vertices) == 3 and not self._holes:
            return Polygon(self._border, self._holes)
        return Polygon(Contour(_to_convex_hull(self._border.vertices)), [])

    @cached.property_
    @documentation.setup(docstring='Checks if the polygon is convex.',
                         origin='property that each internal angle '
                                'of convex polygon is less than 180 degrees',
                         reference='http://tiny.cc/convex_polygon',
                         time_complexity='O(n), where\n'
                                         'n -- polygon\'s vertices count')
    def is_convex(self) -> bool:
        """
        >>> polygon = Polygon.from_raw(([(0, 0), (6, 0), (6, 6), (0, 6)],
        ...                             [[(2, 2), (4, 2), (4, 4), (2, 4)]]))
        >>> polygon.is_convex
        False
        >>> polygon.convex_hull.is_convex
        True
        """
        return not self._holes and forms_convex_polygon(self._border)

    @property
    @documentation.setup(docstring='Returns triangulation of the polygon.',
                         origin='constrained Delaunay triangulation',
                         reference='http://tiny.cc/delaunay_triangulation\n'
                                   'http://tiny.cc/constrained_delaunay',
                         time_complexity='O(n * log n) for convex polygons,\n'
                                         'O(n^2) for concave polygons, where\n'
                                         'n -- polygon\'s vertices count')
    def triangulation(self) -> Sequence['Polygon']:
        """
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
