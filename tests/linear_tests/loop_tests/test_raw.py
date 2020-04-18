from hypothesis import given

from gon.linear import (Loop,
                        RawLoop)
from . import strategies


@given(strategies.loops)
def test_loop_round_trip(loop: Loop) -> None:
    assert Loop.from_raw(loop.raw()) == loop


@given(strategies.raw_loops)
def test_raw_loop_round_trip(raw_loop: RawLoop) -> None:
    assert Loop.from_raw(raw_loop).raw() == raw_loop
