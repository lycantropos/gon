from hypothesis_geometry import planar

from gon.contour import Contour
from gon.hints import Coordinate
from gon.polygon import Polygon
from tests.strategies import (coordinates_strategies,
                              coordinates_to_points)
from tests.utils import (Strategy,
                         cleave_in_tuples,
                         to_pairs,
                         to_triplets)

raw_triangular_contours = (coordinates_strategies
                           .flatmap(planar.triangular_contours))
triangular_contours = raw_triangular_contours.map(Contour.from_raw)
triangles = triangular_contours.map(Polygon)
raw_polygons = coordinates_strategies.flatmap(planar.polygons)
polygons = raw_polygons.map(Polygon.from_raw)


def coordinates_to_polygons(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Polygon]:
    return planar.polygons(coordinates).map(Polygon.from_raw)


polygons_strategies = coordinates_strategies.map(coordinates_to_polygons)
polygons_pairs = polygons_strategies.flatmap(to_pairs)
polygons_triplets = polygons_strategies.flatmap(to_triplets)
polygons_with_points = (coordinates_strategies
                        .flatmap(cleave_in_tuples(coordinates_to_polygons,
                                                  coordinates_to_points)))
