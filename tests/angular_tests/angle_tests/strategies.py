from functools import partial
from typing import Tuple, Sequence

from hypothesis import strategies
from lz.functional import pack

from gon.angular import Angle
from gon.base import Point
from tests.strategies import points_strategies
from tests.utils import to_origin, Strategy, is_non_origin_point

unique_points_triplets = points_strategies.flatmap(partial(strategies.lists,
                                                           min_size=3,
                                                           max_size=3,
                                                           unique=True))
angles = unique_points_triplets.map(pack(Angle))


def to_origin_angles(rays_points: Tuple[Point, Point]) -> Angle:
    first_ray_point, second_ray_point = rays_points
    origin = to_origin(first_ray_point)
    return Angle(first_ray_point, origin, second_ray_point)


def to_non_origin_points_pairs(points: Strategy[Point]
                               ) -> Strategy[Sequence[Point]]:
    return strategies.lists(points.filter(is_non_origin_point),
                            min_size=2,
                            max_size=2,
                            unique=True)


origin_angles = (points_strategies
                 .flatmap(to_non_origin_points_pairs)
                 .map(to_origin_angles))
