from functools import partial
from operator import attrgetter

from hypothesis import strategies
from lz.functional import (compose,
                           pack)
from lz.replication import replicator

from gon.shaped.contracts import vertices_forms_strict_polygon
from .base import points_strategies

triangles_vertices = (points_strategies
                      .flatmap(compose(pack(strategies.tuples), replicator(3)))
                      .filter(vertices_forms_strict_polygon))
to_non_triangle_vertices_base = partial(strategies.lists,
                                        min_size=4,
                                        unique_by=(attrgetter('x'),
                                                   attrgetter('y')))
