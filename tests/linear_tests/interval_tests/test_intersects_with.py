from typing import Tuple

from hypothesis import given

from gon.linear import Interval
from tests.utils import implication
from . import strategies


@given(strategies.intervals)
def test_reflexivity(interval: Interval) -> None:
    assert interval.intersects_with(interval)


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
