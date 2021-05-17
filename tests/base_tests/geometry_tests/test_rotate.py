from typing import Tuple

from hypothesis import given

from gon.base import (Geometry,
                      Point)
from gon.hints import Scalar
from . import strategies


@given(strategies.rational_geometries_points_with_cosines_sines)
def test_basic(geometry_point_with_cosine_sine
               : Tuple[Tuple[Geometry, Point], Tuple[Scalar, Scalar]]
               ) -> None:
    (geometry, point), (cosine, sine) = geometry_point_with_cosine_sine

    result = geometry.rotate(cosine, sine, point)

    assert isinstance(result, type(geometry))


@given(strategies.rational_geometries_points_with_cosines_sines)
def test_around_point(geometry_point_with_cosine_sine
                      : Tuple[Tuple[Geometry, Point],
                              Tuple[Scalar, Scalar]]) -> None:
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
                            Tuple[Scalar, Scalar]]) -> None:
    (geometry, point), (cosine, sine) = geometry_point_with_cosine_sine

    result = geometry.rotate(cosine, sine, point)

    assert result.rotate(cosine, -sine, point) == geometry


@given(strategies.rational_geometries_points_with_cosines_sines_pairs)
def test_consecutive(geometry_point_with_cosine_sine_pair
                     : Tuple[Tuple[Geometry, Point],
                             Tuple[Scalar, Scalar],
                             Tuple[Scalar, Scalar]]) -> None:
    ((geometry, point), (first_cosine, first_sine),
     (second_cosine, second_sine)) = geometry_point_with_cosine_sine_pair

    result = geometry.rotate(first_cosine, first_sine, point)

    angle_sum_cosine = first_cosine * second_cosine - first_sine * second_sine
    angle_sum_sine = first_sine * second_cosine + second_sine * first_cosine
    assert (result.rotate(second_cosine, second_sine, point)
            == geometry.rotate(angle_sum_cosine, angle_sum_sine, point))
