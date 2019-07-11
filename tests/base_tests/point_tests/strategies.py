import math
from hypothesis import strategies
from lz.functional import identity

from tests.strategies import scalars_strategies

valid_coordinates = scalars_strategies.flatmap(identity)
invalid_coordinates = strategies.sampled_from([math.nan, math.inf])
