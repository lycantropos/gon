from typing import Tuple

from hypothesis import given

from gon.base import Point
from gon.shaped.base import (Polygon,
                             to_edges)
from tests.utils import implication
from . import strategies


@given(strategies.polygons)
def test_contour(polygon: Polygon) -> None:
    assert all(vertex in polygon
               for vertex in polygon.contour)


@given(strategies.polygons_with_points)
def test_point_on_edge(polygon_with_point: Tuple[Polygon, Point]) -> None:
    polygon, point = polygon_with_point

    assert implication(any(point in edge
                           for edge in to_edges(polygon.contour)),
                       point in polygon)


@given(strategies.polygons_with_points)
def test_convex_hull(polygon_with_point: Tuple[Polygon, Point]) -> None:
    polygon, point = polygon_with_point

    assert implication(point in polygon, point in polygon.convex_hull)
