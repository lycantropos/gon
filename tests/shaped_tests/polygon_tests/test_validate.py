import pytest
from hypothesis import given

from gon.shaped import Polygon
from . import strategies


@given(strategies.polygons)
def test_basic(polygon: Polygon) -> None:
    result = polygon.validate()

    assert result is None


@given(strategies.invalid_polygons)
def test_invalid_polygon(polygon: Polygon) -> None:
    with pytest.raises(ValueError):
        polygon.validate()
