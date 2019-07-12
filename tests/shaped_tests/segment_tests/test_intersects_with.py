from typing import Tuple

from hypothesis import given

from gon.shaped import Segment
from tests import strategies
from tests.utils import implication


@given(strategies.segments)
def test_reflexivity(segment: Segment) -> None:
    assert segment.intersects_with(segment)


@given(strategies.segments_pairs)
def test_symmetry(segments_pair: Tuple[Segment, Segment]) -> None:
    segment, other_segment = segments_pair

    assert implication(segment.intersects_with(other_segment),
                       other_segment.intersects_with(segment))


@given(strategies.segments_pairs)
def test_independence_from_ends_order(segments_pair: Tuple[Segment, Segment]
                                      ) -> None:
    segment, other_segment = segments_pair
    reversed_segment = Segment(segment.second_end, segment.first_end)

    assert implication(segment.intersects_with(other_segment),
                       reversed_segment.intersects_with(other_segment))
