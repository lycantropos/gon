import math

from hypothesis import given

from gon.compound import Shaped
from gon.hints import Coordinate
from . import strategies


@given(strategies.shaped_geometries)
def test_basic(shaped: Shaped) -> None:
    assert isinstance(shaped.area, Coordinate)


@given(strategies.shaped_geometries)
def test_properties(shaped: Shaped) -> None:
    result = shaped.area

    assert math.isfinite(result)
    assert result > 0
