from collections import Counter

from hypothesis import given

from gon.angular import Orientation
from gon.polygon import Polygon
from . import strategies


@given(strategies.polygons)
def test_basic(polygon: Polygon) -> None:
    isinstance(polygon.normalized, Polygon)


@given(strategies.polygons)
def test_sizes(polygon: Polygon) -> None:
    result = polygon.normalized

    assert len(result.border.vertices) == len(polygon.border.vertices)
    assert len(result.holes) == len(polygon.holes)
    assert (Counter(len(hole.vertices) for hole in result.holes)
            == Counter(len(hole.vertices) for hole in polygon.holes))


@given(strategies.polygons)
def test_elements(polygon: Polygon) -> None:
    result = polygon.normalized

    assert Counter(result.border.vertices) == Counter(polygon.border.vertices)
    assert (Counter(frozenset(Counter(hole.vertices).items())
                    for hole in result.holes)
            == Counter(frozenset(Counter(hole.vertices).items())
                       for hole in polygon.holes))
    assert result.border.vertices[0] == min(result.border.vertices)
    assert all(hole.vertices[0] == min(hole.vertices)
               for hole in result.holes)


@given(strategies.polygons)
def test_orientations(polygon: Polygon) -> None:
    result = polygon.normalized

    assert result.border.orientation is Orientation.COUNTERCLOCKWISE
    assert all(hole.orientation is Orientation.CLOCKWISE
               for hole in result.holes)


@given(strategies.polygons)
def test_idempotence(polygon: Polygon) -> None:
    result = polygon.normalized

    assert result.normalized == result
