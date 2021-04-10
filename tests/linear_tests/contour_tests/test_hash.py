from typing import Tuple

from hypothesis import given

from gon.base import Contour
from tests.utils import implication
from . import strategies


@given(strategies.contours)
def test_determinism(contour: Contour) -> None:
    result = hash(contour)

    assert result == hash(contour)


@given(strategies.contours_pairs)
def test_connection_with_equality(contours_pair: Tuple[Contour, Contour]
                                  ) -> None:
    left_contour, right_contour = contours_pair

    assert implication(left_contour == right_contour,
                       hash(left_contour) == hash(right_contour))
