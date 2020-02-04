from functools import partial
from operator import attrgetter

from hypothesis import strategies
from hypothesis_geometry import planar
from lz.functional import pack
from lz.iterating import mapper

from gon.base import Point
from .base import scalars_strategies

triangles_vertices = (scalars_strategies.flatmap(planar.triangular_contours)
                      .map(mapper(pack(Point)))
                      .map(list))
to_non_triangle_vertices_base = partial(strategies.lists,
                                        min_size=4,
                                        unique_by=(attrgetter('x'),
                                                   attrgetter('y')))
