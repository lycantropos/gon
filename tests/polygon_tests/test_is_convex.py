from hypothesis import given

from gon.polygon import Polygon
from tests.utils import equivalence
from . import strategies


@given(strategies.triangles)
def test_triangle(triangle: Polygon) -> None:
    assert triangle.is_convex


@given(strategies.polygons)
def test_relation_with_convex_hull(polygon: Polygon) -> None:
    assert equivalence(polygon.is_convex,
                       polygon.normalized == polygon.convex_hull.normalized)