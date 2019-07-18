from typing import Tuple

import pytest
from hypothesis import given

from gon.base import Point
from gon.linear import (Interval,
                        Segment,
                        to_interval)
from . import strategies


@given(strategies.unequal_points_pairs,
       strategies.booleans, strategies.booleans)
def test_basic(points_pair: Tuple[Point, Point],
               start_inclusive: bool,
               end_inclusive: bool) -> None:
    start, end = points_pair

    result = to_interval(start, end,
                         start_inclusive=start_inclusive,
                         end_inclusive=end_inclusive)

    assert isinstance(result, Interval)
    assert result.start == start
    assert result.end == end
    assert result.start_inclusive is start_inclusive
    assert result.end_inclusive is end_inclusive


@given(strategies.unequal_points_pairs)
def test_both_ends_included(points_pair: Tuple[Point, Point]) -> None:
    start, end = points_pair

    result = to_interval(start, end,
                         start_inclusive=True,
                         end_inclusive=True)

    assert isinstance(result, Segment)


@given(strategies.points, strategies.booleans, strategies.booleans)
def test_degenerate_case(point: Point,
                         start_inclusive: bool,
                         end_inclusive: bool) -> None:
    with pytest.raises(ValueError):
        to_interval(point, point,
                    start_inclusive=start_inclusive,
                    end_inclusive=end_inclusive)
