from hypothesis import strategies

from tests.strategies import (angles,
                              coordinates_strategies,
                              coordinates_to_linear_geometries,
                              coordinates_to_points)
from tests.utils import (cleave_in_tuples,
                         identity)

linear_geometries = coordinates_strategies.flatmap(
        coordinates_to_linear_geometries)
linear_geometries_with_coordinates_pairs = coordinates_strategies.flatmap(
        cleave_in_tuples(coordinates_to_linear_geometries, identity, identity))
linear_geometries_points_with_angles = strategies.tuples(
        (coordinates_strategies
         .flatmap(cleave_in_tuples(coordinates_to_linear_geometries,
                                   coordinates_to_points))),
        angles)
