from typing import Tuple

from hypothesis import given

from gon.shaped import Polygon
from tests.utils import implication
from . import strategies


@given(strategies.polygons)
def test_irreflexivity(polygon: Polygon) -> None:
    assert not polygon < polygon


@given(strategies.polygons_pairs)
def test_asymmetry(polygons_pair: Tuple[Polygon, Polygon]) -> None:
    first_polygon, second_polygon = polygons_pair

    assert implication(first_polygon < second_polygon,
                       not second_polygon < first_polygon)


@given(strategies.polygons_triplets)
def test_transitivity(polygons_triplet: Tuple[Polygon, Polygon, Polygon]
                      ) -> None:
    first_polygon, second_polygon, third_polygon = polygons_triplet

    assert implication(first_polygon < second_polygon < third_polygon,
                       first_polygon < third_polygon)
