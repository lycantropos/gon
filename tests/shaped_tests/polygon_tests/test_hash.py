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


@given(strategies.polygons_pairs)
def test_connection_with_equality(polygons_pair: Tuple[Polygon, Polygon]
                                  ) -> None:
    left_polygon, right_polygon = polygons_pair

    assert implication(left_polygon == right_polygon,
                       hash(left_polygon) == hash(right_polygon))


@given(strategies.polygons_with_contours_indices)
def test_contour_shift(polygon_with_contour_index: Tuple[Polygon, int]
                       ) -> None:
    polygon, index = polygon_with_contour_index

    shifted_polygon = to_polygon(polygon.contour[index:]
                                 + polygon.contour[:index])

    assert hash(polygon) == hash(shifted_polygon)
