from hypothesis import given

from gon.linear import (Segment,
                        RawSegment)
from . import strategies


@given(strategies.segments)
def test_segment_round_trip(segment: Segment) -> None:
    assert Segment.from_raw(segment.raw()) == segment


@given(strategies.raw_segments)
def test_raw_segment_round_trip(raw_segment: RawSegment) -> None:
    assert Segment.from_raw(raw_segment).raw() == raw_segment
