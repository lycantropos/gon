from typing import Tuple

from hypothesis import given

from gon.geometry import Geometry
from gon.hints import Coordinate
from . import strategies


@given(strategies.non_empty_geometries_pairs)
def test_basic(geometries_pair: Tuple[Geometry, Geometry]) -> None:
    left_geometry, right_geometry = geometries_pair

    result = left_geometry.distance_to(right_geometry)

    assert isinstance(result, Coordinate)


@given(strategies.non_empty_geometries_pairs)
def test_commutativity(geometries_pair: Tuple[Geometry, Geometry]) -> None:
    left_geometry, right_geometry = geometries_pair

    result = left_geometry.distance_to(right_geometry)

    assert result == right_geometry.distance_to(left_geometry)


@given(strategies.non_empty_geometries_pairs)
def test_non_negativeness(geometries_pair: Tuple[Geometry, Geometry]) -> None:
    left_geometry, right_geometry = geometries_pair

    result = left_geometry.distance_to(right_geometry)

    assert result >= 0
