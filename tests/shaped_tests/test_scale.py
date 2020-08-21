from typing import Tuple

from hypothesis import given

from gon.compound import Shaped
from gon.hints import Coordinate
from . import strategies


@given(strategies.rational_shaped_geometries_with_non_zero_coordinates_pairs)
def test_area(shaped_with_factors: Tuple[Shaped, Coordinate, Coordinate]
              ) -> None:
    shaped, factor_x, factor_y = shaped_with_factors

    result = shaped.scale(factor_x, factor_y)

    assert result.area == shaped.area * abs(factor_x * factor_y)
