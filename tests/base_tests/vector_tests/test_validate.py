import pytest
from hypothesis import given

from gon.base import Vector
from . import strategies


@given(strategies.vectors)
def test_basic(vector: Vector) -> None:
    result = vector.validate()

    assert result is None


@given(strategies.invalid_vectors)
def test_invalid_vector(vector: Vector) -> None:
    with pytest.raises(ValueError):
        vector.validate()
