from hypothesis import given

from gon.degenerate import Empty
from tests.utils import implication
from . import strategies


@given(strategies.empty_geometries)
def test_determinism(empty: Empty) -> None:
    result = hash(empty)

    assert result == hash(empty)


@given(strategies.empty_geometries, strategies.empty_geometries)
def test_connection_with_equality(left_empty: Empty,
                                  right_empty: Empty) -> None:
    assert implication(left_empty == right_empty,
                       hash(left_empty) == hash(right_empty))
