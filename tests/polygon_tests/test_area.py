import math
from hypothesis import given

from gon.hints import Coordinate
from gon.polygon import Polygon
from . import strategies


@given(strategies.polygons)
def test_basic(polygon: Polygon) -> None:
    assert isinstance(polygon.area, Coordinate)


@given(strategies.polygons)
def test_properties(polygon: Polygon) -> None:
    result = polygon.area

    assert math.isfinite(result)
    assert result > 0


@given(strategies.polygons)
def test_convex_hull(polygon: Polygon) -> None:
    assert polygon.area <= polygon.convex_hull.area
