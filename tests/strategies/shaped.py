from itertools import repeat
from typing import Tuple

from hypothesis import strategies
from hypothesis_geometry import planar

from gon.base import (Contour,
                      Multipolygon,
                      Polygon)
from tests.utils import (Strategy,
                         arg_min,
                         divide_by_int,
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


def to_polygon_with_overlapping_polygon(polygon: Polygon
                                        ) -> Tuple[Polygon, Polygon]:
    border_vertices = polygon.border.vertices
    min_vertex_index = arg_min(border_vertices)
    min_vertex, other_vertex = (border_vertices[min_vertex_index],
                                border_vertices[min_vertex_index - 1])
    return (polygon,
            polygon.translate(divide_by_int(other_vertex.x - min_vertex.x, 2),
                              divide_by_int(other_vertex.y - min_vertex.y, 2)))


overlapping_polygons = polygons.map(to_polygon_with_overlapping_polygon)
invalid_multipolygons = strategies.builds(Multipolygon,
                                          empty_sequences
                                          | polygons.map(lift)
                                          | strategies.lists(invalid_polygons)
                                          | repeated_polygons
                                          | overlapping_polygons)
