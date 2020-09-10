from typing import Tuple

from hypothesis import given

from gon.compound import Linear
from gon.discrete import Multipoint
from gon.hints import Coordinate
from gon.linear import Segment
from gon.primitive import Point
from . import strategies


@given(strategies.contours_with_zero_non_zero_coordinates)
def test_degenerate(contour_with_zero_non_zero_factors
                    : Tuple[Linear, Coordinate, Coordinate]) -> None:
    contour, zero_factor, non_zero_factors = contour_with_zero_non_zero_factors

    zero_result = contour.scale(zero_factor)
    zero_non_zero_result = contour.scale(zero_factor, non_zero_factors)
    non_zero_zero_result = contour.scale(non_zero_factors, zero_factor)

    assert isinstance(zero_result, Multipoint)
    assert isinstance(zero_non_zero_result, Segment)
    assert isinstance(non_zero_zero_result, Segment)
    assert len(zero_result.points) == 1
    assert zero_result.points[0] == Point(zero_factor, zero_factor)
    assert (zero_non_zero_result.start.x == zero_non_zero_result.end.x
            == zero_factor)
    assert (non_zero_zero_result.start.y == non_zero_zero_result.end.y
            == zero_factor)
