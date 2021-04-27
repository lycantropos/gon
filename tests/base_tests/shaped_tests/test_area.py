import math
from numbers import Real

from hypothesis import given

from gon.base import Shaped
from . import strategies


@given(strategies.shaped_geometries)
def test_basic(shaped: Shaped) -> None:
    assert isinstance(shaped.area, Real)


@given(strategies.shaped_geometries)
def test_value(shaped: Shaped) -> None:
    result = shaped.area

    assert 0 < result < math.inf
