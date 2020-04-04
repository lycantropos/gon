from hypothesis import given

from gon.shaped import Polygon
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.polygons)
def test_basic(polygon: Polygon) -> None:
    assert isinstance(polygon.is_convex, bool)


@given(strategies.polygons)
def test_base_case(polygon: Polygon) -> None:
    assert implication(len(polygon.border.vertices) == 3
                       and not polygon.holes,
                       polygon.is_convex)


@given(strategies.polygons)
def test_relation_with_convex_hull(polygon: Polygon) -> None:
    assert equivalence(polygon.is_convex,
                       polygon.normalized == polygon.convex_hull.normalized)
