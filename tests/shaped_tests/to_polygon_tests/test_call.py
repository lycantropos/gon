import pytest
from hypothesis import given

from gon.shaped import to_polygon
from gon.shaped.hints import Contour
from . import strategies


@given(strategies.invalid_contours)
def test_invalid_contour(contour: Contour) -> None:
    with pytest.raises(ValueError):
        to_polygon(contour)
