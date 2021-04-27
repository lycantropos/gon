from typing import Tuple

from hypothesis import given

from gon.base import (Multipolygon,
                      Point)
from tests.utils import equivalence
from . import strategies


@given(strategies.multipolygons)
def test_vertices(multipolygon: Multipolygon) -> None:
    assert all(vertex in multipolygon
               for polygon in multipolygon.polygons
               for vertex in polygon.border.vertices)
    assert all(vertex in multipolygon
               for polygon in multipolygon.polygons
               for hole in polygon.holes
               for vertex in hole.vertices)


@given(strategies.multipolygons_with_points)
def test_indexing(multipolygon_with_point: Tuple[Multipolygon, Point]) -> None:
    multipolygon, point = multipolygon_with_point

    before_indexing = point in multipolygon

    multipolygon.index()

    after_indexing = point in multipolygon

    assert equivalence(before_indexing, after_indexing)
