import pytest
from hypothesis import given

from gon.shaped import Multipolygon
from . import strategies


@given(strategies.multipolygons)
def test_basic(multipolygon: Multipolygon) -> None:
    result = multipolygon.validate()

    assert result is None


@given(strategies.invalid_multipolygons)
def test_invalid_multipolygon(multipolygon: Multipolygon) -> None:
    with pytest.raises(ValueError):
        multipolygon.validate()
