from hypothesis_geometry import planar

from gon.linear import Loop
from tests.strategies import (loops_with_repeated_points,
                              coordinates_strategies,
                              coordinates_to_loops,
                              invalid_vertices_loops,
                              small_loops)
from tests.utils import (to_pairs,
                         to_triplets)

raw_loops = coordinates_strategies.flatmap(planar.loops)
loops = raw_loops.map(Loop.from_raw)
invalid_loops = (small_loops
                 | invalid_vertices_loops
                 | loops_with_repeated_points)
loops_strategies = coordinates_strategies.map(coordinates_to_loops)
loops_pairs = loops_strategies.flatmap(to_pairs)
loops_triplets = loops_strategies.flatmap(to_triplets)
