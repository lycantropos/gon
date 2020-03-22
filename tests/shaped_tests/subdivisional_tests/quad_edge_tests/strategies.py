from numbers import Real
from typing import (List,
                    Optional)

from hypothesis import strategies
from lz.functional import (compose,
                           identity,
                           pack)
from lz.replication import duplicate

from gon.base import Point
from gon.shaped import triangular
from gon.shaped.subdivisional import QuadEdge
from gon.shaped.triangular import Triangulation
from tests.strategies import (scalars_strategies,
                              scalars_to_points)
from tests.utils import (Strategy,
                         cleave_in_tuples,
                         points_do_not_lie_on_the_same_line,
                         to_pairs,
                         to_triplets)

points_pairs = (scalars_strategies
                .flatmap(compose(pack(strategies.tuples),
                                 duplicate,
                                 scalars_to_points)))


def scalars_to_quad_edges(scalars: Strategy[Real]) -> Strategy[QuadEdge]:
    return (scalars_to_points_in_general_position(scalars)
            .map(triangular.delaunay)
            .map(Triangulation.to_edges)
            .map(list)
            .flatmap(strategies.sampled_from))


def scalars_to_points_in_general_position(scalars: Strategy[Real],
                                          *,
                                          min_size: int = 2,
                                          max_size: Optional[int] = None
                                          ) -> Strategy[List[Point]]:
    return (strategies.lists(scalars_to_points(scalars),
                             min_size=min_size,
                             max_size=max_size,
                             unique=True)
            .filter(points_do_not_lie_on_the_same_line))


quad_edges_strategies = scalars_strategies.map(scalars_to_quad_edges)
quad_edges = quad_edges_strategies.flatmap(identity)
quad_edges_pairs = quad_edges_strategies.flatmap(to_pairs)
quad_edges_triplets = quad_edges_strategies.flatmap(to_triplets)


def scalars_to_quad_edges_with_neighbours(scalars: Strategy[Real]
                                          ) -> Strategy[QuadEdge]:
    return (scalars_to_points_in_general_position(scalars,
                                                  min_size=4)
            .map(triangular.delaunay)
            .map(Triangulation.to_inner_edges)
            .map(list)
            .flatmap(strategies.sampled_from))


quad_edges_with_neighbours = (scalars_strategies
                              .flatmap(scalars_to_quad_edges_with_neighbours))
quad_edges_with_points = (scalars_strategies
                          .flatmap(cleave_in_tuples(scalars_to_quad_edges,
                                                    scalars_to_points)))
non_quad_edges = strategies.builds(object)
