from typing import (Any,
                    Tuple)

from hypothesis import given

from gon.shaped import (Polygon,
                        to_polygon)
from tests.utils import implication
from . import strategies


@given(strategies.polygons)
def test_reflexivity(polygon: Polygon) -> None:
    assert polygon == polygon


@given(strategies.polygons_pairs)
def test_symmetry(polygons_pair: Tuple[Polygon, Polygon]) -> None:
    left_polygon, right_polygon = polygons_pair

    assert implication(left_polygon == right_polygon,
                       right_polygon == left_polygon)


@given(strategies.polygons_triplets)
def test_transitivity(polygons_triplet: Tuple[Polygon, Polygon, Polygon]
                      ) -> None:
    left_polygon, mid_polygon, right_polygon = polygons_triplet

    assert implication(left_polygon == mid_polygon == right_polygon,
                       left_polygon == right_polygon)


@given(strategies.polygons_with_contours_indices)
def test_contour_shift(polygon_with_contour_index: Tuple[Polygon, int]
                       ) -> None:
    polygon, index = polygon_with_contour_index

    shifted_polygon = to_polygon(polygon.contour[index:]
                                 + polygon.contour[:index])

    assert polygon == shifted_polygon
