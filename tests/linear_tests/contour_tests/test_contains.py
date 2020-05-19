from typing import Tuple

from hypothesis import given

from gon.linear import Contour
from gon.primitive import Point
from tests.utils import equivalence
from . import strategies


@given(strategies.contours)
def test_vertices(contour: Contour) -> None:
    assert all(vertex in contour
               for vertex in contour.vertices)


@given(strategies.contours_with_points)
def test_indexing(contour_with_point: Tuple[Contour, Point]) -> None:
    contour, point = contour_with_point

    before_indexing = point in contour

    contour.index()

    after_indexing = point in contour

    assert equivalence(before_indexing, after_indexing)
