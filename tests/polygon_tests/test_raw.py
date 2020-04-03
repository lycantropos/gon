from hypothesis import given

from gon.polygon import (Polygon,
                         RawPolygon)
from . import strategies


@given(strategies.polygons)
def test_polygon_round_trip(polygon: Polygon) -> None:
    assert Polygon.from_raw(polygon.raw()) == polygon


@given(strategies.raw_polygons)
def test_raw_polygon_round_trip(raw_polygon: RawPolygon) -> None:
    assert Polygon.from_raw(raw_polygon).raw() == raw_polygon
