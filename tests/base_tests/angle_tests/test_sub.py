from typing import Tuple

from hypothesis import given

from gon.base import Angle
from tests.utils import (equivalence,
                         not_raises)
from . import strategies


@given(strategies.angles_pairs)
def test_basic(angles_pair: Tuple[Angle, Angle]) -> None:
    first, second = angles_pair

    result = first - second

    assert isinstance(result, Angle)


@given(strategies.angles_pairs)
def test_validity(angles_pair: Tuple[Angle, Angle]) -> None:
    first, second = angles_pair

    result = first - second

    with not_raises(ValueError):
        result.validate()


@given(strategies.zero_angles_with_angles)
def test_third(zero_angle_with_angle
               : Tuple[Angle, Angle]) -> None:
    zero_angle, angle = zero_angle_with_angle

    result = angle - zero_angle

    assert result == angle


@given(strategies.angles_pairs)
def test_commutative_case(angles_pair: Tuple[Angle, Angle]) -> None:
    first, second = angles_pair

    assert equivalence(first - second == second - first,
                       (first.sine * second.cosine
                        == second.sine * first.cosine))


@given(strategies.angles_pairs)
def test_equivalents(angles_pair: Tuple[Angle, Angle]) -> None:
    first, second = angles_pair

    result = first - second

    assert result == first + (-second)
