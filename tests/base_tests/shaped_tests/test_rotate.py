from typing import Tuple

from hypothesis import given

from gon.base import (Angle,
                      Point,
                      Shaped)
from . import strategies


@given(strategies.shaped_geometries_points_with_angles)
def test_isometry(shaped_with_angle: Tuple[Tuple[Shaped, Point], Angle]
                  ) -> None:
    (shaped, point), angle = shaped_with_angle

    result = shaped.rotate(angle, point)

    assert result.area == shaped.area
    assert result.perimeter == shaped.perimeter
