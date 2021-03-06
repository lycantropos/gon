from typing import Tuple

from hypothesis import given

from gon.linear import Segment
from tests.utils import (implication,
                         reverse_segment)
from . import strategies


@given(strategies.segments)
def test_reflexivity(segment: Segment) -> None:
    assert segment == segment


@given(strategies.segments_pairs)
def test_symmetry(segments_pair: Tuple[Segment, Segment]) -> None:
    left_segment, right_segment = segments_pair

    assert implication(left_segment == right_segment,
                       right_segment == left_segment)


@given(strategies.segments_triplets)
def test_transitivity(segments_triplet: Tuple[Segment, Segment, Segment]
                      ) -> None:
    left_segment, mid_segment, right_segment = segments_triplet

    assert implication(left_segment == mid_segment
                       and mid_segment == right_segment,
                       left_segment == right_segment)


@given(strategies.segments)
def test_reversals(segment: Segment) -> None:
    assert segment == reverse_segment(segment)
