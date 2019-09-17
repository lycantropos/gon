from enum import (IntEnum,
                  unique)

from reprit.base import generate_repr

from .base import Point
from .robust import counterclockwise
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


class Region(IntEnum):
    pass


@unique
class Fixed(Region):
    ZERO_RADIAN = 0
    HALF_PI_RADIAN = 2
    PI_RADIAN = 4
    ONE_AND_A_HALF_RADIAN = 6


@unique
class Quadrant(Region):
    FIRST = 1
    SECOND = 3
    THIRD = 5
    FOURTH = 7


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
        determinant = counterclockwise.determinant(self._vertex,
                                                   self._first_ray_point,
                                                   self._second_ray_point)
        return Orientation(to_sign(determinant))
