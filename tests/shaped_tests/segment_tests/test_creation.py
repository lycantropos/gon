import pytest
from hypothesis import given

from gon.base import Point
from gon.shaped import Segment
from tests import strategies


@given(strategies.points)
def test_degenerate_case(point: Point) -> None:
    with pytest.raises(ValueError):
        Segment(point, point)
