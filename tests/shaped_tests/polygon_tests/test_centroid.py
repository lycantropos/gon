from hypothesis import given

from gon.shaped import Polygon
from tests.utils import implication
from . import strategies


@given(strategies.polygons)
def test_connection_with_contains(polygon: Polygon) -> None:
    assert implication(polygon.is_convex, polygon.centroid in polygon)
