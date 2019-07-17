from hypothesis import given

from gon.shaped import Segment
from tests import strategies
from tests.utils import equivalence


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
    assert equivalence(left_segment == right_segment,
                       hash(left_segment) == hash(right_segment))
