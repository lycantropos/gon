from enum import IntEnum

from reprit.base import generate_repr

from .base import (Point,
                   Vector)
from .utils import to_sign


class Angle:
    def __init__(self,
                 vertex: Point,
                 first_ray_point: Point,
                 second_ray_point: Point) -> None:
        self._vertex = vertex
        self._first_ray_point = first_ray_point
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
    def orientation(self) -> int:
        first_ray_vector = Vector.from_points(self.vertex,
                                              self._first_ray_point)
        second_ray_vector = Vector.from_points(self.vertex,
                                               self._second_ray_point)
        return to_sign(first_ray_vector.cross_z(second_ray_vector))

    @property
    def is_acute(self) -> bool:
        return self.kind == AngleKind.ACUTE

    @property
    def is_right(self) -> bool:
        return self.kind == AngleKind.RIGHT

    @property
    def is_obtuse(self) -> bool:
        return self.kind == AngleKind.OBTUSE

    @property
    def kind(self) -> int:
        return to_sign(
                self.vertex.squared_distance_to(self._first_ray_point)
                - self._first_ray_point.squared_distance_to(
                        self._second_ray_point)
                + self.vertex.squared_distance_to(
                        self._second_ray_point))


class AngleKind(IntEnum):
    OBTUSE = -1
    RIGHT = 0
    ACUTE = 1


class Orientation(IntEnum):
    CLOCKWISE = -1
    COLLINEAR = 0
    COUNTERCLOCKWISE = 1
