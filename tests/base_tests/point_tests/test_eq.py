from typing import Tuple

from hypothesis import given

from gon.base import Point
from tests.utils import implication
from . import strategies


@given(strategies.points)
def test_reflexivity(point: Point) -> None:
    assert point == point


@given(strategies.points_pairs)
def test_symmetry(points_pair: Tuple[Point, Point]) -> None:
    first, second = points_pair

    assert implication(first == second, second == first)


@given(strategies.points_triplets)
def test_transitivity(points_triplet: Tuple[Point, Point, Point]) -> None:
    first, second, third = points_triplet

    assert implication(first == second and second == third, first == third)
