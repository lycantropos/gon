from hypothesis import given

from gon.angular import Angle
from gon.base import Point
from . import strategies


@given(strategies.unique_points_triplets)
def test_basic(points_triplet: Point) -> None:
    vertex, first_ray_point, second_ray_point = points_triplet

    angle = Angle(first_ray_point, vertex, second_ray_point)

    assert angle.vertex == vertex
    assert angle.first_ray_point == first_ray_point
    assert angle.second_ray_point == second_ray_point
