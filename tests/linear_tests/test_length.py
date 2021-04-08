import math

from hypothesis import given
from symba.base import Expression

from gon.compound import Linear
from . import strategies


@given(strategies.linear_geometries)
def test_basic(linear: Linear) -> None:
    assert isinstance(linear.length, Expression)


@given(strategies.linear_geometries)
def test_properties(linear: Linear) -> None:
    result = linear.length

    assert math.isfinite(result)
    assert result > 0
