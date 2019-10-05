from typing import Tuple

from hypothesis import given

from gon.angular import Orientation
from gon.base import Point
from gon.linear import Interval
from tests.utils import (equivalence,
                         implication,
                         reflect_interval)
from . import strategies


@given(strategies.intervals)
def test_endpoints(interval: Interval) -> None:
    assert equivalence(interval.start_inclusive, interval.start in interval)
    assert equivalence(interval.end_inclusive, interval.end in interval)


@given(strategies.intervals)
def test_reflection(interval: Interval) -> None:
    reflected_interval = reflect_interval(interval)

    assert equivalence(interval.start_inclusive,
                       reflected_interval.start in interval)
    assert reflected_interval.end not in interval


@given(strategies.intervals_with_points)
def test_orientation(interval_with_point: Tuple[Interval, Point]) -> None:
    interval, point = interval_with_point

    assert implication(point in interval,
                       interval.orientation_with(point)
                       is Orientation.COLLINEAR)
