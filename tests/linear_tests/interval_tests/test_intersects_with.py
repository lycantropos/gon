from typing import Tuple

from hypothesis import given

from gon.linear import Interval
from tests.utils import (equivalence,
                         implication,
                         inverse_inclusion,
                         is_non_origin_point,
                         reflect_interval)
from . import strategies


@given(strategies.intervals)
def test_reflexivity(interval: Interval) -> None:
    assert interval.intersects_with(interval)


@given(strategies.intervals)
def test_inversed_inclusion(interval: Interval) -> None:
    assert interval.intersects_with(inverse_inclusion(interval))


@given(strategies.intervals_pairs)
def test_symmetry(intervals_pair: Tuple[Interval, Interval]) -> None:
    interval, other_interval = intervals_pair

    assert implication(interval.intersects_with(other_interval),
                       other_interval.intersects_with(interval))


@given(strategies.intervals_pairs)
def test_independence_from_ends_order(intervals_pair: Tuple[Interval, Interval]
                                      ) -> None:
    interval, other_interval = intervals_pair

    assert implication(interval.intersects_with(other_interval),
                       interval.reversed.intersects_with(other_interval))


@given(strategies.same_quadrant_intervals)
def test_same_quadrant_interval_reflection(interval: Interval) -> None:
    reflected_interval = reflect_interval(interval)

    one_of_endpoints_is_included_origin = (
            interval.start_inclusive
            and not is_non_origin_point(interval.start)
            or interval.end_inclusive
            and not is_non_origin_point(interval.end))

    assert equivalence(one_of_endpoints_is_included_origin,
                       interval.intersects_with(reflected_interval))
