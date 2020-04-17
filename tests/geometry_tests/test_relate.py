from typing import Tuple

from hypothesis import given
from orient.planar import Relation

from gon.geometry import Geometry
from . import strategies


@given(strategies.geometries_pairs)
def test_basic(geometries_pair: Tuple[Geometry, Geometry]) -> None:
    left_geometry, right_geometry = geometries_pair

    result = left_geometry.relate(right_geometry)

    assert isinstance(result, Relation)


@given(strategies.geometries)
def test_self(geometry: Geometry) -> None:
    assert geometry.relate(geometry) is Relation.EQUAL


@given(strategies.geometries_pairs)
def test_complement(geometries_pair: Tuple[Geometry, Geometry]) -> None:
    left_geometry, right_geometry = geometries_pair

    result = left_geometry.relate(right_geometry)

    assert result.complement is right_geometry.relate(left_geometry)
