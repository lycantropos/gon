from typing import Tuple

from hypothesis import given

from gon.base import (Angle,
                      Point,
                      Vector)
from . import strategies


@given(strategies.vectors_points_with_angles)
def test_basic(vector_point_with_angle: Tuple[Tuple[Vector, Point], Angle]
               ) -> None:
    (vector, point), angle = vector_point_with_angle

    result = vector.rotate(angle, point)

    assert isinstance(result, type(vector))


@given(strategies.vectors_points_with_angles)
def test_around_point(vector_point_with_angle
                      : Tuple[Tuple[Vector, Point], Angle]) -> None:
    (vector, point), angle = vector_point_with_angle

    result = vector.rotate(angle, point)

    assert result == vector.rotate(angle)


@given(strategies.vectors_with_points)
def test_neutral_angle(vector_with_point: Tuple[Vector, Point]) -> None:
    vector, point = vector_with_point

    result = vector.rotate(Angle(1, 0), point)

    assert result == vector


@given(strategies.vectors_points_with_angles)
def test_round_trip(vector_point_with_angle: Tuple[Tuple[Vector, Point], Angle]
                    ) -> None:
    (vector, point), angle = vector_point_with_angle

    result = vector.rotate(angle, point)

    assert result.rotate(-angle, point) == vector


@given(strategies.vectors_points_with_angles_pairs)
def test_consecutive(vector_point_with_angle_pair
                     : Tuple[Tuple[Vector, Point], Angle, Angle]) -> None:
    (vector, point), first_angle, second_angle = vector_point_with_angle_pair

    result = vector.rotate(first_angle, point)

    assert (result.rotate(second_angle, point)
            == vector.rotate(first_angle + second_angle, point))
