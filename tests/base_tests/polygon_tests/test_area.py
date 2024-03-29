from hypothesis import given

from gon.base import Polygon
from . import strategies


@given(strategies.polygons)
def test_convex_hull(polygon: Polygon) -> None:
    assert polygon.area <= polygon.convex_hull.area
