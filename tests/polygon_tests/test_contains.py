from typing import Tuple

from hypothesis import given

from gon.point import Point
from gon.polygon import Polygon
from tests.utils import implication
from . import strategies


@given(strategies.polygons)
def test_border_vertices(polygon: Polygon) -> None:
    assert all(vertex in polygon
               for vertex in polygon.border.vertices)


@given(strategies.polygons)
def test_holes_vertices(polygon: Polygon) -> None:
    assert all(vertex in polygon
               for hole in polygon.holes
               for vertex in hole.vertices)


@given(strategies.polygons_with_points)
def test_convex_hull(polygon_with_point: Tuple[Polygon, Point]) -> None:
    polygon, point = polygon_with_point

    assert implication(point in polygon, point in polygon.convex_hull)
