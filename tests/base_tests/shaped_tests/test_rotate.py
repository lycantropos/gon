from typing import Tuple

from hypothesis import given

from gon.base import (Point,
                      Shaped)
from gon.hints import Scalar
from . import strategies


@given(strategies.rational_shaped_geometries_points_with_cosines_sines)
def test_isometry(shaped_with_cosine_sine: Tuple[Tuple[Shaped, Point],
                                                 Tuple[Scalar, Scalar]]
                  ) -> None:
    (shaped, point), (cosine, sine) = shaped_with_cosine_sine

    result = shaped.rotate(cosine, sine, point)

    assert result.area == shaped.area
    assert result.perimeter == shaped.perimeter
