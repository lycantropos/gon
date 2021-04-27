from typing import Tuple

from hypothesis import given

from gon.base import Linear
from gon.hints import Coordinate
from . import strategies


@given(strategies.rational_linear_geometries_with_coordinates_pairs)
def test_isometry(linear_with_steps: Tuple[Linear, Coordinate, Coordinate]
                  ) -> None:
    linear, step_x, step_y = linear_with_steps

    result = linear.translate(step_x, step_y)

    assert result.length == linear.length
