from typing import Tuple

from hypothesis import given

from gon.shaped import Multipolygon
from tests.utils import implication
from . import strategies


@given(strategies.multipolygons)
def test_reflexivity(multipolygon: Multipolygon) -> None:
    assert multipolygon == multipolygon


@given(strategies.multipolygons_pairs)
def test_symmetry(multipolygons_pair: Tuple[Multipolygon, Multipolygon]
                  ) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    assert implication(left_multipolygon == right_multipolygon,
                       right_multipolygon == left_multipolygon)


@given(strategies.multipolygons_triplets)
def test_transitivity(multipolygons_triplet: Tuple[Multipolygon, Multipolygon,
                                                   Multipolygon]) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    assert implication(left_multipolygon == mid_multipolygon
                       == right_multipolygon,
                       left_multipolygon == right_multipolygon)
