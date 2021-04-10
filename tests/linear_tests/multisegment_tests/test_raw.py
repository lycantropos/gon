from hypothesis import given

from gon.base import Multisegment
from gon.raw import RawMultisegment
from . import strategies


@given(strategies.multisegments)
def test_multisegment_round_trip(multisegment: Multisegment) -> None:
    assert Multisegment.from_raw(multisegment.raw()) == multisegment


@given(strategies.raw_multisegments)
def test_raw_multisegment_round_trip(raw_multisegment: RawMultisegment
                                     ) -> None:
    assert Multisegment.from_raw(raw_multisegment).raw() == raw_multisegment
