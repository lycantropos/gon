from hypothesis import given

from gon.shaped import Polygon
from tests import strategies
from tests.utils import equivalence


@given(strategies.polygons)
def test_basic(polygon: Polygon) -> None:
    result = hash(polygon)

    assert isinstance(result, int)


@given(strategies.polygons)
def test_determinism(polygon: Polygon) -> None:
    result = hash(polygon)

    assert result == hash(polygon)


@given(strategies.polygons, strategies.polygons)
def test_connection_with_equality(left_polygon: Polygon,
                                  right_polygon: Polygon) -> None:
    assert equivalence(left_polygon == right_polygon,
                       hash(left_polygon) == hash(right_polygon))
