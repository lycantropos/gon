from operator import (methodcaller,
                      ne)
from typing import Tuple

from hypothesis import strategies
from lz.functional import (compose,
                           pack)
from lz.replication import duplicate

from gon.base import Point
from gon.linear import Segment
from tests.strategies import (points_strategies,
                              scalars_to_points,
                              segment_to_scalars)
from tests.utils import Strategy

points_to_segments = compose(methodcaller(Strategy.map.__name__,
                                          pack(Segment)),
                             methodcaller(Strategy.filter.__name__,
                                          pack(ne)),
                             pack(strategies.tuples),
                             duplicate)
segments = points_strategies.flatmap(points_to_segments)


def to_segment_with_points(segment: Segment
                           ) -> Strategy[Tuple[Segment, Point]]:
    return strategies.tuples(strategies.just(segment),
                             scalars_to_points(segment_to_scalars(segment)))


segments_with_points = segments.flatmap(to_segment_with_points)
segments_pairs = points_strategies.flatmap(compose(pack(strategies.tuples),
                                                   duplicate,
                                                   points_to_segments))
