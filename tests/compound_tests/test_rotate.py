from typing import Tuple

from hypothesis import given

from gon.compound import Compound
from gon.hints import Coordinate
from . import strategies


@given(strategies.rational_non_empty_compounds_with_cosines_sines)
def test_centroid(compound_with_cosine_sine
                  : Tuple[Compound, Tuple[Coordinate, Coordinate]]) -> None:
    compound, (cosine, sine) = compound_with_cosine_sine

    result = compound.rotate(cosine, sine, compound.centroid)

    assert result.centroid == compound.centroid
