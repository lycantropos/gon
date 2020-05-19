from hypothesis import given

from gon.degenerate import Empty
from . import strategies


@given(strategies.empty_geometries)
def test_basic(empty: Empty) -> None:
    result = empty.validate()

    assert result is None
