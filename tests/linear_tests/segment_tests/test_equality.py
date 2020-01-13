from typing import (Any,
                    Tuple)

from hypothesis import given

from gon.linear import Segment
from tests.utils import implication
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
def test_independence_from_ends_order(segment: Segment) -> None:
    reversed_segment = Segment(segment.end, segment.start)

    assert segment == reversed_segment


@given(strategies.segments, strategies.non_segments)
def test_non_segment(segment: Segment, non_segment: Any) -> None:
    assert segment != non_segment
