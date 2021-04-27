from functools import reduce
from operator import or_

from hypothesis import given

from gon.base import (Polygon,
                      Triangulation)
from . import strategies


@given(strategies.polygons)
def test_basic(polygon: Polygon) -> None:
    result = polygon.triangulate()

    assert isinstance(result, Triangulation)


@given(strategies.polygons)
def test_round_trip(polygon: Polygon) -> None:
    result = polygon.triangulate()

    assert (reduce(or_, [Polygon(contour) for contour in result.triangles()])
            == polygon)
