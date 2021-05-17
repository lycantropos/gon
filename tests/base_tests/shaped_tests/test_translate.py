from typing import Tuple

from hypothesis import given

from gon.base import Shaped
from gon.hints import Scalar
from . import strategies


@given(strategies.rational_shaped_geometries_with_coordinates_pairs)
def test_isometry(shaped_with_steps: Tuple[Shaped, Scalar, Scalar]) -> None:
    shaped, step_x, step_y = shaped_with_steps

    result = shaped.translate(step_x, step_y)

    assert result.area == shaped.area
    assert result.perimeter == shaped.perimeter
