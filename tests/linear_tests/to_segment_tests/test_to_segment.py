from typing import Tuple

import pytest
from hypothesis import given

from gon.base import Point
from gon.linear import (Segment,
                        to_segment)
from . import strategies


@given(strategies.unequal_points_pairs)
def test_basic(points_pair: Tuple[Point, Point]) -> None:
    start, end = points_pair

    result = to_segment(start, end)

    assert isinstance(result, Segment)
    assert result.start == start
    assert result.end == end


@given(strategies.points)
def test_degenerate_case(point: Point) -> None:
    with pytest.raises(ValueError):
        to_segment(point, point)
