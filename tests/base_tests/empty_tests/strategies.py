from hypothesis import strategies

from gon.base import EMPTY
from tests.strategies import (coordinates_strategies,
                              coordinates_to_points)

empty_geometries = strategies.just(EMPTY)
empty_geometries_with_points = strategies.tuples(
        empty_geometries,
        coordinates_strategies.flatmap(coordinates_to_points))
