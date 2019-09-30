from enum import (IntEnum,
                  unique)

from reprit.base import generate_repr

from .base import Point
from .robust import parallelogram
from .utils import to_sign


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
    def orientation(self) -> Orientation:
        return Orientation(to_sign(
                parallelogram.signed_area(self._vertex,
                                          self._first_ray_point,
                                          self._second_ray_point)))
