from typing import Tuple

from hypothesis import given

from gon.base import (Point,
                      Vector)
from gon.hints import Scalar
from . import strategies


@given(strategies.vectors_points_with_cosines_sines)
def test_basic(vector_point_with_cosine_sine
               : Tuple[Tuple[Vector, Point], Tuple[Scalar, Scalar]]
               ) -> None:
    (vector, point), (cosine, sine) = vector_point_with_cosine_sine

    result = vector.rotate(cosine, sine, point)

    assert isinstance(result, type(vector))


@given(strategies.vectors_points_with_cosines_sines)
def test_around_point(vector_point_with_cosine_sine
                      : Tuple[Tuple[Vector, Point],
                              Tuple[Scalar, Scalar]]) -> None:
    (vector, point), (cosine, sine) = vector_point_with_cosine_sine

    result = vector.rotate(cosine, sine, point)

    assert result == vector.rotate(cosine, sine)


@given(strategies.vectors_with_points)
def test_neutral_angle(vector_with_point: Tuple[Vector, Point]) -> None:
    vector, point = vector_with_point

    result = vector.rotate(1, 0, point)

    assert result == vector


@given(strategies.vectors_points_with_cosines_sines)
def test_round_trip(vector_point_with_cosine_sine
                    : Tuple[Tuple[Vector, Point],
                            Tuple[Scalar, Scalar]]) -> None:
    (vector, point), (cosine, sine) = vector_point_with_cosine_sine

    result = vector.rotate(cosine, sine, point)

    assert result.rotate(cosine, -sine, point) == vector


@given(strategies.vectors_points_with_cosines_sines_pairs)
def test_consecutive(vector_point_with_cosine_sine_pair
                     : Tuple[Tuple[Vector, Point],
                             Tuple[Scalar, Scalar],
                             Tuple[Scalar, Scalar]]) -> None:
    ((vector, point), (first_cosine, first_sine),
     (second_cosine, second_sine)) = vector_point_with_cosine_sine_pair

    result = vector.rotate(first_cosine, first_sine, point)

    angle_sum_cosine = first_cosine * second_cosine - first_sine * second_sine
    angle_sum_sine = first_sine * second_cosine + second_sine * first_cosine
    assert (result.rotate(second_cosine, second_sine, point)
            == vector.rotate(angle_sum_cosine, angle_sum_sine, point))
