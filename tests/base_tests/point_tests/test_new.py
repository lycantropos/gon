import pytest
from hypothesis import given

from gon.base import Point
from gon.hints import Scalar
from . import strategies


@given(strategies.invalid_coordinates, strategies.valid_coordinates)
def test_invalid_x_coordinate(x: Scalar, y: Scalar) -> None:
    with pytest.raises(ValueError):
        Point(x, y)


@given(strategies.valid_coordinates, strategies.invalid_coordinates)
def test_invalid_y_coordinate(x: Scalar, y: Scalar) -> None:
    with pytest.raises(ValueError):
        Point(x, y)
