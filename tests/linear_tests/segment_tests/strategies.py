from operator import (methodcaller,
                      ne)

from hypothesis import strategies
from lz.functional import (compose,
                           identity,
                           pack)
from lz.replication import duplicate

from gon.linear import Segment
from tests.strategies import (coordinates_strategies,
                              coordinates_to_points)
from tests.utils import (Strategy,
                         cleave_in_tuples,
                         to_pairs,
                         to_triplets)

coordinates_to_segments = compose(methodcaller(Strategy.map.__name__,
                                               pack(Segment)),
                                  methodcaller(Strategy.filter.__name__,
                                               pack(ne)),
                                  pack(strategies.tuples),
                                  duplicate,
                                  coordinates_to_points)
segments_strategies = coordinates_strategies.map(coordinates_to_segments)
segments = segments_strategies.flatmap(identity)
segments_with_points = (coordinates_strategies
                        .flatmap(cleave_in_tuples(coordinates_to_segments,
                                                  coordinates_to_points)))
segments_pairs = segments_strategies.flatmap(to_pairs)
segments_triplets = segments_strategies.flatmap(to_triplets)
non_segments = strategies.builds(object)
