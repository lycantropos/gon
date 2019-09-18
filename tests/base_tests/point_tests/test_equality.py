from typing import Any

from hypothesis import given

from gon.linear import Point
from tests.utils import implication
from . import strategies


@given(strategies.points)
def test_reflexivity(point: Point) -> None:
    assert point == point


@given(strategies.points, strategies.points)
def test_symmetry(left_point: Point, right_point: Point) -> None:
    assert implication(left_point == right_point, right_point == left_point)


@given(strategies.points, strategies.points, strategies.points)
def test_transitivity(left_point: Point,
                      mid_point: Point,
                      right_point: Point) -> None:
    assert implication(left_point == mid_point and mid_point == right_point,
                       left_point == right_point)


@given(strategies.points, strategies.non_points)
def test_non_point(point: Point, non_point: Any) -> None:
    assert point != non_point
