import pytest
from hypothesis import given

from gon.compound import Compound
from gon.primitive import Point
from . import strategies


@given(strategies.non_empty_compounds)
def test_basic(compound: Compound) -> None:
    result = compound.centroid

    assert isinstance(result, Point)


@given(strategies.empty_compounds)
def test_empty(compound: Compound) -> None:
    with pytest.raises(ValueError):
        compound.centroid
