import pytest
from hypothesis import given

from gon.linear import Segment
from . import strategies


@given(strategies.segments)
def test_basic(segment: Segment) -> None:
    result = segment.validate()

    assert result is None


@given(strategies.invalid_segments)
def test_invalid_segment(segment: Segment) -> None:
    with pytest.raises(ValueError):
        segment.validate()
