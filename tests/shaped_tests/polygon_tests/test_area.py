from hypothesis import given

from gon.shaped import Polygon
from tests import strategies


@given(strategies.polygons)
def test_basic(polygon: Polygon) -> None:
    assert polygon.area > 0


@given(strategies.polygons)
def test_convex_hull(polygon: Polygon) -> None:
    assert polygon.area <= polygon.convex_hull.area
