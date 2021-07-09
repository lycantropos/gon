from hypothesis import given

from gon.base import Vector
from . import strategies


@given(strategies.vectors)
def test_basic(vector: Vector) -> None:
    result = -vector

    assert isinstance(result, Vector)


@given(strategies.vectors)
def test_involution(vector: Vector) -> None:
    result = -vector

    assert -result == vector
