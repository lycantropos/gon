from typing import Tuple

from hypothesis import given

from gon.base import Point
from gon.shaped import (Polygon,
                        to_edges)
from tests import strategies
from tests.utils import implication


@given(strategies.polygons)
def test_vertices(polygon: Polygon) -> None:
    assert all(vertex in polygon
               for vertex in polygon.vertices)


@given(strategies.polygons_with_points)
def test_point_on_edge(polygon_with_point: Tuple[Polygon, Point]) -> None:
    polygon, point = polygon_with_point

    assert implication(any(point in edge
                           for edge in to_edges(polygon.vertices)),
                       point in polygon)
