from typing import Tuple

from hypothesis import given

from gon.linear import Loop
from tests.utils import implication
from . import strategies


@given(strategies.loops)
def test_reflexivity(loop: Loop) -> None:
    assert loop == loop


@given(strategies.loops_pairs)
def test_symmetry(loops_pair: Tuple[Loop, Loop]) -> None:
    left_loop, right_loop = loops_pair

    assert implication(left_loop == right_loop,
                       right_loop == left_loop)


@given(strategies.loops_triplets)
def test_transitivity(loops_triplet: Tuple[Loop, Loop, Loop]
                      ) -> None:
    left_loop, mid_loop, right_loop = loops_triplet

    assert implication(left_loop == mid_loop == right_loop,
                       left_loop == right_loop)
