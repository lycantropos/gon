from functools import reduce
from itertools import combinations
from operator import or_

from hypothesis import given

from gon.compound import (Relation,
                          Shaped)
from gon.shaped import Polygon
from . import strategies


@given(strategies.shaped_geometries)
def test_basic(shaped: Shaped) -> None:
    result = shaped.triangulate()

    assert isinstance(result, list)
    assert all(isinstance(element, Polygon) for element in result)


@given(strategies.shaped_geometries)
def test_sizes(shaped: Shaped) -> None:
    result = shaped.triangulate()

    assert all(len(polygon.border.vertices) == 3 and not polygon.holes
               for polygon in result)


@given(strategies.shaped_geometries)
def test_relations(shaped: Shaped) -> None:
    result = shaped.triangulate()

    assert all(shaped.relate(triangle) in (Relation.EQUAL,
                                           Relation.COMPONENT,
                                           Relation.ENCLOSED)
               for triangle in result)
    assert all(triangle.relate(next_triangle) in (Relation.DISJOINT,
                                                  Relation.TOUCH)
               for triangle, next_triangle in combinations(result, 2))


@given(strategies.rational_shaped_geometries)
def test_area(shaped: Shaped) -> None:
    result = shaped.triangulate()

    assert sum(triangle.area for triangle in result) == shaped.area


@given(strategies.shaped_geometries)
def test_round_trip(shaped: Shaped) -> None:
    result = shaped.triangulate()

    assert reduce(or_, result).relate(shaped) is Relation.EQUAL
