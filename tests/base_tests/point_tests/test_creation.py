import pytest
from hypothesis import given

from gon.base import Point
from gon.hints import Coordinate
from . import strategies


@given(strategies.invalid_coordinates, strategies.valid_coordinates)
def test_invalid_x_coordinate(x: Coordinate, y: Coordinate) -> None:
    with pytest.raises(ValueError):
        Point(x, y)


@given(strategies.valid_coordinates, strategies.invalid_coordinates)
def test_invalid_y_coordinate(x: Coordinate, y: Coordinate) -> None:
    with pytest.raises(ValueError):
        Point(x, y)
