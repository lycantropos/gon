from typing import Tuple

from hypothesis import given

from gon.base import Mix
from tests.utils import implication
from . import strategies


@given(strategies.mixes)
def test_determinism(mix: Mix) -> None:
    result = hash(mix)

    assert result == hash(mix)


@given(strategies.mixes_pairs)
def test_connection_with_equality(mixes_pair: Tuple[Mix, Mix]) -> None:
    first, second = mixes_pair

    assert implication(first == second, hash(first) == hash(second))
