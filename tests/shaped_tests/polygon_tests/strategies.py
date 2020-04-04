from hypothesis import strategies
from hypothesis_geometry import planar

from gon.hints import Coordinate
from gon.linear import Contour
from gon.shaped import (Polygon,
                        _to_convex_hull)
from tests.strategies import (coordinates_strategies,
                              coordinates_to_contours,
                              coordinates_to_points,
                              invalid_contours)
from tests.utils import (Strategy,
                         cleave_in_tuples,
                         to_pairs,
                         to_triplets)

raw_polygons = coordinates_strategies.flatmap(planar.polygons)
polygons = raw_polygons.map(Polygon.from_raw)


def to_invalid_polygon_with_hole(concave_contour: Contour) -> Polygon:
    return Polygon(concave_contour,
                   [Contour(_to_convex_hull(concave_contour.vertices))])


invalid_polygons = (
        strategies.builds(Polygon, invalid_contours)
        | strategies.builds(Polygon,
                            coordinates_strategies
                            .flatmap(coordinates_to_contours),
                            strategies.lists(invalid_contours, min_size=1))
        | (coordinates_strategies.flatmap(planar.concave_contours)
           .map(Contour.from_raw)
           .map(to_invalid_polygon_with_hole)))


def coordinates_to_polygons(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Polygon]:
    return planar.polygons(coordinates).map(Polygon.from_raw)


polygons_strategies = coordinates_strategies.map(coordinates_to_polygons)
polygons_pairs = polygons_strategies.flatmap(to_pairs)
polygons_triplets = polygons_strategies.flatmap(to_triplets)
polygons_with_points = (coordinates_strategies
                        .flatmap(cleave_in_tuples(coordinates_to_polygons,
                                                  coordinates_to_points)))