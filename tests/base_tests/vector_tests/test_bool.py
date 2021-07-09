from typing import Tuple

from hypothesis import given

from gon.base import Vector
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.vectors_pairs)
def test_connection_with_equality(vectors_pair: Tuple[Vector, Vector]) -> None:
    first, second = vectors_pair

    assert implication(first == second, bool(first) is bool(second))


@given(strategies.vectors)
def test_negated(vector: Vector) -> None:
    assert equivalence(bool(vector), bool(-vector))
