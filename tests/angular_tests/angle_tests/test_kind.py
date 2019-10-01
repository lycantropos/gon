from hypothesis import given

from gon.angular import (Angle,
                         AngleKind)
from tests.utils import reflect_angle
from . import strategies


@given(strategies.angles)
def test_alternatives(angle: Angle) -> None:
    assert angle.kind in AngleKind


@given(strategies.angles)
def test_rays_flip(angle: Angle) -> None:
    flipped_angle = Angle(angle.second_ray_point,
                          angle.vertex,
                          angle.first_ray_point)

    assert angle.kind is flipped_angle.kind


@given(strategies.origin_angles)
def test_origin_angle_reflection(angle: Angle) -> None:
    reflected_angle = reflect_angle(angle)

    assert angle.kind is reflected_angle.kind
