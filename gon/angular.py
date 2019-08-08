from enum import IntEnum

from reprit.base import generate_repr

from .base import (Point,
                   Vector)
from .hints import Scalar
from .utils import to_sign


class AngleKind(IntEnum):
    OBTUSE = -1
    RIGHT = 0
    ACUTE = 1


class Orientation(IntEnum):
    CLOCKWISE = -1
    COLLINEAR = 0
    COUNTERCLOCKWISE = 1


class Angle:
    def __init__(self,
                 first_ray_point: Point,
                 vertex: Point,
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

    def __lt__(self, other: 'Angle') -> bool:
        first_ray_vector = self.first_ray_vector
        second_ray_vector = self.second_ray_vector
        other_first_ray_vector = other.first_ray_vector
        other_second_ray_vector = other.second_ray_vector
        cosine = first_ray_vector.dot(second_ray_vector)
        other_cosine = other_first_ray_vector.dot(other_second_ray_vector)
        sine = first_ray_vector.cross_z(second_ray_vector)
        other_sine = other_first_ray_vector.cross_z(other_second_ray_vector)
        region = _to_region(cosine, sine)
        other_region = _to_region(other_cosine, other_sine)
        if region is not other_region:
            return region < other_region
        if region in Fixed:
            return False
        return cosine / sine > other_cosine / other_sine

    @property
    def orientation(self) -> Orientation:
        return Orientation(to_sign(self.first_ray_vector
                                   .cross_z(self.second_ray_vector)))

    @property
    def first_ray_vector(self) -> Vector:
        return Vector.from_points(self.vertex, self._first_ray_point)

    @property
    def second_ray_vector(self):
        return Vector.from_points(self.vertex, self._second_ray_point)

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
    def kind(self) -> AngleKind:
        """
        Based on:
            "law of cosines" (aka "cosine formula").

        Reference:
            https://en.wikipedia.org/wiki/Law_of_cosines

        Time complexity:
            O(1)

        >>> angle = Angle(Point(1, 0), Point(0, 0), Point(0, 1))
        >>> angle.kind == AngleKind.RIGHT
        True
        """
        return AngleKind(to_sign(
                self.vertex.squared_distance_to(self._first_ray_point)
                - self._first_ray_point.squared_distance_to(
                        self._second_ray_point)
                + self.vertex.squared_distance_to(
                        self._second_ray_point)))

class Region(IntEnum):
    pass


class Fixed(Region):
    ZERO_RADIAN = 0
    HALF_PI_RADIAN = 2
    PI_RADIAN = 4
    ONE_AND_A_HALF_RADIAN = 6


class Quadrant(Region):
    FIRST = 1
    SECOND = 3
    THIRD = 5
    FOURTH = 7


def _to_region(cosine: Scalar, sine: Scalar) -> Region:
    if cosine > 0:
        if sine > 0:
            return Quadrant.FIRST
        elif sine < 0:
            return Quadrant.FOURTH
        else:
            return Fixed.ZERO_RADIAN
    elif cosine < 0:
        if sine > 0:
            return Quadrant.SECOND
        elif sine < 0:
            return Quadrant.THIRD
        else:
            return Fixed.PI_RADIAN
    else:
        if sine > 0:
            return Fixed.HALF_PI_RADIAN
        else:
            return Fixed.ONE_AND_A_HALF_RADIAN


def to_squared_cosine(angle: Angle) -> Scalar:
    first_ray_vector = angle.first_ray_vector
    second_ray_vector = angle.second_ray_vector
    return (first_ray_vector.dot(second_ray_vector) ** 2
            / (first_ray_vector.squared_length
               * second_ray_vector.squared_length))
