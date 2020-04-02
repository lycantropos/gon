from typing import Tuple

from hypothesis import given

from gon.point import Point
from gon.polygon import (PointLocation,
                         Polygon)
from tests.utils import implication
from . import strategies


@given(strategies.polygons)
def test_border_vertices(polygon: Polygon) -> None:
    assert all(polygon.locate(vertex) is PointLocation.BOUNDARY
               for vertex in polygon.border.vertices)


@given(strategies.polygons)
def test_holes_vertices(polygon: Polygon) -> None:
    assert all(polygon.locate(vertex) is PointLocation.BOUNDARY
               for vertex in polygon.border.vertices)


@given(strategies.polygons_with_points)
def test_convex_hull(polygon_with_point: Tuple[Polygon, Point]) -> None:
    polygon, point = polygon_with_point

    assert implication(polygon.locate(point) is PointLocation.INTERNAL,
                       polygon.convex_hull.locate(point)
                       is PointLocation.INTERNAL)
    assert implication(polygon.is_convex
                       and polygon.locate(point) is PointLocation.BOUNDARY,
                       polygon.convex_hull.locate(point)
                       is PointLocation.BOUNDARY)
