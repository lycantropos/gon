from typing import Sequence

from hypothesis import given

from gon.base import Point
from gon.shaped.contracts import self_intersects
from . import strategies


@given(strategies.triangles_vertices)
def test_triangle_vertices(vertices: Sequence[Point]) -> None:
    assert not self_intersects(vertices)
