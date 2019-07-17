from hypothesis import given

from gon.shaped import Segment
from tests import strategies
from tests.utils import implication


@given(strategies.segments)
def test_reflexivity(segment: Segment) -> None:
    assert segment == segment


@given(strategies.segments, strategies.segments)
def test_symmetry(left_segment: Segment, right_segment: Segment) -> None:
    assert implication(left_segment == right_segment,
                       right_segment == left_segment)


@given(strategies.segments, strategies.segments, strategies.segments)
def test_transitivity(left_segment: Segment,
                      mid_segment: Segment,
                      right_segment: Segment) -> None:
    assert implication(left_segment == mid_segment
                       and mid_segment == right_segment,
                       left_segment == right_segment)
