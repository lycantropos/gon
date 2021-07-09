from typing import Tuple

from hypothesis import given

from gon.base import Multipoint
from tests.utils import (implication,
                         reverse_multipoint,
                         shift_multipoint)
from . import strategies


@given(strategies.multipoints)
def test_reflexivity(multipoint: Multipoint) -> None:
    assert multipoint == multipoint


@given(strategies.multipoints_pairs)
def test_symmetry(multipoints_pair: Tuple[Multipoint, Multipoint]) -> None:
    first, second = multipoints_pair

    assert implication(first == second, second == first)


@given(strategies.multipoints_triplets)
def test_transitivity(multipoints_triplet: Tuple[Multipoint, Multipoint,
                                                 Multipoint]) -> None:
    first, second, third = multipoints_triplet

    assert implication(first == second == third, first == third)


@given(strategies.multipoints)
def test_reversed(multipoint: Multipoint) -> None:
    assert multipoint == reverse_multipoint(multipoint)


@given(strategies.multipoints)
def test_shifted(multipoint: Multipoint) -> None:
    assert all(multipoint == shift_multipoint(multipoint, step)
               for step in range(len(multipoint.points)))
