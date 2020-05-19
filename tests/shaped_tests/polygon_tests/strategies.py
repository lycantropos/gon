from hypothesis import strategies
from hypothesis_geometry import planar

from gon.linear import Contour
from gon.shaped import Polygon
from gon.shaped.utils import to_convex_hull
from tests.strategies import (contours_with_repeated_points,
                              coordinates_strategies,
                              coordinates_to_contours,
                              coordinates_to_points,
                              coordinates_to_polygons,
                              invalid_vertices_contours)
from tests.utils import (cleave_in_tuples,
                         to_pairs,
                         to_triplets)

raw_polygons = coordinates_strategies.flatmap(planar.polygons)
polygons = raw_polygons.map(Polygon.from_raw)


def to_invalid_polygon_with_hole(concave_contour: Contour) -> Polygon:
    return Polygon(concave_contour,
                   [Contour(to_convex_hull(concave_contour.vertices))])


invalid_contours = invalid_vertices_contours | contours_with_repeated_points
invalid_polygons = (
        strategies.builds(Polygon, invalid_contours)
        | strategies.builds(Polygon,
                            coordinates_strategies
                            .flatmap(coordinates_to_contours),
                            strategies.lists(invalid_contours, min_size=1))
        | (coordinates_strategies.flatmap(planar.concave_contours)
           .map(Contour.from_raw)
           .map(to_invalid_polygon_with_hole)))
polygons_strategies = coordinates_strategies.map(coordinates_to_polygons)
polygons_pairs = polygons_strategies.flatmap(to_pairs)
polygons_triplets = polygons_strategies.flatmap(to_triplets)
polygons_with_points = (coordinates_strategies
                        .flatmap(cleave_in_tuples(coordinates_to_polygons,
                                                  coordinates_to_points)))
