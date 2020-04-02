from typing import Tuple

from hypothesis import given

from gon.segment import (Segment,
                         SegmentsRelationship)
from tests.utils import (reflect_segment,
                         reverse_segment)
from . import strategies


@given(strategies.segments)
def test_relationship_with_self(segment: Segment) -> None:
    assert segment.relationship_with(segment) is SegmentsRelationship.OVERLAP


@given(strategies.segments_pairs)
def test_commutativity(segments_pair: Tuple[Segment, Segment]) -> None:
    segment, other_segment = segments_pair

    assert (segment.relationship_with(other_segment)
            is other_segment.relationship_with(segment))


@given(strategies.segments_pairs)
def test_independence_from_ends_order(segments_pair: Tuple[Segment, Segment]
                                      ) -> None:
    segment, other_segment = segments_pair

    assert (segment.relationship_with(other_segment)
            is reverse_segment(segment).relationship_with(other_segment))


@given(strategies.segments)
def test_reflection(segment: Segment) -> None:
    reflected_segment = reflect_segment(segment)

    assert (segment.relationship_with(reflected_segment)
            is SegmentsRelationship.TOUCH)
