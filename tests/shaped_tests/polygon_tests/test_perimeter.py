from hypothesis import given

from gon.base import Polygon
from tests.utils import equivalence
from . import strategies


@given(strategies.polygons)
def test_convexity(polygon: Polygon) -> None:
    result = polygon.perimeter

    is_polygon_convex = polygon.is_convex
    convex_hull_perimeter = polygon.convex_hull.perimeter
    assert equivalence(not is_polygon_convex, result > convex_hull_perimeter)
    assert equivalence(is_polygon_convex, result == convex_hull_perimeter)
