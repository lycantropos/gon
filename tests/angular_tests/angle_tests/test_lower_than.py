from hypothesis import given

from gon.angular import Angle
from tests.utils import implication
from . import strategies


@given(strategies.angles)
def test_irreflexivity(angle: Angle) -> None:
    assert not angle < angle


@given(strategies.angles, strategies.angles)
def test_asymmetry(left_angle: Angle, right_angle: Angle) -> None:
    assert implication(left_angle < right_angle,
                       not right_angle < left_angle)


@given(strategies.angles, strategies.angles, strategies.angles)
def test_transitivity(left_angle: Angle,
                      mid_angle: Angle,
                      right_angle: Angle) -> None:
    assert implication(left_angle < mid_angle < right_angle,
                       left_angle < right_angle)
