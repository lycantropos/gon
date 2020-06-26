from typing import Tuple

from hypothesis import given

from gon.mixed import Mix
from tests.utils import implication
from . import strategies


@given(strategies.mixes)
def test_reflexivity(mix: Mix) -> None:
    assert mix == mix


@given(strategies.mixes_pairs)
def test_symmetry(mixes_pair: Tuple[Mix, Mix]) -> None:
    left_mix, right_mix = mixes_pair

    assert implication(left_mix == right_mix, right_mix == left_mix)


@given(strategies.mixes_triplets)
def test_transitivity(mixes_triplet: Tuple[Mix, Mix, Mix]) -> None:
    left_mix, mid_mix, right_mix = mixes_triplet

    assert implication(left_mix == mid_mix == right_mix, left_mix == right_mix)
