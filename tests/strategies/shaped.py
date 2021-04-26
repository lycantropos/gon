from itertools import repeat
from typing import (List)

from hypothesis import strategies
from hypothesis_geometry import planar

from gon.base import (Contour,
                      Multipolygon,
                      Polygon)
from tests.utils import (Domain,
                         Strategy,
                         sub_lists,
                         to_points_convex_hull)
from .base import (coordinates_strategies,
                   empty_sequences)
from .factories import (coordinates_to_contours,
                        coordinates_to_polygons)
from .linear import (contours_with_repeated_points,
                     invalid_vertices_contours)

polygons = coordinates_strategies.flatmap(coordinates_to_polygons)


def contour_to_invalid_polygon(contour: Contour) -> Polygon:
    return Polygon(contour, [Contour(to_points_convex_hull(contour.vertices))])


def contour_to_invalid_polygons(convex_contour: Contour) -> Strategy[Polygon]:
    def lift(value: Domain) -> List[Domain]:
        return [value]

    return strategies.builds(Polygon,
                             strategies.just(convex_contour),
                             sub_lists(convex_contour.vertices,
                                       min_size=3)
                             .map(Contour)
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
           .flatmap(contour_to_invalid_polygons))
        | (coordinates_strategies.flatmap(planar.contours)
           .map(contour_to_invalid_polygon)))
repeated_polygons = (strategies.builds(repeat, polygons,
                                       strategies.integers(2, 100))
                     .map(list))
invalid_multipolygons = strategies.builds(Multipolygon,
                                          empty_sequences
                                          | strategies.lists(invalid_polygons)
                                          | repeated_polygons)
