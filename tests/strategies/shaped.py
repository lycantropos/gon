from functools import partial
from operator import attrgetter

from hypothesis import strategies
from lz.logical import negate

from gon.shaped import (self_intersects,
                        vertices_forms_angles)
from .base import points_strategies

to_non_triangle_vertices_base = partial(strategies.lists,
                                        min_size=4,
                                        unique_by=(attrgetter('x'),
                                                   attrgetter('y')))
invalid_vertices = points_strategies.flatmap(to_non_triangle_vertices_base)
invalid_vertices = (points_strategies.flatmap(partial(strategies.lists,
                                                      max_size=2))
                    | invalid_vertices.filter(self_intersects)
                    | invalid_vertices.filter(negate(vertices_forms_angles)))
