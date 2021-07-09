from typing import Tuple

from hypothesis import given

from gon.base import Segment
from tests.utils import (implication,
                         reverse_segment)
from . import strategies


@given(strategies.segments)
def test_reflexivity(segment: Segment) -> None:
    assert segment == segment


@given(strategies.segments_pairs)
def test_symmetry(segments_pair: Tuple[Segment, Segment]) -> None:
    first, second = segments_pair

    assert implication(first == second, second == first)


@given(strategies.segments_triplets)
def test_transitivity(segments_triplet: Tuple[Segment, Segment, Segment]
                      ) -> None:
    first, second, third = segments_triplet

    assert implication(first == second and second == third, first == third)


@given(strategies.segments)
def test_reversals(segment: Segment) -> None:
    assert segment == reverse_segment(segment)
