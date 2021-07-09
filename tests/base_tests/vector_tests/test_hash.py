from typing import Tuple

from hypothesis import given

from gon.base import Vector
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.vectors)
def test_basic(vector: Vector) -> None:
    result = hash(vector)

    assert isinstance(result, int)


@given(strategies.vectors)
def test_determinism(vector: Vector) -> None:
    result = hash(vector)

    assert result == hash(vector)


@given(strategies.vectors_pairs)
def test_connection_with_equality(vectors_pair: Tuple[Vector, Vector]
                                  ) -> None:
    left_vector, right_vector = vectors_pair

    assert implication(left_vector == right_vector,
                       hash(left_vector) == hash(right_vector))


@given(strategies.vectors)
def test_negated(vector: Vector) -> None:
    assert equivalence(hash(vector) == hash(-vector), not vector)
