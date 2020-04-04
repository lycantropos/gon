import pytest
from hypothesis import given

from gon.hints import Coordinate
from gon.primitive import Point
from . import strategies


@given(strategies.invalid_coordinates, strategies.valid_coordinates)
def test_invalid_x_coordinate(x: Coordinate, y: Coordinate) -> None:
    point = Point(x, y)

    with pytest.raises(ValueError):
        point.validate()


@given(strategies.valid_coordinates, strategies.invalid_coordinates)
def test_invalid_y_coordinate(x: Coordinate, y: Coordinate) -> None:
    point = Point(x, y)

    with pytest.raises(ValueError):
        point.validate()
