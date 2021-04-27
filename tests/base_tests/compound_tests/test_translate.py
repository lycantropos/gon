from typing import Tuple

from hypothesis import given

from gon.base import Compound
from gon.hints import Coordinate
from . import strategies


@given(strategies.rational_non_empty_compounds_with_coordinates_pairs)
def test_centroid(compound_with_steps: Tuple[Compound, Coordinate, Coordinate]
                  ) -> None:
    compound, step_x, step_y = compound_with_steps

    result = compound.translate(step_x, step_y)

    assert result.centroid == compound.centroid.translate(step_x, step_y)
