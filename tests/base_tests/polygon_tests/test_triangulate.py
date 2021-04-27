from hypothesis import given

from gon.base import (Polygon,
                      Triangulation)
from . import strategies


@given(strategies.polygons)
def test_basic(polygon: Polygon) -> None:
    result = polygon.triangulate()

    assert isinstance(result, Triangulation)
