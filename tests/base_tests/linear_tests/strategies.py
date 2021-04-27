from hypothesis import strategies

from tests.strategies import (coordinates_strategies,
                              coordinates_to_linear_geometries,
                              coordinates_to_points,
                              rational_coordinates_strategies,
                              rational_cosines_sines)
from tests.utils import (cleave_in_tuples,
                         identity)

linear_geometries = coordinates_strategies.flatmap(
        coordinates_to_linear_geometries)
rational_linear_geometries_with_coordinates_pairs = (
    rational_coordinates_strategies.flatmap(
            cleave_in_tuples(coordinates_to_linear_geometries, identity,
                             identity)))
rational_linear_geometries_points_with_cosines_sines = (
    strategies.tuples(
            (rational_coordinates_strategies
             .flatmap(cleave_in_tuples(coordinates_to_linear_geometries,
                                       coordinates_to_points))),
            rational_cosines_sines))
