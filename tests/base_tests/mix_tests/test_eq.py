from typing import Tuple

from hypothesis import given

from gon.base import Mix
from tests.utils import implication
from . import strategies


@given(strategies.mixes)
def test_reflexivity(mix: Mix) -> None:
    assert mix == mix


@given(strategies.mixes_pairs)
def test_symmetry(mixes_pair: Tuple[Mix, Mix]) -> None:
    first, second = mixes_pair

    assert implication(first == second, second == first)


@given(strategies.mixes_triplets)
def test_transitivity(mixes_triplet: Tuple[Mix, Mix, Mix]) -> None:
    first, second, third = mixes_triplet

    assert implication(first == second == third, first == third)
