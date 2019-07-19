from operator import ne

from hypothesis import strategies
from lz.functional import pack

from tests.strategies import points

booleans = strategies.booleans()
points = points
unequal_points_pairs = strategies.tuples(points, points).filter(pack(ne))
