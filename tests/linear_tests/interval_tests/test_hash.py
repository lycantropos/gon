from typing import Tuple

from hypothesis import given

from gon.linear import Interval
from tests.utils import implication
from . import strategies


@given(strategies.intervals)
def test_basic(interval: Interval) -> None:
    result = hash(interval)

    assert isinstance(result, int)


@given(strategies.intervals)
def test_determinism(interval: Interval) -> None:
    result = hash(interval)

    assert result == hash(interval)


@given(strategies.intervals_pairs)
def test_connection_with_equality(intervals_pair: Tuple[Interval, Interval]
                                  ) -> None:
    left_interval, right_interval = intervals_pair

    assert implication(left_interval == right_interval,
                       hash(left_interval) == hash(right_interval))


@given(strategies.intervals)
def test_independence_from_ends_order(interval: Interval) -> None:
    assert hash(interval) == hash(interval.reversed)
