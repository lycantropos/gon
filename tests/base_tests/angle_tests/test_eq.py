from typing import Tuple

from hypothesis import given

from gon.base import Angle
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.angles)
def test_reflexivity(angle: Angle) -> None:
    assert angle == angle


@given(strategies.angles_pairs)
def test_symmetry(angles_pair: Tuple[Angle, Angle]) -> None:
    first, second = angles_pair

    assert implication(first == second, second == first)


@given(strategies.angles_pairs)
def test_negation(angles_pair: Tuple[Angle, Angle]) -> None:
    first, second = angles_pair

    assert equivalence(first == second, -first == -second)


@given(strategies.angles_triplets)
def test_transitivity(angles_triplet: Tuple[Angle, Angle, Angle]) -> None:
    first, second, third = angles_triplet

    assert implication(first == second == third, first == third)
