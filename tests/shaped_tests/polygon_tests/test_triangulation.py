from collections import abc

from hypothesis import given

from gon.shaped import (Polygon,
                        SimplePolygon)
from gon.shaped.utils import to_edges
from tests.utils import to_boundary
from . import strategies


@given(strategies.polygons)
def test_basic(polygon: Polygon) -> None:
    result = polygon.triangulation

    assert isinstance(result, abc.Sequence)
    assert all(isinstance(element, SimplePolygon)
               for element in result)


@given(strategies.polygons)
def test_sizes(polygon: Polygon) -> None:
    result = polygon.triangulation

    assert 0 < len(result) <= (2 * (len(polygon.contour) - 1)
                               - len(polygon.convex_hull.contour))
    assert all(len(element.contour) == 3
               for element in result)


@given(strategies.triangles)
def test_triangle(triangle: Polygon) -> None:
    result = triangle.triangulation

    assert len(result) == 1
    assert triangle in result


@given(strategies.polygons)
def test_boundary(polygon: Polygon) -> None:
    assert (to_boundary(triangle.contour
                        for triangle in polygon.triangulation)
            == set(to_edges(polygon.contour)))
