from typing import Tuple

from hypothesis import given

from gon.base import Multipoint
from tests.utils import implication
from . import strategies


@given(strategies.multipoints)
def test_determinism(multipoint: Multipoint) -> None:
    result = hash(multipoint)

    assert result == hash(multipoint)


@given(strategies.multipoints_pairs)
def test_connection_with_equality(multipoints_pair: Tuple[Multipoint,
                                                          Multipoint]) -> None:
    left_multipoint, right_multipoint = multipoints_pair

    assert implication(left_multipoint == right_multipoint,
                       hash(left_multipoint) == hash(right_multipoint))
