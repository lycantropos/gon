import math

from hypothesis import strategies
from lz.functional import identity

from tests.strategies import (coordinates_strategies,
                              points,
                              points_strategies)
from tests.utils import (to_pairs,
                         to_triplets)

valid_coordinates = coordinates_strategies.flatmap(identity)
invalid_coordinates = strategies.sampled_from([math.nan, math.inf, -math.inf])
points = points
points_pairs = points_strategies.flatmap(to_pairs)
points_triplets = points_strategies.flatmap(to_triplets)
