from typing import Tuple

from hypothesis import given
from lz.reversal import reverse

from gon.base import Segment
from gon.shaped import segments_intersect
from tests import strategies
from tests.utils import implication


@given(strategies.segments)
def test_reflexivity(segment: Segment) -> None:
    assert segments_intersect(segment, segment)


@given(strategies.segments_pairs)
def test_symmetry(segments_pair: Tuple[Segment, Segment]) -> None:
    segment, other_segment = segments_pair

    assert implication(segments_intersect(segment, other_segment),
                       segments_intersect(other_segment, segment))


@given(strategies.segments_pairs)
def test_independence_from_points_order(segments_pair: Tuple[Segment, Segment]
                                        ) -> None:
    segment, other_segment = segments_pair

    assert implication(segments_intersect(segment, other_segment),
                       segments_intersect(reverse(segment), other_segment))
