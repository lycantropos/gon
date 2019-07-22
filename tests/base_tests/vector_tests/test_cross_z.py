from hypothesis import given

from gon.base import Vector
from . import strategies


@given(strategies.vectors)
def test_self_multiplication(vector: Vector) -> None:
    assert not vector.cross_z(vector)


@given(strategies.vectors, strategies.vectors)
def test_anticommutativity(vector: Vector, other_vector: Vector) -> None:
    assert vector.cross_z(other_vector) == -other_vector.cross_z(vector)
