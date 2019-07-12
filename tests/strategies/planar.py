from typing import Sequence

from hypothesis import strategies
from lz.functional import (compose,
                           pack)
from lz.logical import negate
from lz.replication import replicator

from gon.base import Point
from gon.shaped import (Polygon,
                        self_intersects,
                        vertices_forms_angles)
from tests.strategies.base import (scalars_strategies,
                                   scalars_to_points)
from tests.utils import Strategy

triangles_vertices = (scalars_strategies
                      .flatmap(compose(pack(strategies.tuples),
                                       replicator(3),
                                       scalars_to_points))
                      .filter(vertices_forms_angles))
triangles = (triangles_vertices
             .map(Polygon))


def to_vertices(points: Strategy[Point]) -> Strategy[Sequence[Point]]:
    return strategies.lists(points,
                            min_size=3)


polygons = (scalars_strategies
            .flatmap(compose(to_vertices,
                             scalars_to_points))
            .filter(vertices_forms_angles)
            .filter(negate(self_intersects))
            .map(Polygon))
