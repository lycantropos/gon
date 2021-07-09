from typing import Tuple

from hypothesis import given

from gon.base import Multipolygon
from tests.utils import implication
from . import strategies


@given(strategies.multipolygons)
def test_reflexivity(multipolygon: Multipolygon) -> None:
    assert multipolygon == multipolygon


@given(strategies.multipolygons_pairs)
def test_symmetry(multipolygons_pair: Tuple[Multipolygon, Multipolygon]
                  ) -> None:
    first, second = multipolygons_pair

    assert implication(first == second, second == first)


@given(strategies.multipolygons_triplets)
def test_transitivity(multipolygons_triplet
                      : Tuple[Multipolygon, Multipolygon, Multipolygon]
                      ) -> None:
    first, second, third = multipolygons_triplet

    assert implication(first == second == third, first == third)
