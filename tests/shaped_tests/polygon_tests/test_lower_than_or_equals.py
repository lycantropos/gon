from typing import Tuple

from hypothesis import given

from gon.shaped import Polygon
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.polygons)
def test_reflexivity(polygon: Polygon) -> None:
    assert polygon <= polygon


@given(strategies.polygons_pairs)
def test_antisymmetry(polygons_pair: Tuple[Polygon, Polygon]) -> None:
    first_polygon, second_polygon = polygons_pair

    assert equivalence(first_polygon <= second_polygon <= first_polygon,
                       first_polygon == second_polygon)


@given(strategies.polygons_triplets)
def test_transitivity(polygons_triplet: Tuple[Polygon, Polygon, Polygon]
                      ) -> None:
    first_polygon, second_polygon, third_polygon = polygons_triplet

    assert implication(first_polygon <= second_polygon <= third_polygon,
                       first_polygon <= third_polygon)


@given(strategies.polygons_pairs)
def test_connection_with_lower_than(polygons_pair: Tuple[Polygon, Polygon]
                                    ) -> None:
    first_polygon, second_polygon = polygons_pair

    assert implication(first_polygon < second_polygon,
                       first_polygon <= second_polygon)


@given(strategies.polygons_pairs)
def test_connection_with_greater_than_or_equals(
        polygons_pair: Tuple[Polygon, Polygon]) -> None:
    first_polygon, second_polygon = polygons_pair

    assert equivalence(first_polygon <= second_polygon,
                       second_polygon >= first_polygon)
