from tests.strategies import (coordinates_strategies,
                              coordinates_to_linear_geometries,
                              rational_coordinates_strategies)
from tests.utils import (cleave_in_tuples,
                         identity)

linear_geometries = coordinates_strategies.flatmap(
        coordinates_to_linear_geometries)
rational_linear_geometries_with_coordinates_pairs = (
    rational_coordinates_strategies.flatmap(
            cleave_in_tuples(coordinates_to_linear_geometries, identity,
                             identity)))
