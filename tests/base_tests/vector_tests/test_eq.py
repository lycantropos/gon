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
    first, second = vectors_pair

    assert implication(first == second, second == first)


@given(strategies.vectors_pairs)
def test_negation(vectors_pair: Tuple[Vector, Vector]) -> None:
    first, second = vectors_pair

    assert equivalence(first == second, -first == -second)


@given(strategies.vectors_triplets)
def test_transitivity(vectors_triplet: Tuple[Vector, Vector, Vector]) -> None:
    first, second, third = vectors_triplet

    assert implication(first == second == third, first == third)


@given(strategies.vectors_pairs)
def test_alternatives(vectors_pair: Tuple[Vector, Vector]) -> None:
    first, second = vectors_pair

    assert equivalence(first == second,
                       square(first.length)
                       == square(second.length)
                       == first.dot(second))
