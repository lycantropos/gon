import pytest
from hypothesis import given

from gon.linear import Multisegment
from . import strategies


@given(strategies.multisegments)
def test_basic(multisegment: Multisegment) -> None:
    result = multisegment.validate()

    assert result is None


@given(strategies.invalid_multisegments)
def test_invalid_multisegment(multisegment: Multisegment) -> None:
    with pytest.raises(ValueError):
        multisegment.validate()
