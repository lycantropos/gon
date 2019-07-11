from hypothesis import given

from gon.shaped import Polygon
from tests import strategies


@given(strategies.triangles)
def test_triangle(triangle: Polygon) -> None:
    assert triangle.is_convex
