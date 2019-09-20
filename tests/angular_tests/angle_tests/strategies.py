from functools import partial

from hypothesis import strategies
from lz.functional import pack

from gon.angular import Angle
from tests.strategies import points_strategies

unique_points_triplets = points_strategies.flatmap(partial(strategies.lists,
                                                           min_size=3,
                                                           max_size=3,
                                                           unique=True))
angles = unique_points_triplets.map(pack(Angle))
