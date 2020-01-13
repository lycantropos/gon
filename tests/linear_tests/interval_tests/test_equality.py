from typing import (Any,
                    Tuple)

from hypothesis import given

from gon.linear import Interval
from tests.utils import implication
from . import strategies


@given(strategies.intervals)
def test_reflexivity(interval: Interval) -> None:
    assert interval == interval


@given(strategies.intervals_pairs)
def test_symmetry(intervals_pair: Tuple[Interval, Interval]) -> None:
    left_interval, right_interval = intervals_pair

    assert implication(left_interval == right_interval,
                       right_interval == left_interval)


@given(strategies.intervals_triplets)
def test_transitivity(intervals_triplet: Tuple[Interval, Interval, Interval]
                      ) -> None:
    left_interval, mid_interval, right_interval = intervals_triplet

    assert implication(left_interval == mid_interval
                       and mid_interval == right_interval,
                       left_interval == right_interval)


@given(strategies.intervals)
def test_independence_from_ends_order(interval: Interval) -> None:
    assert interval == interval.reversed


@given(strategies.intervals, strategies.non_intervals)
def test_non_interval(interval: Interval, non_interval: Any) -> None:
    assert interval != non_interval
