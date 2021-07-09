from typing import Tuple

from hypothesis import given

from gon.base import Angle
from tests.utils import not_raises
from . import strategies


@given(strategies.angles_pairs)
def test_basic(angles_pair: Tuple[Angle, Angle]) -> None:
    left_angle, right_angle = angles_pair

    result = left_angle + right_angle

    assert isinstance(result, Angle)


@given(strategies.angles_pairs)
def test_validity(angles_pair: Tuple[Angle, Angle]) -> None:
    left_angle, right_angle = angles_pair

    result = left_angle + right_angle

    with not_raises(ValueError):
        result.validate()


@given(strategies.zero_angles_with_angles)
def test_left_neutral_element(zero_angle_with_angle: Tuple[Angle, Angle]
                              ) -> None:
    zero_angle, angle = zero_angle_with_angle

    result = zero_angle + angle

    assert result == angle


@given(strategies.zero_angles_with_angles)
def test_right_neutral_element(zero_angle_with_angle
                               : Tuple[Angle, Angle]) -> None:
    zero_angle, angle = zero_angle_with_angle

    result = angle + zero_angle

    assert result == angle


@given(strategies.angles_pairs)
def test_commutativity(angles_pair: Tuple[Angle, Angle]) -> None:
    left_angle, right_angle = angles_pair

    result = left_angle + right_angle

    assert result == right_angle + left_angle


@given(strategies.angles_triplets)
def test_associativity(angles_triplet: Tuple[Angle, Angle, Angle]
                       ) -> None:
    left_angle, mid_angle, right_angle = angles_triplet

    result = (left_angle + mid_angle) + right_angle

    assert result == left_angle + (mid_angle + right_angle)


@given(strategies.angles_pairs)
def test_equivalents(angles_pair: Tuple[Angle, Angle]) -> None:
    left_angle, right_angle = angles_pair

    result = left_angle + right_angle

    assert result == left_angle - (-right_angle)
