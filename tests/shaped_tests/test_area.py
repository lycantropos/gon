import math
from numbers import Real

from hypothesis import given

from gon.compound import Shaped
from . import strategies


@given(strategies.shaped_geometries)
def test_basic(shaped: Shaped) -> None:
    assert isinstance(shaped.area, Real)


@given(strategies.shaped_geometries)
def test_properties(shaped: Shaped) -> None:
    result = shaped.area

    assert math.isfinite(result)
    assert result > 0
