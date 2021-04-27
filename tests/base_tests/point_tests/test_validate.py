import pytest
from hypothesis import given

from gon.base import Point
from . import strategies


@given(strategies.points)
def test_basic(point: Point) -> None:
    result = point.validate()

    assert result is None


@given(strategies.invalid_points)
def test_invalid_point(point: Point) -> None:
    with pytest.raises(ValueError):
        point.validate()
