from typing import Tuple

from hypothesis import given

from gon.geometry import Geometry
from tests.utils import equivalence
from . import strategies


@given(strategies.geometries_pairs)
def test_basic(geometries_pair: Tuple[Geometry, Geometry]) -> None:
    left_geometry, right_geometry = geometries_pair

    result = left_geometry.disjoint(right_geometry)

    assert isinstance(result, bool)


@given(strategies.geometries)
def test_irreflexivity(geometry: Geometry) -> None:
    assert not geometry.disjoint(geometry)


@given(strategies.geometries_pairs)
def test_symmetry(geometries_pair: Tuple[Geometry, Geometry]) -> None:
    left_geometry, right_geometry = geometries_pair

    assert equivalence(left_geometry.disjoint(right_geometry),
                       right_geometry.disjoint(left_geometry))
