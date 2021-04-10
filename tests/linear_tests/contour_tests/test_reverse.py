from collections import Counter

from hypothesis import given

from gon.base import Contour
from . import strategies


@given(strategies.contours)
def test_basic(contour: Contour) -> None:
    isinstance(contour.reverse(), Contour)


@given(strategies.contours)
def test_sizes(contour: Contour) -> None:
    result = contour.reverse()

    assert len(result.vertices) == len(contour.vertices)


@given(strategies.contours)
def test_elements(contour: Contour) -> None:
    result = contour.reverse()

    assert Counter(result.vertices) == Counter(contour.vertices)
    assert result.vertices[0] == result.vertices[0]


@given(strategies.contours)
def test_orientation(contour: Contour) -> None:
    result = contour.reverse()

    assert result.orientation is not contour.orientation


@given(strategies.contours)
def test_involution(contour: Contour) -> None:
    result = contour.reverse()

    assert result.reverse() == contour
