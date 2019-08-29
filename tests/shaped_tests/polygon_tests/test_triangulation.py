from collections import abc
from typing import (Iterable,
                    Set)

from hypothesis import given

from gon.linear import Segment
from gon.shaped import (Polygon,
                        SimplePolygon)
from gon.shaped.hints import Vertices
from gon.shaped.utils import to_edges
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

    assert 0 < len(result) <= (2 * (len(polygon.vertices) - 1)
                               - len(polygon.convex_hull.vertices))
    assert all(len(element.vertices) == 3
               for element in result)


@given(strategies.triangles)
def test_triangle(triangle: Polygon) -> None:
    result = triangle.triangulation

    assert len(result) == 1
    assert triangle in result


@given(strategies.polygons)
def test_boundary(polygon: Polygon) -> None:
    assert (to_boundary(triangle.vertices
                        for triangle in polygon.triangulation)
            == set(to_edges(polygon.vertices)))


def to_boundary(polygons_vertices: Iterable[Vertices]) -> Set[Segment]:
    result = set()
    for vertices in polygons_vertices:
        result.symmetric_difference_update(to_edges(vertices))
    return result
