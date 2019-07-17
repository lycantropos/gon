from operator import (methodcaller,
                      ne)
from typing import Tuple

from hypothesis import strategies
from lz.functional import (compose,
                           pack)
from lz.replication import duplicate

from gon.base import Point
from gon.hints import Scalar
from gon.linear import Segment
from tests.utils import Strategy
from .base import (points_strategies,
                   scalars_strategies_factories,
                   scalars_to_points)

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


def segment_to_scalars(segment: Segment) -> Strategy[Scalar]:
    coordinates = [segment.start.x, segment.start.y,
                   segment.end.x, segment.end.y]
    coordinates_type, = set(map(type, coordinates))
    strategy_factory = scalars_strategies_factories[coordinates_type]
    return strategy_factory(min_value=min(coordinates),
                            max_value=max(coordinates))


segments_with_points = segments.flatmap(to_segment_with_points)
segments_pairs = points_strategies.flatmap(compose(pack(strategies.tuples),
                                                   duplicate,
                                                   points_to_segments))
