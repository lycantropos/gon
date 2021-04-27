import math

from hypothesis import given

from gon.base import Linear
from tests.utils import is_scalar
from . import strategies


@given(strategies.linear_geometries)
def test_basic(linear: Linear) -> None:
    assert is_scalar(linear.length)


@given(strategies.linear_geometries)
def test_value(linear: Linear) -> None:
    result = linear.length

    assert 0 < result < math.inf
