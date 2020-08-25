from typing import Tuple

from hypothesis import given

from gon.compound import Linear
from gon.hints import Coordinate
from gon.primitive import Point
from . import strategies


@given(strategies.rational_linear_geometries_points_with_cosines_sines)
def test_isometry(linear_with_cosine_sine: Tuple[Tuple[Linear, Point],
                                                 Tuple[Coordinate, Coordinate]]
                  ) -> None:
    (linear, point), (cosine, sine) = linear_with_cosine_sine

    result = linear.rotate(cosine, sine, point)

    assert result.length == linear.length
