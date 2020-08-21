from gon.hints import Coordinate
from tests.strategies import (coordinates_strategies,
                              coordinates_to_shaped_geometries,
                              rational_coordinates_strategies)
from tests.utils import (Strategy,
                         cleave_in_tuples,
                         identity)

shaped_geometries = (coordinates_strategies
                     .flatmap(coordinates_to_shaped_geometries))
rational_shaped_geometries_with_coordinates_pairs = (
    rational_coordinates_strategies.flatmap(
            cleave_in_tuples(coordinates_to_shaped_geometries, identity,
                             identity)))


def coordinates_to_non_zero_coordinates(coordinates: Strategy[Coordinate]
                                        ) -> Strategy[Coordinate]:
    return coordinates.filter(bool)


rational_shaped_geometries_with_non_zero_coordinates_pairs = (
    rational_coordinates_strategies.flatmap(
            cleave_in_tuples(coordinates_to_shaped_geometries,
                             coordinates_to_non_zero_coordinates,
                             coordinates_to_non_zero_coordinates)))
