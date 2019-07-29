from collections import abc

from hypothesis import given

from gon.shaped import (Polygon,
                        SimplePolygon)
from gon.shaped.triangulation import _to_boundary
from gon.shaped.utils import to_edges
from . import strategies


@given(strategies.polygons)
def test_basic(polygon: Polygon) -> None:
    result = polygon.triangulation

    assert isinstance(result, abc.Sequence)
    assert 0 < len(result) <= (2 * (len(polygon.vertices) - 1)
                               - len(polygon.convex_hull.vertices))
    assert all(isinstance(element, SimplePolygon)
               for element in result)
    assert all(len(element.vertices) == 3
               for element in result)


@given(strategies.triangles)
def test_triangle(triangle: Polygon) -> None:
    result = triangle.triangulation

    assert len(result) == 1
    assert triangle in result


@given(strategies.polygons)
def test_boundary(polygon: Polygon) -> None:
    triangles_vertices = [triangle.vertices
                          for triangle in polygon.triangulation]

    assert _to_boundary(triangles_vertices) == set(to_edges(polygon.vertices))
