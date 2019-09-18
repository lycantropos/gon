from typing import Tuple

from hypothesis import given

from gon.shaped import (Polygon,
                        to_polygon)
from tests.utils import implication
from . import strategies


@given(strategies.polygons)
def test_basic(polygon: Polygon) -> None:
    result = hash(polygon)

    assert isinstance(result, int)


@given(strategies.polygons)
def test_determinism(polygon: Polygon) -> None:
    result = hash(polygon)

    assert result == hash(polygon)


@given(strategies.polygons, strategies.polygons)
def test_connection_with_equality(left_polygon: Polygon,
                                  right_polygon: Polygon) -> None:
    assert implication(left_polygon == right_polygon,
                       hash(left_polygon) == hash(right_polygon))


@given(strategies.polygons_with_vertices_indices)
def test_vertices_shift(polygon_with_vertices_index: Tuple[Polygon, int]
                        ) -> None:
    polygon, index = polygon_with_vertices_index

    shifted_polygon = to_polygon(polygon.vertices[index:]
                                 + polygon.vertices[:index])

    assert hash(polygon) == hash(shifted_polygon)
