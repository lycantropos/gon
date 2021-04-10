from typing import Tuple

from hypothesis import given

from gon.base import Geometry
from gon.hints import Coordinate
from . import strategies


@given(strategies.geometries_with_coordinates_pairs)
def test_basic(geometry_with_steps: Tuple[Geometry, Coordinate, Coordinate]
               ) -> None:
    geometry, step_x, step_y = geometry_with_steps

    result = geometry.translate(step_x, step_y)

    assert isinstance(result, type(geometry))


@given(strategies.geometries)
def test_neutral_step(geometry: Geometry) -> None:
    result = geometry.translate(0, 0)

    assert result == geometry


@given(strategies.empty_compounds_with_coordinates_pairs)
def test_empty(geometry_with_steps: Tuple[Geometry, Coordinate, Coordinate]
               ) -> None:
    geometry, step_x, step_y = geometry_with_steps

    result = geometry.translate(step_x, step_y)

    assert result == geometry
