import math

from hypothesis import strategies
from lz.functional import identity

from tests.strategies import (points,
                              points_strategies,
                              scalars_strategies)
from tests.utils import (to_pairs,
                         to_triplets)

valid_coordinates = scalars_strategies.flatmap(identity)
invalid_coordinates = strategies.sampled_from([math.nan, math.inf, -math.inf])
points = points
points_pairs = points_strategies.flatmap(to_pairs)
points_triplets = points_strategies.flatmap(to_triplets)
non_points = strategies.builds(object)
