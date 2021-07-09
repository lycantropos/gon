from typing import Tuple

from hypothesis import given

from gon.base import Angle
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.angles_pairs)
def test_connection_with_equality(angles_pair: Tuple[Angle, Angle]) -> None:
    first, second = angles_pair

    assert implication(first == second, bool(first) is bool(second))


@given(strategies.angles)
def test_negated(angle: Angle) -> None:
    assert equivalence(bool(angle), bool(-angle))
