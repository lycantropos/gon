from typing import Tuple

from hypothesis import given

from gon.compound import Compound
from gon.geometry import Geometry
from gon.hints import Coordinate
from tests.utils import (equivalence,
                         robust_invert)
from . import strategies


@given(strategies.geometries_with_coordinates_pairs)
def test_basic(geometry_with_factors: Tuple[Geometry, Coordinate, Coordinate]
               ) -> None:
    geometry, factor_x, factor_y = geometry_with_factors

    result = geometry.scale(factor_x, factor_y)

    assert isinstance(result, Geometry)
    assert equivalence(isinstance(result, Compound),
                       isinstance(geometry, Compound))


@given(strategies.rational_geometries_with_non_zero_coordinates_pairs)
def test_round_trip(geometry_with_non_zero_factors: Tuple[Geometry, Coordinate,
                                                          Coordinate]) -> None:
    geometry, factor_x, factor_y = geometry_with_non_zero_factors

    result = geometry.scale(factor_x, factor_y)

    assert (result.scale(robust_invert(factor_x), robust_invert(factor_y))
            == geometry)


@given(strategies.geometries)
def test_neutral_factor(geometry: Geometry) -> None:
    result = geometry.scale(1)

    assert result == geometry


@given(strategies.empty_compounds_with_coordinates_pairs)
def test_empty(geometry_with_factors: Tuple[Geometry, Coordinate, Coordinate]
               ) -> None:
    geometry, factor_x, factor_y = geometry_with_factors

    result = geometry.scale(factor_x, factor_y)

    assert result == geometry
