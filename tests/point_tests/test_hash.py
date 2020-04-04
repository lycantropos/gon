from typing import Tuple

from hypothesis import given

from gon.primitive import Point
from tests.utils import implication
from . import strategies


@given(strategies.points)
def test_basic(point: Point) -> None:
    result = hash(point)

    assert isinstance(result, int)


@given(strategies.points)
def test_determinism(point: Point) -> None:
    result = hash(point)

    assert result == hash(point)


@given(strategies.points_pairs)
def test_connection_with_equality(points_pair: Tuple[Point, Point]) -> None:
    left_point, right_point = points_pair

    assert implication(left_point == right_point,
                       hash(left_point) == hash(right_point))
