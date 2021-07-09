from typing import Tuple

from hypothesis import given

from gon.base import Polygon
from tests.utils import implication
from . import strategies


@given(strategies.polygons)
def test_reflexivity(polygon: Polygon) -> None:
    assert polygon == polygon


@given(strategies.polygons_pairs)
def test_symmetry(polygons_pair: Tuple[Polygon, Polygon]) -> None:
    first, second = polygons_pair

    assert implication(first == second, second == first)


@given(strategies.polygons_triplets)
def test_transitivity(polygons_triplet: Tuple[Polygon, Polygon, Polygon]
                      ) -> None:
    first, second, third = polygons_triplet

    assert implication(first == second == third, first == third)
