import math
from typing import Tuple

import pytest
from hypothesis import given

from gon.base import (Compound,
                      Geometry)
from tests.utils import is_scalar
from . import strategies


@given(strategies.non_empty_geometries_pairs)
def test_basic(geometries_pair: Tuple[Geometry, Geometry]) -> None:
    left_geometry, right_geometry = geometries_pair

    result = left_geometry.distance_to(right_geometry)

    assert is_scalar(result)


@given(strategies.non_empty_geometries_pairs)
def test_commutativity(geometries_pair: Tuple[Geometry, Geometry]) -> None:
    left_geometry, right_geometry = geometries_pair

    result = left_geometry.distance_to(right_geometry)

    assert result == right_geometry.distance_to(left_geometry)


@given(strategies.non_empty_geometries_pairs)
def test_value(geometries_pair: Tuple[Geometry, Geometry]) -> None:
    left_geometry, right_geometry = geometries_pair

    result = left_geometry.distance_to(right_geometry)

    assert 0 <= result < math.inf


@given(strategies.empty_compounds, strategies.geometries)
def test_empty(compound: Compound, geometry: Geometry) -> None:
    with pytest.raises(ValueError):
        compound.distance_to(geometry)
