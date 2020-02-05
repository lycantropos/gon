from hypothesis import given

from gon.shaped.contracts import self_intersects
from gon.shaped.hints import Contour
from tests import strategies


@given(strategies.triangular_contours)
def test_triangle_contour(contour: Contour) -> None:
    assert not self_intersects(contour)
