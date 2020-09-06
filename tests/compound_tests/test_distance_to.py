from typing import Tuple

from hypothesis import given

from gon.compound import (Compound,
                          Indexable)
from gon.geometry import Geometry
from gon.primitive import Point
from tests.utils import equivalence
from . import strategies


@given(strategies.non_empty_compounds_with_points)
def test_connection_with_contains(compound_with_point: Tuple[Compound, Point]
                                  ) -> None:
    compound, point = compound_with_point

    result = compound.distance_to(point)

    assert equivalence(not result, point in compound)


@given(strategies.non_empty_compounds_pairs)
def test_connection_with_disjoint(compounds_pair: Tuple[Compound, Compound]
                                  ) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound.distance_to(right_compound)

    assert equivalence(bool(result), left_compound.disjoint(right_compound))


@given(strategies.indexables_with_non_empty_geometries)
def test_indexing(indexable_with_geometry: Tuple[Indexable, Geometry]) -> None:
    indexable, geometry = indexable_with_geometry

    before_indexing = indexable.distance_to(geometry)

    indexable.index()

    after_indexing = indexable.distance_to(geometry)

    assert before_indexing == after_indexing
