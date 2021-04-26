from tests.strategies import (coordinates_strategies,
                              coordinates_to_multipolygons,
                              coordinates_to_points,
                              coordinates_to_polygons,
                              invalid_multipolygons)
from tests.utils import (cleave_in_tuples,
                         to_pairs,
                         to_triplets)

multipolygons = coordinates_strategies.flatmap(coordinates_to_multipolygons)
polygons = coordinates_strategies.flatmap(coordinates_to_polygons)
invalid_multipolygons = invalid_multipolygons
multipolygons_strategies = (coordinates_strategies
                            .map(coordinates_to_multipolygons))
multipolygons_pairs = multipolygons_strategies.flatmap(to_pairs)
multipolygons_triplets = multipolygons_strategies.flatmap(to_triplets)
multipolygons_with_points = (
    coordinates_strategies.flatmap(
            cleave_in_tuples(coordinates_to_multipolygons,
                             coordinates_to_points)))
