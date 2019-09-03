from hypothesis import strategies
from lz.functional import (compose,
                           pack)
from lz.replication import duplicate

from gon.shaped.subdivisional import QuadEdge
from tests.strategies import (scalars_strategies,
                              scalars_to_points)

points_pairs = (scalars_strategies
                .flatmap(compose(pack(strategies.tuples),
                                 duplicate,
                                 scalars_to_points)))
quad_edges = points_pairs.map(pack(QuadEdge.factory))
