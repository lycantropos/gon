from hypothesis import given

from gon.shaped import Polygon
from . import strategies


@given(strategies.polygons)
def test_convex_hull(polygon: Polygon) -> None:
    assert polygon.perimeter >= polygon.convex_hull.perimeter
