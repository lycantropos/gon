from typing import Tuple

from hypothesis import given

from gon.base import Angle, Compound
from . import strategies


@given(strategies.non_empty_compounds_with_angles)
def test_centroid(compound_with_angle: Tuple[Compound, Angle]) -> None:
    compound, angle = compound_with_angle

    result = compound.rotate(angle, compound.centroid)

    assert result.centroid == compound.centroid
