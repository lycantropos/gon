from typing import Tuple

from hypothesis import given

from gon.base import Vector
from gon.hints import Scalar
from tests.utils import (equivalence,
                         not_raises)
from . import strategies


@given(strategies.vectors_pairs)
def test_basic(vectors_pair: Tuple[Vector, Vector]) -> None:
    left_vector, right_vector = vectors_pair

    result = left_vector - right_vector

    assert isinstance(result, Vector)


@given(strategies.vectors_pairs)
def test_validity(vectors_pair: Tuple[Vector, Vector]) -> None:
    left_vector, right_vector = vectors_pair

    result = left_vector - right_vector

    with not_raises(ValueError):
        result.validate()


@given(strategies.zero_vectors_with_vectors)
def test_right_neutral_element(zero_vector_with_vector
                               : Tuple[Vector, Vector]) -> None:
    zero_vector, vector = zero_vector_with_vector

    result = vector - zero_vector

    assert result == vector


@given(strategies.vectors_pairs)
def test_commutative_case(vectors_pair: Tuple[Vector, Vector]) -> None:
    left_vector, right_vector = vectors_pair

    assert equivalence(left_vector - right_vector
                       == right_vector - left_vector,
                       left_vector == right_vector)


@given(strategies.vectors_pairs_with_scalars)
def test_distribution_over_scalar_multiplication(
        vectors_pair_with_scalar: Tuple[Vector, Vector, Scalar]
) -> None:
    left_vector, right_vector, scalar = vectors_pair_with_scalar

    result = scalar * (left_vector - right_vector)

    assert result == (scalar * left_vector) - (scalar * right_vector)


@given(strategies.vectors_pairs)
def test_equivalents(vectors_pair: Tuple[Vector, Vector]) -> None:
    left_vector, right_vector = vectors_pair

    result = left_vector - right_vector

    assert result == left_vector + (-right_vector)