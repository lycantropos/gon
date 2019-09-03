from typing import Tuple

from hypothesis import given

from gon.base import Point
from gon.shaped.subdivisional import QuadEdge
from . import strategies


@given(strategies.points_pairs)
def test_basic(endpoints: Tuple[Point, Point]) -> None:
    start, end = endpoints

    result = QuadEdge.factory(start, end)

    assert isinstance(result, QuadEdge)
    assert isinstance(result.start, Point)
    assert isinstance(result.rotated, QuadEdge)
    assert isinstance(result.left_from_start, QuadEdge)


@given(strategies.points_pairs)
def test_endpoints(endpoints: Tuple[Point, Point]) -> None:
    start, end = endpoints

    result = QuadEdge.factory(start, end)

    assert result.start == start
    assert result.end == end
