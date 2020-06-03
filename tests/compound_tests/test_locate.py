from typing import Tuple

from hypothesis import given

from gon.compound import (Compound,
                          Location)
from gon.primitive import Point
from . import strategies


@given(strategies.compounds_with_points)
def test_basic(compound_with_point: Tuple[Compound, Point]) -> None:
    compound, point = compound_with_point

    result = compound.locate(point)

    assert isinstance(result, Location)
