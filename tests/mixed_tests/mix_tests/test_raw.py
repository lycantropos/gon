from hypothesis import given

from gon.mixed import (Mix,
                       RawMix)
from . import strategies


@given(strategies.mixes)
def test_mix_round_trip(mix: Mix) -> None:
    assert Mix.from_raw(mix.raw()) == mix


@given(strategies.raw_mixes)
def test_raw_mix_round_trip(raw_mix: RawMix) -> None:
    assert Mix.from_raw(raw_mix).raw() == raw_mix
