from hypothesis import given

from gon.shaped import (Contour,
                        RawContour)
from . import strategies


@given(strategies.contours)
def test_contour_round_trip(contour: Contour) -> None:
    assert Contour.from_raw(contour.raw()) == contour


@given(strategies.raw_contours)
def test_raw_contour_round_trip(raw_contour: RawContour) -> None:
    assert Contour.from_raw(raw_contour).raw() == raw_contour
