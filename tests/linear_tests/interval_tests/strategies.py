from operator import ne
from typing import Tuple

from hypothesis import strategies
from lz.functional import (compose,
                           pack)
from lz.replication import duplicate

from gon.base import Point
from gon.linear import Interval
from tests.strategies import (interval_to_scalars,
                              points_strategies,
                              scalars_to_points)
from tests.utils import Strategy


def points_to_intervals(points: Strategy[Point]) -> Strategy[Interval]:
    return (strategies.tuples(points, points)
            .filter(pack(ne))
            .flatmap(lambda endpoints:
                     strategies.builds(Interval,
                                       strategies.just(endpoints[0]),
                                       strategies.just(endpoints[1]),
                                       start_inclusive=strategies.booleans(),
                                       end_inclusive=strategies.booleans())))


intervals = points_strategies.flatmap(points_to_intervals)
non_intervals = strategies.builds(object)


def to_interval_with_points(interval: Interval
                            ) -> Strategy[Tuple[Interval, Point]]:
    return strategies.tuples(strategies.just(interval),
                             scalars_to_points(interval_to_scalars(interval)))


intervals_with_points = intervals.flatmap(to_interval_with_points)
intervals_pairs = points_strategies.flatmap(compose(pack(strategies.tuples),
                                                    duplicate,
                                                    points_to_intervals))
