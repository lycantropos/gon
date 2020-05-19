from hypothesis import strategies

from gon.degenerate import Empty
from tests.strategies import (coordinates_strategies,
                              coordinates_to_points)

raw_empty_geometries = strategies.none()
empty_geometries = strategies.builds(Empty)
empty_geometries_with_points = strategies.tuples(
        empty_geometries,
        coordinates_strategies.flatmap(coordinates_to_points))
