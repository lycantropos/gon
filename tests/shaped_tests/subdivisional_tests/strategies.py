from functools import partial
from typing import Sequence

from hypothesis import strategies
from lz.functional import (compose,
                           pack)
from lz.replication import duplicate

from gon.base import Point
from gon.shaped.subdivisional import QuadEdge
from gon.shaped.triangular import _delaunay
from tests.strategies import (scalars_strategies,
                              scalars_to_points)
from tests.utils import (Strategy,
                         points_do_not_lie_on_the_same_line,
                         triplicate)

points_pairs = (scalars_strategies
                .flatmap(compose(pack(strategies.tuples),
                                 duplicate,
                                 scalars_to_points)))


def points_to_quad_edge(points: Sequence[Point]) -> Strategy[QuadEdge]:
    triangulation = _delaunay(points)
    return strategies.sampled_from(list(triangulation.to_edges()))


quad_edges = (scalars_strategies
              .flatmap(compose(partial(strategies.lists,
                                       min_size=2,
                                       unique=True),
                               scalars_to_points))
              .filter(points_do_not_lie_on_the_same_line)
              .flatmap(points_to_quad_edge))
points_triplets = (scalars_strategies
                   .flatmap(compose(pack(strategies.tuples),
                                    triplicate,
                                    scalars_to_points)))
quad_edges_with_points = (points_triplets
                          .map(lambda points_triplet:
                               (points_to_quad_edge(points_triplet[:2]),
                                points_triplet[2])))
