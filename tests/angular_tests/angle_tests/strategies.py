from functools import partial
from typing import (Sequence,
                    Tuple)

from hypothesis import strategies
from lz.functional import pack

from gon.angular import Angle
from gon.base import Point
from tests.strategies import (points,
                              points_strategies)
from tests.utils import (Strategy,
                         is_non_origin_point,
                         reflect_point,
                         to_origin,
                         to_perpendicular_point)

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


def to_straight_origin_angles(point: Point) -> Angle:
    return Angle(point, to_origin(point), reflect_point(point))


straight_origin_angles = (points
                          .filter(is_non_origin_point)
                          .map(to_straight_origin_angles))


def to_right_origin_angle(point: Point) -> Angle:
    return Angle(point, to_origin(point), to_perpendicular_point(point))


right_origin_angles = (points
                       .filter(is_non_origin_point)
                       .map(to_right_origin_angle))
