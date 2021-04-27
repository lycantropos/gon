from tests.strategies import (invalid_points,
                              points,
                              points_strategies)
from tests.utils import (to_pairs,
                         to_triplets)

invalid_points = invalid_points
points = points
points_pairs = points_strategies.flatmap(to_pairs)
points_triplets = points_strategies.flatmap(to_triplets)
