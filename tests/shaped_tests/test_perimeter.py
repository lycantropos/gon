from hypothesis import given
from symba.base import Expression

from gon.compound import Shaped
from . import strategies


@given(strategies.shaped_geometries)
def test_basic(shaped: Shaped) -> None:
    assert isinstance(shaped.perimeter, Expression)


@given(strategies.shaped_geometries)
def test_properties(shaped: Shaped) -> None:
    result = shaped.perimeter

    assert result > 0
