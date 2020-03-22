from functools import partial
from numbers import Real
from operator import (attrgetter,
                      ne)
from typing import (Optional,
                    Tuple)

from hypothesis import strategies
from lz.functional import (identity,
                           pack)
from lz.hints import Operator

from gon.base import Point
from gon.linear import Interval
from tests.strategies import (scalars_strategies,
                              scalars_to_points)
from tests.utils import (Strategy,
                         cleave_in_tuples,
                         inverse_inclusion,
                         reflect_interval,
                         scale_interval,
                         to_pairs,
                         to_triplets)


def scalars_to_intervals(scalars: Strategy[Real]) -> Strategy[Interval]:
    return (points_to_interval_endpoints(scalars_to_points(scalars))
            .flatmap(lambda endpoints:
                     strategies.builds(Interval,
                                       strategies.just(endpoints[0]),
                                       strategies.just(endpoints[1]),
                                       with_start=strategies.booleans(),
                                       with_end=strategies.booleans())))


def points_to_interval_endpoints(points: Strategy[Point]
                                 ) -> Strategy[Tuple[Point, Point]]:
    return strategies.tuples(points, points).filter(pack(ne))


intervals_strategies = scalars_strategies.map(scalars_to_intervals)
intervals = intervals_strategies.flatmap(identity)
intervals_pairs = intervals_strategies.flatmap(to_pairs)
intervals_triplets = intervals_strategies.flatmap(to_triplets)
non_intervals = strategies.builds(object)
intervals_with_points = (scalars_strategies
                         .flatmap(cleave_in_tuples(scalars_to_intervals,
                                                   scalars_to_points)))


def to_pythagorean_triplets(*,
                            min_value: int = 1,
                            max_value: Optional[int] = None
                            ) -> Strategy[Tuple[int, int, int]]:
    if min_value < 1:
        raise ValueError('`min_value` should be positive.')

    def to_increasing_integers_pairs(value: int) -> Strategy[Tuple[int, int]]:
        return strategies.tuples(strategies.just(value),
                                 strategies.integers(min_value=value + 1,
                                                     max_value=max_value))

    def to_pythagorean_triplet(increasing_integers_pair: Tuple[int, int]
                               ) -> Tuple[int, int, int]:
        first, second = increasing_integers_pair
        first_squared = first ** 2
        second_squared = second ** 2
        return (second_squared - first_squared,
                2 * first * second,
                first_squared + second_squared)

    return (strategies.integers(min_value=min_value,
                                max_value=(max_value - 1
                                           if max_value is not None
                                           else max_value))
            .flatmap(to_increasing_integers_pairs)
            .map(to_pythagorean_triplet))


pythagorean_triplets = to_pythagorean_triplets(max_value=1000)


def to_maybe_intersecting_intervals_pairs(
        intervals: Strategy[Interval]) -> Strategy[Tuple[Interval, Interval]]:
    def to_scaled_intervals_pair(interval_with_scale: Tuple[Interval, Real]
                                 ) -> Tuple[Interval, Interval]:
        interval, scale = interval_with_scale
        return interval, scale_interval(interval,
                                        scale=scale)

    def to_rotated_intervals_pair(
            interval_with_pythagorean_triplet: Tuple[Interval,
                                                     Tuple[int, int, int]]
    ) -> Tuple[Interval, Interval]:
        interval, pythagorean_triplet = interval_with_pythagorean_triplet
        area_sine, area_cosine, area = pythagorean_triplet
        dx, dy = (interval.end.x - interval.start.x,
                  interval.end.y - interval.start.y)
        return interval, Interval(interval.start,
                                  Point((area_cosine * dx - area_sine * dy)
                                        / area,
                                        (area_sine * dx + area_cosine * dy)
                                        / area),
                                  with_start=interval.with_start,
                                  with_end=interval.with_end)

    def map_first(map_: Operator[Interval],
                  intervals_pair: Tuple[Interval, Interval]
                  ) -> Tuple[Interval, Interval]:
        first, second = intervals_pair
        return map_(first), second

    def map_second(map_: Operator[Interval],
                   intervals_pair: Tuple[Interval, Interval]
                   ) -> Tuple[Interval, Interval]:
        first, second = intervals_pair
        return first, map_(second)

    variants = [intervals.map(lambda interval: (interval, interval)),
                (strategies.tuples(intervals,
                                   strategies.integers(min_value=-100,
                                                       max_value=-1)
                                   | strategies.integers(min_value=1,
                                                         max_value=100))
                 .map(to_scaled_intervals_pair)),
                (strategies.tuples(intervals, pythagorean_triplets)
                 .map(to_rotated_intervals_pair)),
                strategies.tuples(intervals, intervals)]
    for map_ in (attrgetter('reversed'), inverse_inclusion, reflect_interval):
        variants.extend([base.map(partial(map_first, map_))
                         for base in variants]
                        + [base.map(partial(map_second, map_))
                           for base in variants])
    return strategies.one_of(variants)


intervals_pairs |= (intervals_strategies
                    .flatmap(to_maybe_intersecting_intervals_pairs))
