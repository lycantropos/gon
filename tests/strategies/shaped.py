from itertools import repeat
from typing import (Iterable,
                    List,
                    Sequence)

from hypothesis import strategies
from hypothesis_geometry import planar
from hypothesis_geometry.utils import to_contour
from robust.angular import (Orientation,
                            orientation)

from gon.base import (Contour,
                      Multipolygon,
                      Polygon)
from gon.raw import (RawContour,
                     RawPoint)
from tests.utils import (Domain,
                         Strategy,
                         sub_lists)
from .base import coordinates_strategies
from .factories import (coordinates_to_contours,
                        coordinates_to_polygons)
from .linear import (contours_with_repeated_points,
                     invalid_vertices_contours)

polygons = coordinates_strategies.flatmap(coordinates_to_polygons)


def raw_contour_to_invalid_polygon(raw_contour: RawContour) -> Polygon:
    return Polygon(Contour.from_raw(raw_contour),
                   [Contour.from_raw(to_raw_points_convex_hull(raw_contour))])


def raw_contour_to_invalid_polygons(raw_convex_contour: RawContour
                                    ) -> Strategy[Polygon]:
    def raw_points_to_contour(raw_points: Sequence[RawPoint]) -> Contour:
        return Contour.from_raw(to_contour(raw_points, len(raw_points)))

    def lift(value: Domain) -> List[Domain]:
        return [value]

    contour = Contour.from_raw(raw_convex_contour)
    return strategies.builds(Polygon,
                             strategies.just(contour),
                             sub_lists(raw_convex_contour,
                                       min_size=3)
                             .map(raw_points_to_contour)
                             .map(lift))


invalid_contours = invalid_vertices_contours | contours_with_repeated_points
invalid_polygons = (
        strategies.builds(Polygon, invalid_contours)
        | strategies.builds(Polygon,
                            coordinates_strategies
                            .flatmap(coordinates_to_contours),
                            strategies.lists(invalid_contours,
                                             min_size=1))
        | (coordinates_strategies.flatmap(planar.convex_contours)
           .flatmap(raw_contour_to_invalid_polygons))
        | (coordinates_strategies.flatmap(planar.contours)
           .map(raw_contour_to_invalid_polygon)))
repeated_polygons = (strategies.builds(repeat, polygons,
                                       strategies.integers(2, 100))
                     .map(list))
invalid_multipolygons = (strategies.builds(Multipolygon,
                                           strategies.lists(invalid_polygons)
                                           | repeated_polygons))


def to_raw_points_convex_hull(points: Sequence[RawPoint]) -> List[RawPoint]:
    points = sorted(points)
    lower = _to_raw_points_sub_hull(points)
    upper = _to_raw_points_sub_hull(reversed(points))
    return lower[:-1] + upper[:-1]


def _to_raw_points_sub_hull(points: Iterable[RawPoint]) -> List[RawPoint]:
    result = []
    for point in points:
        while len(result) >= 2:
            if orientation(result[-1], result[-2],
                           point) is not Orientation.COUNTERCLOCKWISE:
                del result[-1]
            else:
                break
        result.append(point)
    return result
