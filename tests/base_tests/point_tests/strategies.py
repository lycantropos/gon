from tests.strategies import (coordinates_strategies,
                              coordinates_to_points,
                              invalid_points,
                              points)
from tests.utils import (to_pairs,
                         to_triplets)

invalid_points = invalid_points
points = points
points_strategies = coordinates_strategies.map(coordinates_to_points)
points_pairs = points_strategies.flatmap(to_pairs)
points_triplets = points_strategies.flatmap(to_triplets)
