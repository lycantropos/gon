from hypothesis import given

from gon.discrete import (Multipoint,
                          RawMultipoint)
from . import strategies


@given(strategies.multipoints)
def test_multipoint_round_trip(multipoint: Multipoint) -> None:
    assert multipoint.from_raw(multipoint.raw()) == multipoint


@given(strategies.raw_multipoints)
def test_raw_multipoint_round_trip(raw_multipoint: RawMultipoint) -> None:
    assert Multipoint.from_raw(raw_multipoint).raw() == raw_multipoint
