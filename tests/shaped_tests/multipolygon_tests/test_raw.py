from hypothesis import given

from gon.shaped import (Multipolygon,
                        RawMultipolygon)
from . import strategies


@given(strategies.multipolygons)
def test_multipolygon_round_trip(multipolygon: Multipolygon) -> None:
    assert Multipolygon.from_raw(multipolygon.raw()) == multipolygon


@given(strategies.raw_multipolygons)
def test_raw_multipolygon_round_trip(raw_multipolygon: RawMultipolygon
                                     ) -> None:
    assert Multipolygon.from_raw(raw_multipolygon).raw() == raw_multipolygon
