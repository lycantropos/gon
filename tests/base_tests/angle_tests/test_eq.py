from typing import Tuple

from hypothesis import given

from gon.base import Angle
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.angles)
def test_reflexivity(angle: Angle) -> None:
    assert angle == angle


@given(strategies.angles_pairs)
def test_symmetry(angles_pair: Tuple[Angle, Angle]) -> None:
    left_angle, right_angle = angles_pair

    assert implication(left_angle == right_angle,
                       right_angle == left_angle)


@given(strategies.angles_pairs)
def test_negation(angles_pair: Tuple[Angle, Angle]) -> None:
    left_angle, right_angle = angles_pair

    assert equivalence(left_angle == right_angle,
                       -left_angle == -right_angle)


@given(strategies.angles_triplets)
def test_transitivity(angles_triplet: Tuple[Angle, Angle, Angle]) -> None:
    left_angle, mid_angle, right_angle = angles_triplet

    assert implication(left_angle == mid_angle == right_angle,
                       left_angle == right_angle)
