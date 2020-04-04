from robust.angular import (Orientation,
                            orientation as _orientation)

from .primitive import Point

Orientation = Orientation


def to_orientation(first_ray_point: Point,
                   vertex: Point,
                   second_ray_point: Point) -> Orientation:
    return _orientation(first_ray_point.raw(),
                        vertex.raw(),
                        second_ray_point.raw())
