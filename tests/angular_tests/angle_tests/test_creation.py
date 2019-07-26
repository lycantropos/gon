from hypothesis import given

from gon.angular import Angle
from gon.base import Point
from . import strategies


@given(strategies.points, strategies.points, strategies.points)
def test_basic(vertex: Point,
               first_ray_point: Point,
               second_ray_point: Point) -> None:
    angle = Angle(first_ray_point, vertex, second_ray_point)

    assert angle.vertex == vertex
    assert angle.first_ray_point == first_ray_point
    assert angle.second_ray_point == second_ray_point
