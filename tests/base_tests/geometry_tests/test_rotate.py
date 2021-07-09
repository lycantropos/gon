from typing import Tuple

from hypothesis import given

from gon.base import (Angle,
                      Geometry,
                      Point)
from . import strategies


@given(strategies.geometries_points_with_angles)
def test_basic(geometry_point_with_angle: Tuple[Tuple[Geometry, Point], Angle]
               ) -> None:
    (geometry, point), angle = geometry_point_with_angle

    result = geometry.rotate(angle, point)

    assert isinstance(result, type(geometry))


@given(strategies.geometries_points_with_angles)
def test_around_point(geometry_point_with_angle
                      : Tuple[Tuple[Geometry, Point], Angle]) -> None:
    (geometry, point), angle = geometry_point_with_angle

    result = geometry.rotate(angle, point)

    assert result == (geometry.translate(-point.x, -point.y)
                      .rotate(angle)
                      .translate(point.x, point.y))


@given(strategies.geometries_with_points)
def test_neutral_angle(geometry_with_point: Tuple[Geometry, Point]) -> None:
    geometry, point = geometry_with_point

    result = geometry.rotate(Angle(1, 0), point)

    assert result == geometry


@given(strategies.geometries_points_with_angles)
def test_round_trip(geometry_point_with_angle
                    : Tuple[Tuple[Geometry, Point], Angle]) -> None:
    (geometry, point), angle = geometry_point_with_angle

    result = geometry.rotate(angle, point)

    assert result.rotate(-angle, point) == geometry


@given(strategies.geometries_points_with_angles_pairs)
def test_consecutive(geometry_point_with_angles_pair
                     : Tuple[Tuple[Geometry, Point], Angle, Angle]) -> None:
    ((geometry, point), first_angle,
     second_angle) = geometry_point_with_angles_pair

    result = geometry.rotate(first_angle, point)

    assert (result.rotate(second_angle, point)
            == geometry.rotate(first_angle + second_angle, point))
