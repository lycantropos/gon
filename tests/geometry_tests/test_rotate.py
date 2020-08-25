from typing import Tuple

from hypothesis import given

from gon.geometry import Geometry
from gon.hints import Coordinate
from gon.primitive import Point
from . import strategies


@given(strategies.rational_geometries_points_with_cosines_sines)
def test_basic(geometry_point_with_cosine_sine
               : Tuple[Tuple[Geometry, Point], Tuple[Coordinate, Coordinate]]
               ) -> None:
    (geometry, point), (cosine, sine) = geometry_point_with_cosine_sine

    result = geometry.rotate(cosine, sine, point)

    assert isinstance(result, type(geometry))


@given(strategies.rational_geometries_points_with_cosines_sines)
def test_around_point(geometry_point_with_cosine_sine
                      : Tuple[Tuple[Geometry, Point],
                              Tuple[Coordinate, Coordinate]]) -> None:
    (geometry, point), (cosine, sine) = geometry_point_with_cosine_sine

    result = geometry.rotate(cosine, sine, point)

    assert result == (geometry.translate(-point.x, -point.y)
                      .rotate(cosine, sine)
                      .translate(point.x, point.y))


@given(strategies.rational_geometries_with_points)
def test_neutral_angle(geometry_with_point: Tuple[Geometry, Point]) -> None:
    geometry, point = geometry_with_point

    result = geometry.rotate(1, 0, point)

    assert result == geometry


@given(strategies.rational_geometries_points_with_cosines_sines)
def test_round_trip(geometry_point_with_cosine_sine
                    : Tuple[Tuple[Geometry, Point],
                            Tuple[Coordinate, Coordinate]]) -> None:
    (geometry, point), (cosine, sine) = geometry_point_with_cosine_sine

    result = geometry.rotate(cosine, sine, point)

    assert result.rotate(cosine, -sine, point) == geometry


@given(strategies.rational_geometries_points_with_cosines_sines)
def test_double_angle(geometry_point_with_cosine_sine
                      : Tuple[Tuple[Geometry, Point],
                              Tuple[Coordinate, Coordinate]]) -> None:
    (geometry, point), (cosine, sine) = geometry_point_with_cosine_sine

    result = geometry.rotate(cosine, sine, point)

    double_angle_sine = 2 * sine * cosine
    double_angle_cosine = cosine * cosine - sine * sine
    assert (result.rotate(cosine, sine, point)
            == geometry.rotate(double_angle_cosine, double_angle_sine, point))
