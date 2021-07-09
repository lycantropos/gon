from typing import Tuple

from hypothesis import given

from gon.base import Multisegment
from tests.utils import (implication,
                         reverse_multisegment,
                         reverse_multisegment_segments,
                         shift_multisegment)
from . import strategies


@given(strategies.multisegments)
def test_reflexivity(multisegment: Multisegment) -> None:
    assert multisegment == multisegment


@given(strategies.multisegments_pairs)
def test_symmetry(multisegments_pair: Tuple[Multisegment, Multisegment]
                  ) -> None:
    first, second = multisegments_pair

    assert implication(first == second, second == first)


@given(strategies.multisegments_triplets)
def test_transitivity(multisegments_triplet
                      : Tuple[Multisegment, Multisegment, Multisegment]
                      ) -> None:
    first, second, third = multisegments_triplet

    assert implication(first == second and second == third, first == third)


@given(strategies.multisegments)
def test_reversals(multisegment: Multisegment) -> None:
    assert multisegment == reverse_multisegment(multisegment)
    assert multisegment == reverse_multisegment_segments(multisegment)


@given(strategies.multisegments)
def test_shifts(multisegment: Multisegment) -> None:
    assert all(multisegment == shift_multisegment(multisegment, step)
               for step in range(1, len(multisegment.segments)))
