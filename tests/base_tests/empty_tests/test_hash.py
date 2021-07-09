from hypothesis import given

from gon.base import Empty
from tests.utils import implication
from . import strategies


@given(strategies.empty_geometries)
def test_determinism(empty: Empty) -> None:
    result = hash(empty)

    assert result == hash(empty)


@given(strategies.empty_geometries, strategies.empty_geometries)
def test_connection_with_equality(first: Empty,
                                  third: Empty) -> None:
    assert implication(first == third,
                       hash(first) == hash(third))
