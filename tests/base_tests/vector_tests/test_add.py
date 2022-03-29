from typing import Tuple

from hypothesis import given

from gon.base import Vector
from gon.hints import Scalar
from tests.utils import not_raises
from . import strategies


@given(strategies.vectors_pairs)
def test_basic(vectors_pair: Tuple[Vector, Vector]) -> None:
    first, second = vectors_pair

    result = first + second

    assert isinstance(result, Vector)


@given(strategies.vectors_pairs)
def test_validity(vectors_pair: Tuple[Vector, Vector]) -> None:
    first, second = vectors_pair

    result = first + second

    with not_raises(ValueError):
        result.validate()


@given(strategies.zero_vectors_with_vectors)
def test_left_neutral_element(zero_vector_with_vector: Tuple[Vector, Vector]
                              ) -> None:
    zero_vector, vector = zero_vector_with_vector

    result = zero_vector + vector

    assert result == vector


@given(strategies.zero_vectors_with_vectors)
def test_right_neutral_element(zero_vector_with_vector: Tuple[Vector, Vector]
                               ) -> None:
    zero_vector, vector = zero_vector_with_vector

    result = vector + zero_vector

    assert result == vector


@given(strategies.vectors_pairs)
def test_commutativity(vectors_pair: Tuple[Vector, Vector]) -> None:
    first, second = vectors_pair

    result = first + second

    assert result == second + first


@given(strategies.vectors_triplets)
def test_associativity(vectors_triplet: Tuple[Vector, Vector, Vector]
                       ) -> None:
    first, second, third = vectors_triplet

    result = (first + second) + third

    assert result == first + (second + third)


@given(strategies.vectors_pairs_with_scalars)
def test_distribution_over_scalar_multiplication(
        vectors_pair_with_scalar: Tuple[Vector, Vector, Scalar]
) -> None:
    first, second, scalar = vectors_pair_with_scalar

    result = scalar * (first + second)

    assert result == (scalar * first) + (scalar * second)


@given(strategies.vectors_pairs)
def test_equivalents(vectors_pair: Tuple[Vector, Vector]) -> None:
    first, second = vectors_pair

    result = first + second

    assert result == first - (-second)
