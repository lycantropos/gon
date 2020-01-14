from enum import (IntEnum,
                  unique)

from reprit.base import generate_repr
from robust import (parallelogram,
                    projection)

from .base import (Point,
                   _point_to_real_tuple)
from .utils import to_sign


@unique
class AngleKind(IntEnum):
    OBTUSE = -1
    RIGHT = 0
    ACUTE = 1


@unique
class Orientation(IntEnum):
    CLOCKWISE = -1
    COLLINEAR = 0
    COUNTERCLOCKWISE = 1


class Angle:
    def __init__(self,
                 first_ray_point: Point,
                 vertex: Point,
                 second_ray_point: Point) -> None:
        self._first_ray_point = first_ray_point
        self._vertex = vertex
        self._second_ray_point = second_ray_point

    @property
    def vertex(self) -> Point:
        return self._vertex

    @property
    def first_ray_point(self) -> Point:
        return self._first_ray_point

    @property
    def second_ray_point(self) -> Point:
        return self._second_ray_point

    __repr__ = generate_repr(__init__)

    @property
    def kind(self) -> AngleKind:
        return AngleKind(to_sign(projection.signed_length(
                _point_to_real_tuple(self._vertex),
                _point_to_real_tuple(self._first_ray_point),
                _point_to_real_tuple(self._vertex),
                _point_to_real_tuple(self._second_ray_point))))

    @property
    def orientation(self) -> Orientation:
        return Orientation(to_sign(parallelogram.signed_area(
                _point_to_real_tuple(self._vertex),
                _point_to_real_tuple(self._first_ray_point),
                _point_to_real_tuple(self._vertex),
                _point_to_real_tuple(self._second_ray_point))))
