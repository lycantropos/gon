from hypothesis_geometry import planar

from gon.base import Polygon
from tests.strategies import (coordinates_strategies,
                              coordinates_to_points,
                              coordinates_to_polygons,
                              invalid_polygons,
                              rational_coordinates_strategies)
from tests.utils import (cleave_in_tuples,
                         to_pairs,
                         to_triplets)

rational_raw_polygons = (rational_coordinates_strategies
                         .flatmap(planar.polygons))
raw_polygons = coordinates_strategies.flatmap(planar.polygons)
rational_polygons = rational_raw_polygons.map(Polygon.from_raw)
polygons = raw_polygons.map(Polygon.from_raw)
invalid_polygons = invalid_polygons
polygons_strategies = coordinates_strategies.map(coordinates_to_polygons)
polygons_pairs = polygons_strategies.flatmap(to_pairs)
polygons_triplets = polygons_strategies.flatmap(to_triplets)
polygons_with_points = (coordinates_strategies
                        .flatmap(cleave_in_tuples(coordinates_to_polygons,
                                                  coordinates_to_points)))
