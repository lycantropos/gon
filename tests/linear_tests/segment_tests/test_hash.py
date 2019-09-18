from hypothesis import given

from gon.linear import Segment
from tests.utils import implication
from . import strategies


@given(strategies.segments)
def test_basic(segment: Segment) -> None:
    result = hash(segment)

    assert isinstance(result, int)


@given(strategies.segments)
def test_determinism(segment: Segment) -> None:
    result = hash(segment)

    assert result == hash(segment)


@given(strategies.segments, strategies.segments)
def test_connection_with_equality(left_segment: Segment,
                                  right_segment: Segment) -> None:
    assert implication(left_segment == right_segment,
                       hash(left_segment) == hash(right_segment))


@given(strategies.segments)
def test_independence_from_ends_order(segment: Segment) -> None:
    reversed_segment = Segment(segment.end, segment.start)

    assert hash(segment) == hash(reversed_segment)
