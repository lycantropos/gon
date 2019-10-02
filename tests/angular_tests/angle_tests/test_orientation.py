from hypothesis import given

from gon.angular import (Angle,
                         Orientation)
from tests.utils import (has_opposite_orientations,
                         reflect_angle)
from . import strategies


@given(strategies.angles)
def test_alternatives(angle: Angle) -> None:
    assert angle.orientation in Orientation


@given(strategies.straight_origin_angles)
def test_straight_angle(angle: Angle) -> None:
    assert angle.orientation is Orientation.COLLINEAR


@given(strategies.right_origin_angles)
def test_right_angle(angle: Angle) -> None:
    assert angle.orientation is not Orientation.COLLINEAR


@given(strategies.angles)
def test_rays_flip(angle: Angle) -> None:
    flipped_angle = Angle(angle.second_ray_point,
                          angle.vertex,
                          angle.first_ray_point)

    assert has_opposite_orientations(angle, flipped_angle)


@given(strategies.origin_angles)
def test_origin_angle_reflection(angle: Angle) -> None:
    reflected_angle = reflect_angle(angle)

    assert angle.orientation is reflected_angle.orientation
