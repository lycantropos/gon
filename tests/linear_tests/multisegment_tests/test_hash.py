from typing import Tuple

from hypothesis import given

from gon.linear import Multisegment
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
    left_multisegment, right_multisegment = multisegments_pair

    assert implication(left_multisegment == right_multisegment,
                       hash(left_multisegment) == hash(right_multisegment))


@given(strategies.multisegments)
def test_reversals(multisegment: Multisegment) -> None:
    assert hash(multisegment) == hash(reverse_multisegment(multisegment))
