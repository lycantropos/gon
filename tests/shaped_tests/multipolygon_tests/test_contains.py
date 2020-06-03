from typing import Tuple

from hypothesis import given

from gon.primitive import Point
from gon.shaped import Multipolygon
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.multipolygons)
def test_border_vertices(multipolygon: Multipolygon) -> None:
    assert all(vertex in multipolygon
               for vertex in multipolygon.border.vertices)


@given(strategies.multipolygons)
def test_holes_vertices(multipolygon: Multipolygon) -> None:
    assert all(vertex in multipolygon
               for hole in multipolygon.holes
               for vertex in hole.vertices)


@given(strategies.multipolygons_with_points)
def test_convex_hull(multipolygon_with_point: Tuple[Multipolygon, Point]) -> None:
    multipolygon, point = multipolygon_with_point

    assert implication(point in multipolygon, point in multipolygon.convex_hull)


@given(strategies.multipolygons_with_points)
def test_indexing(multipolygon_with_point: Tuple[Multipolygon, Point]) -> None:
    multipolygon, point = multipolygon_with_point

    before_indexing = point in multipolygon

    multipolygon.index()

    after_indexing = point in multipolygon

    assert equivalence(before_indexing, after_indexing)
