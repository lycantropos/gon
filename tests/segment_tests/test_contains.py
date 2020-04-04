from typing import Tuple

from hypothesis import given

from gon.angular import Orientation
from gon.linear import Segment
from gon.primitive import Point
from tests.utils import implication
from . import strategies


@given(strategies.segments)
def test_endpoints(segment: Segment) -> None:
    assert segment.start in segment
    assert segment.end in segment


@given(strategies.segments_with_points)
def test_orientation(segment_with_point: Tuple[Segment, Point]) -> None:
    segment, point = segment_with_point

    assert implication(point in segment,
                       segment.orientation_with(point)
                       is Orientation.COLLINEAR)
