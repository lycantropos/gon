from typing import Tuple

from hypothesis import given

from gon.base import Vector
from tests.utils import (equivalence,
                         implication,
                         square)
from . import strategies


@given(strategies.vectors)
def test_reflexivity(vector: Vector) -> None:
    assert vector == vector


@given(strategies.vectors_pairs)
def test_symmetry(vectors_pair: Tuple[Vector, Vector]) -> None:
    left_vector, right_vector = vectors_pair

    assert implication(left_vector == right_vector,
                       right_vector == left_vector)


@given(strategies.vectors_pairs)
def test_negation(vectors_pair: Tuple[Vector, Vector]) -> None:
    left_vector, right_vector = vectors_pair

    assert equivalence(left_vector == right_vector,
                       -left_vector == -right_vector)


@given(strategies.vectors_triplets)
def test_transitivity(vectors_triplet: Tuple[Vector, Vector, Vector]) -> None:
    left_vector, mid_vector, right_vector = vectors_triplet

    assert implication(left_vector == mid_vector == right_vector,
                       left_vector == right_vector)


@given(strategies.vectors_pairs)
def test_alternatives(vectors_pair: Tuple[Vector, Vector]) -> None:
    left_vector, right_vector = vectors_pair

    assert equivalence(left_vector == right_vector,
                       square(left_vector.length)
                       == square(right_vector.length)
                       == left_vector.dot(right_vector))
