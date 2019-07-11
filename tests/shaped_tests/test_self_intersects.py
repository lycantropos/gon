from itertools import repeat
from typing import Sequence

from hypothesis import given

from gon.base import Point
from gon.shaped import self_intersects
from tests import strategies
from tests.utils import implication


@given(strategies.triangles_vertices)
def test_triangle_vertices(vertices: Sequence[Point]) -> None:
    assert not self_intersects(vertices)


@given(strategies.points, strategies.polygons_vertices_counts)
def test_same_point(point: Point, vertices_count: int) -> None:
    assert implication(vertices_count > 3,
                       self_intersects(list(repeat(point, vertices_count))))
