from typing import Tuple

from hypothesis import given

from gon.base import (Empty,
                      Point)
from . import strategies


@given(strategies.empty_geometries_with_points)
def test_points(empty_with_point: Tuple[Empty, Point]) -> None:
    empty, point = empty_with_point

    assert point not in empty
