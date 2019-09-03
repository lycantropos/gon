from hypothesis import strategies
from lz.functional import (compose,
                           pack)
from lz.replication import duplicate

from gon.shaped.subdivisional import QuadEdge
from tests.strategies import (scalars_strategies,
                              scalars_to_points)
from tests.utils import triplicate

points_pairs = (scalars_strategies
                .flatmap(compose(pack(strategies.tuples),
                                 duplicate,
                                 scalars_to_points)))
quad_edges = points_pairs.map(pack(QuadEdge.factory))
points_triplets = (scalars_strategies
                   .flatmap(compose(pack(strategies.tuples),
                                    triplicate,
                                    scalars_to_points)))
quad_edges_with_points = (points_triplets
                          .map(lambda points_triplet:
                               (QuadEdge.factory(points_triplet[0],
                                                 points_triplet[1]),
                                points_triplet[2])))
