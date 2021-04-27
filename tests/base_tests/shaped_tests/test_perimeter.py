import math

from hypothesis import given

from gon.base import Shaped
from tests.utils import is_scalar
from . import strategies


@given(strategies.shaped_geometries)
def test_basic(shaped: Shaped) -> None:
    assert is_scalar(shaped.perimeter)


@given(strategies.shaped_geometries)
def test_value(shaped: Shaped) -> None:
    result = shaped.perimeter

    assert 0 < result < math.inf
