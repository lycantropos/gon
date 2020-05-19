from hypothesis import given

from gon.degenerate import Empty
from . import strategies


@given(strategies.empty_geometries_with_points)
def test_points(empty_with_point: Empty) -> None:
    empty, point = empty_with_point

    assert point not in empty
