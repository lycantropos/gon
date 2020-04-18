import pytest
from hypothesis import given

from gon.linear import Loop
from . import strategies


@given(strategies.loops)
def test_basic(loop: Loop) -> None:
    result = loop.validate()

    assert result is None


@given(strategies.invalid_loops)
def test_invalid_loop(loop: Loop) -> None:
    with pytest.raises(ValueError):
        loop.validate()
