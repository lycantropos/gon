from typing import (List,
                    Optional)

from hypothesis import strategies
from lz.functional import (compose,
                           identity,
                           pack)
from lz.replication import duplicate

from gon.base import Point
from gon.hints import Coordinate
from gon.shaped import triangular
from gon.shaped.subdivisional import QuadEdge
from gon.shaped.triangular import Triangulation
from tests.strategies import (coordinates_strategies,
                              coordinates_to_points)
from tests.utils import (Strategy,
                         cleave_in_tuples,
                         points_do_not_lie_on_the_same_line,
                         to_pairs,
                         to_triplets)

points_pairs = (coordinates_strategies
                .flatmap(compose(pack(strategies.tuples),
                                 duplicate,
                                 coordinates_to_points)))


def coordinates_to_quad_edges(coordinates: Strategy[Coordinate]
                              ) -> Strategy[QuadEdge]:
    return (coordinates_to_points_in_general_position(coordinates)
            .map(triangular.delaunay)
            .map(Triangulation.to_edges)
            .map(list)
            .flatmap(strategies.sampled_from))


def coordinates_to_points_in_general_position(
        coordinates: Strategy[Coordinate],
        *,
        min_size: int = 2,
        max_size: Optional[int] = None) -> Strategy[List[Point]]:
    return (strategies.lists(coordinates_to_points(coordinates),
                             min_size=min_size,
                             max_size=max_size,
                             unique=True)
            .filter(points_do_not_lie_on_the_same_line))


quad_edges_strategies = coordinates_strategies.map(coordinates_to_quad_edges)
quad_edges = quad_edges_strategies.flatmap(identity)
quad_edges_pairs = quad_edges_strategies.flatmap(to_pairs)
quad_edges_triplets = quad_edges_strategies.flatmap(to_triplets)


def coordinates_to_quad_edges_with_neighbours(coordinates: Strategy[Coordinate]
                                              ) -> Strategy[QuadEdge]:
    return (coordinates_to_points_in_general_position(coordinates,
                                                      min_size=4)
            .map(triangular.delaunay)
            .map(Triangulation.to_inner_edges)
            .map(list)
            .flatmap(strategies.sampled_from))


quad_edges_with_neighbours = (
    coordinates_strategies.flatmap(coordinates_to_quad_edges_with_neighbours))
quad_edges_with_points = (coordinates_strategies
                          .flatmap(cleave_in_tuples(coordinates_to_quad_edges,
                                                    coordinates_to_points)))
non_quad_edges = strategies.builds(object)
