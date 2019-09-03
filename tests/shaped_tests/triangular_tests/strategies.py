from functools import partial

from hypothesis import strategies
from lz.functional import compose

from tests.strategies import (scalars_strategies,
                              scalars_to_points,
                              triangles_vertices)
from tests.utils import points_do_not_lie_on_the_same_line

scalars_to_points_lists = partial(strategies.lists,
                                  unique=True)
points_lists = (scalars_strategies
                .flatmap(compose(partial(scalars_to_points_lists,
                                         min_size=3),
                                 scalars_to_points))
                .filter(points_do_not_lie_on_the_same_line))
non_triangle_points_lists = (scalars_strategies
                             .flatmap(compose(partial(scalars_to_points_lists,
                                                      min_size=4),
                                              scalars_to_points)))
triangles_vertices = triangles_vertices
