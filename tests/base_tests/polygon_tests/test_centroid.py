from hypothesis import given

from gon.base import Polygon
from tests.utils import implication
from . import strategies


@given(strategies.rational_polygons)
def test_connection_with_contains(polygon: Polygon) -> None:
    assert implication(polygon.is_convex, polygon.centroid in polygon)
