from typing import Tuple

from hypothesis import given

from gon.base import Contour
from tests.utils import (implication,
                         shift_contour)
from . import strategies


@given(strategies.contours)
def test_reflexivity(contour: Contour) -> None:
    assert contour == contour


@given(strategies.contours_pairs)
def test_symmetry(contours_pair: Tuple[Contour, Contour]) -> None:
    first, second = contours_pair

    assert implication(first == second, second == first)


@given(strategies.contours_triplets)
def test_transitivity(contours_triplet: Tuple[Contour, Contour, Contour]
                      ) -> None:
    first, second, third = contours_triplet

    assert implication(first == second == third,
                       first == third)


@given(strategies.contours)
def test_reversals(contour: Contour) -> None:
    assert contour == contour.reverse()


@given(strategies.contours)
def test_shifts(contour: Contour) -> None:
    assert all(contour == shift_contour(contour, step)
               for step in range(1, len(contour.vertices)))
