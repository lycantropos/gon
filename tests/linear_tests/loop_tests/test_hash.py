from typing import Tuple

from hypothesis import given

from gon.linear import Loop
from tests.utils import implication
from . import strategies


@given(strategies.loops)
def test_determinism(loop: Loop) -> None:
    result = hash(loop)

    assert result == hash(loop)


@given(strategies.loops_pairs)
def test_connection_with_equality(loops_pair: Tuple[Loop, Loop]
                                  ) -> None:
    left_loop, right_loop = loops_pair

    assert implication(left_loop == right_loop,
                       hash(left_loop) == hash(right_loop))
