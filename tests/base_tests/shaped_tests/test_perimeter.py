import math

from hypothesis import given
from symba.base import Expression

from gon.base import Shaped
from . import strategies


@given(strategies.shaped_geometries)
def test_basic(shaped: Shaped) -> None:
    assert isinstance(shaped.perimeter, Expression)


@given(strategies.shaped_geometries)
def test_value(shaped: Shaped) -> None:
    result = shaped.perimeter

    assert 0 < result < math.inf
