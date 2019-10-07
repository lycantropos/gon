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
               with_start: bool,
               with_end: bool) -> None:
    start, end = points_pair

    result = to_interval(start, end,
                         with_start=with_start,
                         with_end=with_end)

    assert isinstance(result, Interval)
    assert result.start == start
    assert result.end == end
    assert result.with_start is with_start
    assert result.with_end is with_end


@given(strategies.unequal_points_pairs)
def test_both_ends_included(points_pair: Tuple[Point, Point]) -> None:
    start, end = points_pair

    result = to_interval(start, end,
                         with_start=True,
                         with_end=True)

    assert isinstance(result, Segment)


@given(strategies.points, strategies.booleans, strategies.booleans)
def test_degenerate_case(point: Point,
                         with_start: bool,
                         with_end: bool) -> None:
    with pytest.raises(ValueError):
        to_interval(point, point,
                    with_start=with_start,
                    with_end=with_end)
