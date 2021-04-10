import pytest
from hypothesis import given

from gon.base import Mix
from . import strategies


@given(strategies.mixes)
def test_basic(mix: Mix) -> None:
    result = mix.validate()

    assert result is None


@given(strategies.invalid_mixes)
def test_invalid_mix(mix: Mix) -> None:
    with pytest.raises(ValueError):
        mix.validate()
