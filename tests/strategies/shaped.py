from itertools import repeat

from hypothesis import strategies
from hypothesis_geometry import planar

from gon.base import (Contour,
                      Multipolygon,
                      Polygon)
from tests.utils import (Strategy,
                         lift,
                         sub_lists,
                         to_points_convex_hull)
from .base import (coordinates_strategies,
                   empty_sequences)
from .factories import (coordinates_to_contours,
                        coordinates_to_polygons)
from .linear import contours_with_repeated_points

polygons = coordinates_strategies.flatmap(coordinates_to_polygons)


def contour_to_invalid_polygon(contour: Contour) -> Polygon:
    return Polygon(contour, [Contour(to_points_convex_hull(contour.vertices))])


def contour_to_invalid_polygons(convex_contour: Contour) -> Strategy[Polygon]:
    return strategies.builds(Polygon,
                             strategies.just(convex_contour),
                             sub_lists(convex_contour.vertices,
                                       min_size=3)
                             .map(Contour)
                             .map(lift))


invalid_polygons = (
        strategies.builds(Polygon, contours_with_repeated_points)
        | strategies.builds(Polygon,
                            coordinates_strategies
                            .flatmap(coordinates_to_contours),
                            strategies.lists(contours_with_repeated_points,
                                             min_size=1))
        | (coordinates_strategies.flatmap(planar.convex_contours)
           .flatmap(contour_to_invalid_polygons))
        | (coordinates_strategies.flatmap(planar.contours)
           .map(contour_to_invalid_polygon)))
repeated_polygons = (strategies.builds(repeat, polygons,
                                       strategies.integers(2, 100))
                     .map(list))
invalid_multipolygons = strategies.builds(Multipolygon,
                                          empty_sequences
                                          | polygons.map(lift)
                                          | strategies.lists(invalid_polygons)
                                          | repeated_polygons)
