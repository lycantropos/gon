from typing import Tuple

from hypothesis import given

from gon.base import (Angle,
                      Linear,
                      Point)
from . import strategies


@given(strategies.linear_geometries_points_with_angles)
def test_isometry(linear_with_angle: Tuple[Tuple[Linear, Point], Angle]
                  ) -> None:
    (linear, point), angle = linear_with_angle

    result = linear.rotate(angle, point)

    assert result.length == linear.length
