from typing import Tuple

from hypothesis import given

from gon.base import Angle
from tests.utils import (equivalence,
                         not_raises)
from . import strategies


@given(strategies.angles_pairs)
def test_basic(angles_pair: Tuple[Angle, Angle]) -> None:
    left_angle, right_angle = angles_pair

    result = left_angle - right_angle

    assert isinstance(result, Angle)


@given(strategies.angles_pairs)
def test_validity(angles_pair: Tuple[Angle, Angle]) -> None:
    left_angle, right_angle = angles_pair

    result = left_angle - right_angle

    with not_raises(ValueError):
        result.validate()


@given(strategies.zero_angles_with_angles)
def test_right_neutral_element(zero_angle_with_angle
                               : Tuple[Angle, Angle]) -> None:
    zero_angle, angle = zero_angle_with_angle

    result = angle - zero_angle

    assert result == angle


@given(strategies.angles_pairs)
def test_commutative_case(angles_pair: Tuple[Angle, Angle]) -> None:
    left_angle, right_angle = angles_pair

    assert equivalence(left_angle - right_angle
                       == right_angle - left_angle,
                       left_angle == right_angle)


@given(strategies.angles_pairs)
def test_equivalents(angles_pair: Tuple[Angle, Angle]) -> None:
    left_angle, right_angle = angles_pair

    result = left_angle - right_angle

    assert result == left_angle + (-right_angle)
