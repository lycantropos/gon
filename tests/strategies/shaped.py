from functools import partial
from operator import attrgetter

from hypothesis import strategies
from lz.functional import (compose,
                           pack)
from lz.replication import replicator

from gon.shaped.contracts import vertices_forms_strict_polygon
from tests.utils import Strategy
from .base import (scalars_strategies,
                   scalars_to_points)

scalars_to_triangles_vertices = compose(
        scalars_to_points,
        partial(Strategy.map,
                compose(pack(strategies.tuples), replicator(3))),
        partial(Strategy.filter, vertices_forms_strict_polygon))
triangles_vertices = scalars_strategies.flatmap(scalars_to_triangles_vertices)
to_non_triangle_vertices_base = partial(strategies.lists,
                                        min_size=4,
                                        unique_by=(attrgetter('x'),
                                                   attrgetter('y')))
