from functools import partial
from operator import attrgetter

from hypothesis import strategies
from lz.functional import compose

from tests.strategies import (scalars_strategies,
                              scalars_to_points,
                              triangles_vertices)

scalars_to_points_lists = partial(strategies.lists,
                                  unique_by=(attrgetter('x'),
                                             attrgetter('y')))
points_lists = (scalars_strategies
                .flatmap(compose(partial(scalars_to_points_lists,
                                         min_size=3),
                                 scalars_to_points)))
non_triangle_points_lists = (scalars_strategies
                             .flatmap(compose(partial(scalars_to_points_lists,
                                                      min_size=4),
                                              scalars_to_points)))
triangles_vertices = triangles_vertices
