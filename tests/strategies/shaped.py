from functools import partial
from operator import attrgetter

from hypothesis import strategies

from gon.hints import Scalar
from gon.shaped.contracts import vertices_forms_strict_polygon
from gon.shaped.hints import Vertices
from tests.utils import (Strategy,
                         to_triplets)
from .base import (scalars_strategies,
                   scalars_to_points)


def scalars_to_triangles_vertices(scalars: Strategy[Scalar]
                                  ) -> Strategy[Vertices]:
    return (to_triplets(scalars_to_points(scalars))
            .filter(vertices_forms_strict_polygon))


triangles_vertices = scalars_strategies.flatmap(scalars_to_triangles_vertices)
to_non_triangle_vertices_base = partial(strategies.lists,
                                        min_size=4,
                                        unique_by=(attrgetter('x'),
                                                   attrgetter('y')))
