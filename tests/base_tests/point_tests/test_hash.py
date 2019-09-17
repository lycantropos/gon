from hypothesis import (example,
                        given)

from gon.linear import Point
from tests.utils import equivalence
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
@example(Point(-1.0, -1.0), Point(2.0, 2.0))
@example(Point(0.0, 0.0), Point(0.0, 0.5))
def test_connection_with_equality(left_point: Point,
                                  right_point: Point) -> None:
    assert equivalence(left_point == right_point,
                       hash(left_point) == hash(right_point))
