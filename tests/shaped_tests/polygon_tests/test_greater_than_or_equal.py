from hypothesis import given

from gon.shaped import Polygon
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.polygons)
def test_reflexivity(polygon: Polygon) -> None:
    assert polygon >= polygon


@given(strategies.polygons, strategies.polygons)
def test_antisymmetry(left_polygon: Polygon, right_polygon: Polygon) -> None:
    assert implication(left_polygon >= right_polygon >= left_polygon,
                       left_polygon == right_polygon)


@given(strategies.polygons, strategies.polygons, strategies.polygons)
def test_transitivity(left_polygon: Polygon,
                      mid_polygon: Polygon,
                      right_polygon: Polygon) -> None:
    assert implication(left_polygon >= mid_polygon >= right_polygon,
                       left_polygon >= right_polygon)


@given(strategies.polygons, strategies.polygons)
def test_relation_with_issuperset(left_polygon: Polygon,
                                  right_polygon: Polygon) -> None:
    assert equivalence(left_polygon >= right_polygon,
                       left_polygon.issuperset(right_polygon))
