from hypothesis_geometry import planar

from gon.shaped import Polygon
from tests.strategies import (coordinates_strategies,
                              coordinates_to_points,
                              coordinates_to_polygons,
                              invalid_polygons)
from tests.utils import (cleave_in_tuples,
                         to_pairs,
                         to_triplets)

raw_polygons = coordinates_strategies.flatmap(planar.polygons)
polygons = raw_polygons.map(Polygon.from_raw)
invalid_polygons = invalid_polygons
polygons_strategies = coordinates_strategies.map(coordinates_to_polygons)
polygons_pairs = polygons_strategies.flatmap(to_pairs)
polygons_triplets = polygons_strategies.flatmap(to_triplets)
polygons_with_points = (coordinates_strategies
                        .flatmap(cleave_in_tuples(coordinates_to_polygons,
                                                  coordinates_to_points)))
