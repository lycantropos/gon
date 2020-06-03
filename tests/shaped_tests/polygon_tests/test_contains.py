from typing import Tuple

from hypothesis import given

from gon.primitive import Point
from gon.shaped import Polygon
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.polygons)
def test_vertices(polygon: Polygon) -> None:
    assert all(vertex in polygon
               for vertex in polygon.border.vertices)
    assert all(vertex in polygon
               for hole in polygon.holes
               for vertex in hole.vertices)


@given(strategies.polygons_with_points)
def test_convex_hull(polygon_with_point: Tuple[Polygon, Point]) -> None:
    polygon, point = polygon_with_point

    assert implication(point in polygon, point in polygon.convex_hull)


@given(strategies.polygons_with_points)
def test_indexing(polygon_with_point: Tuple[Polygon, Point]) -> None:
    polygon, point = polygon_with_point

    before_indexing = point in polygon

    polygon.index()

    after_indexing = point in polygon

    assert equivalence(before_indexing, after_indexing)
