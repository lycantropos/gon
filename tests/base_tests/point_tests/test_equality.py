from typing import (Any,
                    Tuple)

from hypothesis import given

from gon.linear import Point
from tests.utils import implication
from . import strategies


@given(strategies.points)
def test_reflexivity(point: Point) -> None:
    assert point == point


@given(strategies.points_pairs)
def test_symmetry(points_pair: Tuple[Point, Point]) -> None:
    left_point, right_point = points_pair

    assert implication(left_point == right_point, right_point == left_point)


@given(strategies.points_triplets)
def test_transitivity(points_triplet: Tuple[Point, Point, Point]) -> None:
    left_point, mid_point, right_point = points_triplet

    assert implication(left_point == mid_point and mid_point == right_point,
                       left_point == right_point)


@given(strategies.points, strategies.non_points)
def test_non_point(point: Point, non_point: Any) -> None:
    assert point != non_point
