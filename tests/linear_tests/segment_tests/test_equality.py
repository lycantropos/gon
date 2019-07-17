from hypothesis import given

from gon.linear import Segment
from tests.utils import implication
from . import strategies


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


@given(strategies.segments)
def test_independence_from_ends_order(segment: Segment) -> None:
    reversed_segment = Segment(segment.end, segment.start)

    assert segment == reversed_segment
