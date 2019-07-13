from typing import Sequence

from hypothesis import strategies
from lz.functional import (compose,
                           pack)
from lz.replication import replicator

from gon.base import Point
from gon.shaped import (Polygon,
                        vertices_forms_angles)
from tests.utils import Strategy
from .base import points_strategies

to_triangles_vertices = compose(pack(strategies.tuples), replicator(3))
triangles_vertices = (points_strategies
                      .flatmap(to_triangles_vertices)
                      .filter(vertices_forms_angles))
triangles = (triangles_vertices
             .map(Polygon))


def to_vertices(points: Strategy[Point]) -> Strategy[Sequence[Point]]:
    return (to_triangles_vertices(points)
            .filter(vertices_forms_angles))


polygons = (points_strategies
            .flatmap(to_vertices)
            .map(Polygon))
