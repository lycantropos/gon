from typing import Tuple

from hypothesis import given

from gon.base import Angle
from tests.utils import not_raises
from . import strategies


@given(strategies.angles_pairs)
def test_basic(angles_pair: Tuple[Angle, Angle]) -> None:
    first, second = angles_pair

    result = first + second

    assert isinstance(result, Angle)


@given(strategies.angles_pairs)
def test_validity(angles_pair: Tuple[Angle, Angle]) -> None:
    first, second = angles_pair

    result = first + second

    with not_raises(ValueError):
        result.validate()


@given(strategies.zero_angles_with_angles)
def test_left_neutral_element(zero_angle_with_angle: Tuple[Angle, Angle]
                              ) -> None:
    zero_angle, angle = zero_angle_with_angle

    result = zero_angle + angle

    assert result == angle


@given(strategies.zero_angles_with_angles)
def test_right_neutral_element(zero_angle_with_angle: Tuple[Angle, Angle]
                               ) -> None:
    zero_angle, angle = zero_angle_with_angle

    result = angle + zero_angle

    assert result == angle


@given(strategies.angles_pairs)
def test_commutativity(angles_pair: Tuple[Angle, Angle]) -> None:
    first, second = angles_pair

    result = first + second

    assert result == second + first


@given(strategies.angles_triplets)
def test_associativity(angles_triplet: Tuple[Angle, Angle, Angle]
                       ) -> None:
    first, second, third = angles_triplet

    result = (first + second) + third

    assert result == first + (second + third)


@given(strategies.angles_pairs)
def test_equivalents(angles_pair: Tuple[Angle, Angle]) -> None:
    first, second = angles_pair

    result = first + second

    assert result == first - (-second)
