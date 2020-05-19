from hypothesis import given

from gon.degenerate import (Empty,
                            RawEmpty)
from . import strategies


@given(strategies.empty_geometries)
def test_empty_round_trip(empty: Empty) -> None:
    assert empty.from_raw(empty.raw()) == empty


@given(strategies.raw_empty_geometries)
def test_raw_empty_round_trip(raw_empty: RawEmpty) -> None:
    assert Empty.from_raw(raw_empty).raw() == raw_empty
