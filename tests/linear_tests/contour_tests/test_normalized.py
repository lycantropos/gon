from collections import Counter

from hypothesis import given

from gon.linear import Contour
from . import strategies


@given(strategies.contours)
def test_basic(contour: Contour) -> None:
    isinstance(contour.normalized, Contour)


@given(strategies.contours)
def test_sizes(contour: Contour) -> None:
    result = contour.normalized

    assert len(result.vertices) == len(contour.vertices)


@given(strategies.contours)
def test_elements(contour: Contour) -> None:
    result = contour.normalized

    assert Counter(result.vertices) == Counter(contour.vertices)
    assert result.vertices[0] == min(result.vertices)


@given(strategies.contours)
def test_orientation(contour: Contour) -> None:
    result = contour.normalized

    assert result.orientation is contour.orientation


@given(strategies.contours)
def test_idempotence(contour: Contour) -> None:
    result = contour.normalized

    assert result.normalized == result
