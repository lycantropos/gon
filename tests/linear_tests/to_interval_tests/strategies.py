from operator import ne

from hypothesis import strategies
from lz.functional import pack

from tests.strategies import (scalars_strategies,
                              scalars_to_points)

booleans = strategies.booleans()
points = scalars_strategies.flatmap(scalars_to_points)
unequal_points_pairs = strategies.tuples(points, points).filter(pack(ne))
