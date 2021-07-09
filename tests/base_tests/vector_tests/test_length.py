import math
from hypothesis import given

from gon.base import Vector
from tests.utils import (equivalence,
                         is_scalar)
from . import strategies


@given(strategies.vectors)
def test_basic(vector: Vector) -> None:
    assert is_scalar(vector.length)


@given(strategies.vectors)
def test_value(vector: Vector) -> None:
    result = vector.length

    assert 0 <= result < math.inf
    assert equivalence(bool(vector), bool(vector.length))
