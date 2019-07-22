from typing import Tuple

from hypothesis import given

from gon.shaped import (Polygon,
                        to_polygon)
from tests.utils import implication
from . import strategies


@given(strategies.polygons)
def test_reflexivity(polygon: Polygon) -> None:
    assert polygon == polygon


@given(strategies.polygons, strategies.polygons)
def test_symmetry(left_polygon: Polygon, right_polygon: Polygon) -> None:
    assert implication(left_polygon == right_polygon,
                       right_polygon == left_polygon)


@given(strategies.polygons, strategies.polygons, strategies.polygons)
def test_transitivity(left_polygon: Polygon,
                      mid_polygon: Polygon,
                      right_polygon: Polygon) -> None:
    assert implication(left_polygon == mid_polygon
                       and mid_polygon == right_polygon,
                       left_polygon == right_polygon)


@given(strategies.polygons_with_vertices_indices)
def test_vertices_shift(polygon_with_vertices_index: Tuple[Polygon, int]
                        ) -> None:
    polygon, index = polygon_with_vertices_index

    shifted_polygon = to_polygon(polygon.vertices[index:]
                                 + polygon.vertices[:index])

    assert polygon == shifted_polygon
