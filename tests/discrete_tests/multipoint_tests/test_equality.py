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
    left_multipoint, right_multipoint = multipoints_pair

    assert implication(left_multipoint == right_multipoint,
                       right_multipoint == left_multipoint)


@given(strategies.multipoints_triplets)
def test_transitivity(multipoints_triplet: Tuple[Multipoint, Multipoint,
                                                 Multipoint]) -> None:
    left_multipoint, mid_multipoint, right_multipoint = multipoints_triplet

    assert implication(left_multipoint == mid_multipoint == right_multipoint,
                       left_multipoint == right_multipoint)


@given(strategies.multipoints)
def test_reversed(multipoint: Multipoint) -> None:
    assert multipoint == reverse_multipoint(multipoint)


@given(strategies.multipoints)
def test_shifted(multipoint: Multipoint) -> None:
    assert all(multipoint == shift_multipoint(multipoint, step)
               for step in range(len(multipoint.points)))
