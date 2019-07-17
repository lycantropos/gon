import pytest
from hypothesis import given

from gon.base import Point
from gon.linear import to_interval
from tests import strategies


@given(strategies.points)
def test_degenerate_case(point: Point) -> None:
    with pytest.raises(ValueError):
        to_interval(point, point)
