from hypothesis import strategies

from gon.hints import Scalar
from tests.strategies import (angles,
                              coordinates_strategies,
                              coordinates_to_points,
                              coordinates_to_shaped_geometries)
from tests.utils import (Strategy,
                         cleave_in_tuples,
                         identity)

shaped_geometries = (coordinates_strategies
                     .flatmap(coordinates_to_shaped_geometries))
shaped_geometries_with_coordinates_pairs = coordinates_strategies.flatmap(
        cleave_in_tuples(coordinates_to_shaped_geometries, identity, identity)
)


def coordinates_to_non_zero_coordinates(coordinates: Strategy[Scalar]
                                        ) -> Strategy[Scalar]:
    return coordinates.filter(bool)


shaped_geometries_with_non_zero_coordinates_pairs = (
    (coordinates_strategies
     .flatmap(cleave_in_tuples(coordinates_to_shaped_geometries,
                               coordinates_to_non_zero_coordinates,
                               coordinates_to_non_zero_coordinates)))
)
shaped_geometries_points_with_angles = strategies.tuples(
        (coordinates_strategies
         .flatmap(cleave_in_tuples(coordinates_to_shaped_geometries,
                                   coordinates_to_points))),
        angles
)
