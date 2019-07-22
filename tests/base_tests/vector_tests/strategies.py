import math
from hypothesis import strategies
from lz.functional import identity

from gon.base import Vector
from tests.strategies import scalars_strategies

invalid_coordinates = strategies.sampled_from([math.nan, math.inf, -math.inf])
valid_coordinates = scalars_strategies.flatmap(identity)
vectors = strategies.builds(Vector, valid_coordinates, valid_coordinates)
