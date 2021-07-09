from typing import Tuple

from hypothesis import given

from gon.base import Angle
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.angles)
def test_basic(angle: Angle) -> None:
    result = hash(angle)

    assert isinstance(result, int)


@given(strategies.angles)
def test_determinism(angle: Angle) -> None:
    result = hash(angle)

    assert result == hash(angle)


@given(strategies.angles_pairs)
def test_connection_with_equality(angles_pair: Tuple[Angle, Angle]
                                  ) -> None:
    left_angle, right_angle = angles_pair

    assert implication(left_angle == right_angle,
                       hash(left_angle) == hash(right_angle))


@given(strategies.angles)
def test_negated(angle: Angle) -> None:
    assert equivalence(hash(angle) == hash(-angle), not angle)
