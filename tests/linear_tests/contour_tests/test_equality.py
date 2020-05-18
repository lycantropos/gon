from typing import Tuple

from hypothesis import given

from gon.linear import Contour
from tests.utils import (implication,
                         rotate_contour,
                         shift_contour)
from . import strategies


@given(strategies.contours)
def test_reflexivity(contour: Contour) -> None:
    assert contour == contour


@given(strategies.contours_pairs)
def test_symmetry(contours_pair: Tuple[Contour, Contour]) -> None:
    left_contour, right_contour = contours_pair

    assert implication(left_contour == right_contour,
                       right_contour == left_contour)


@given(strategies.contours_triplets)
def test_transitivity(contours_triplet: Tuple[Contour, Contour, Contour]
                      ) -> None:
    left_contour, mid_contour, right_contour = contours_triplet

    assert implication(left_contour == mid_contour == right_contour,
                       left_contour == right_contour)


@given(strategies.contours)
def test_rotated(contour: Contour) -> None:
    assert contour == rotate_contour(contour)


@given(strategies.contours)
def test_shifted(contour: Contour) -> None:
    assert all(contour == shift_contour(contour, step)
               for step in range(len(contour.vertices)))
