from hypothesis import given

from gon.linear import Point
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


@given(strategies.points, strategies.points)
def test_connection_with_equality(left_point: Point,
                                  right_point: Point) -> None:
    assert implication(left_point == right_point,
                       hash(left_point) == hash(right_point))
