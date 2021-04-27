from hypothesis import given

from gon.base import Segment
from . import strategies


@given(strategies.segments)
def test_endpoints(segment: Segment) -> None:
    assert segment.start in segment
    assert segment.end in segment
