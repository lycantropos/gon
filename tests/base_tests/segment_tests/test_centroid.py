from hypothesis import given

from gon.base import Segment
from . import strategies


@given(strategies.segments)
def test_connection_with_contains(segment: Segment) -> None:
    assert segment.centroid in segment
