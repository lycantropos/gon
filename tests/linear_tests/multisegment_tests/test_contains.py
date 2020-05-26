from hypothesis import given

from gon.linear import Multisegment
from . import strategies


@given(strategies.multisegments)
def test_endpoints(multisegment: Multisegment) -> None:
    assert all(segment.start in multisegment
               and segment.end in multisegment
               for segment in multisegment.segments)
