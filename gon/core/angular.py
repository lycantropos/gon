from ground.base import (Orientation,
                         get_context)

from .point import Point

Orientation = Orientation


def to_orientation(vertex: Point,
                   first_ray_point: Point,
                   second_ray_point: Point) -> Orientation:
    return get_context().angle_orientation(vertex, first_ray_point,
                                           second_ray_point)
