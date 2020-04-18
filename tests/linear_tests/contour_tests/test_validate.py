import pytest
from hypothesis import given

from gon.linear import Contour
from . import strategies


@given(strategies.contours)
def test_basic(contour: Contour) -> None:
    result = contour.validate()

    assert result is None


@given(strategies.invalid_contours)
def test_invalid_contour(contour: Contour) -> None:
    with pytest.raises(ValueError):
        contour.validate()
