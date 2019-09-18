from typing import Any

from hypothesis import given

from gon.linear import Interval
from tests.utils import implication
from . import strategies


@given(strategies.intervals)
def test_reflexivity(interval: Interval) -> None:
    assert interval == interval


@given(strategies.intervals, strategies.intervals)
def test_symmetry(left_interval: Interval, right_interval: Interval) -> None:
    assert implication(left_interval == right_interval,
                       right_interval == left_interval)


@given(strategies.intervals, strategies.intervals, strategies.intervals)
def test_transitivity(left_interval: Interval,
                      mid_interval: Interval,
                      right_interval: Interval) -> None:
    assert implication(left_interval == mid_interval
                       and mid_interval == right_interval,
                       left_interval == right_interval)


@given(strategies.intervals)
def test_independence_from_ends_order(interval: Interval) -> None:
    assert interval == interval.reversed


@given(strategies.intervals, strategies.non_intervals)
def test_non_interval(interval: Interval, non_interval: Any) -> None:
    assert interval != non_interval
