import pytest
from hypothesis import given

from gon.base import Multipoint
from . import strategies


@given(strategies.multipoints)
def test_basic(multipoint: Multipoint) -> None:
    result = multipoint.validate()

    assert result is None


@given(strategies.invalid_multipoints)
def test_invalid_multipoint(multipoint: Multipoint) -> None:
    with pytest.raises(ValueError):
        multipoint.validate()
