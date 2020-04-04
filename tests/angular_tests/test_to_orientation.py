from typing import Tuple

from hypothesis import given

from gon.angular import (Orientation,
                         to_orientation)
from gon.primitive import Point
from tests.utils import equivalence
from . import strategies


@given(strategies.unique_points_triplets)
def test_basic(points_triplet: Tuple[Point, Point, Point]) -> None:
    first_ray_point, vertex, second_ray_point = points_triplet

    result = to_orientation(first_ray_point, vertex, second_ray_point)

    assert isinstance(result, Orientation)


@given(strategies.unique_points_triplets)
def test_rays_flip(points_triplet: Tuple[Point, Point, Point]) -> None:
    first_ray_point, vertex, second_ray_point = points_triplet

    result = to_orientation(first_ray_point, vertex, second_ray_point)

    flipped_orientation = to_orientation(second_ray_point, vertex,
                                         first_ray_point)
    assert equivalence(result is Orientation.COLLINEAR,
                       flipped_orientation is result)
