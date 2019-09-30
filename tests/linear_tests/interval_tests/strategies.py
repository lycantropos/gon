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
    return (points_to_interval_endpoints(points)
            .flatmap(lambda endpoints:
                     strategies.builds(Interval,
                                       strategies.just(endpoints[0]),
                                       strategies.just(endpoints[1]),
                                       start_inclusive=strategies.booleans(),
                                       end_inclusive=strategies.booleans())))


def points_to_interval_endpoints(points: Strategy[Point]
                                 ) -> Strategy[Tuple[Point, Point]]:
    return strategies.tuples(points, points).filter(pack(ne))


intervals = points_strategies.flatmap(points_to_intervals)


def points_to_same_quadrant_intervals(points: Strategy[Point]
                                      ) -> Strategy[Interval]:
    def endpoints_to_same_quadrant_intervals(endpoints: Tuple[Point, Point]
                                             ) -> Strategy[Interval]:
        start, end = endpoints
        if start.x * end.x < 0:
            if start.y * end.y < 0:
                end = Point(-end.x, -end.y)
            else:
                end = Point(-end.x, end.y)
        else:
            if start.y * end.y < 0:
                end = Point(end.x, -end.y)
        return strategies.builds(Interval,
                                 strategies.just(start), strategies.just(end),
                                 start_inclusive=strategies.booleans(),
                                 end_inclusive=strategies.booleans())

    return (points_to_interval_endpoints(points)
            .flatmap(endpoints_to_same_quadrant_intervals))


same_quadrant_intervals = (points_strategies
                           .flatmap(points_to_same_quadrant_intervals))
non_intervals = strategies.builds(object)


def to_interval_with_points(interval: Interval
                            ) -> Strategy[Tuple[Interval, Point]]:
    return strategies.tuples(strategies.just(interval),
                             scalars_to_points(interval_to_scalars(interval)))


intervals_with_points = intervals.flatmap(to_interval_with_points)
intervals_pairs = points_strategies.flatmap(compose(pack(strategies.tuples),
                                                    duplicate,
                                                    points_to_intervals))
