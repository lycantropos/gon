from typing import Tuple

from hypothesis import given

from gon.base import Multisegment
from tests.utils import (implication,
                         reverse_multisegment)
from . import strategies


@given(strategies.multisegments)
def test_basic(multisegment: Multisegment) -> None:
    result = hash(multisegment)

    assert isinstance(result, int)


@given(strategies.multisegments)
def test_determinism(multisegment: Multisegment) -> None:
    result = hash(multisegment)

    assert result == hash(multisegment)


@given(strategies.multisegments_pairs)
def test_connection_with_equality(
        multisegments_pair: Tuple[Multisegment, Multisegment]
) -> None:
    first, second = multisegments_pair

    assert implication(first == second, hash(first) == hash(second))


@given(strategies.multisegments)
def test_reversals(multisegment: Multisegment) -> None:
    assert hash(multisegment) == hash(reverse_multisegment(multisegment))
