from math import isfinite
from typing import (Optional,
                    Tuple)

from reprit.base import generate_repr

from gon.core.arithmetic import robust_sqrt
from gon.geometry import Geometry
from gon.hints import Coordinate
from .hints import RawPoint


class Point(Geometry):
    __slots__ = '_x', '_y', '_raw',

    def __init__(self, x: Coordinate, y: Coordinate) -> None:
        """
        Initializes point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        """
        self._x, self._y = x, y
        self._raw = x, y

    __repr__ = generate_repr(__init__)

    def __hash__(self) -> int:
        """
        Returns hash value of the point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> hash(Point(0, 0)) == hash(Point(0, 0))
        True
        """
        return hash(self._raw)

    def __eq__(self, other: 'Point') -> bool:
        """
        Checks if the point is equal to the other.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> Point(0, 0) == Point(0, 0)
        True
        >>> Point(0, 0) == Point(0, 1)
        False
        >>> Point(0, 0) == Point(1, 1)
        False
        >>> Point(0, 0) == Point(1, 0)
        False
        """
        return (self._x == other._x and self._y == other._y
                if isinstance(other, Point)
                else NotImplemented)

    def __lt__(self, other: 'Point') -> bool:
        """
        Checks if the point is less than the other.
        Compares points lexicographically, ``x`` coordinates first.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        Reference:
            https://en.wikipedia.org/wiki/Lexicographical_order

        >>> Point(0, 0) < Point(0, 0)
        False
        >>> Point(0, 0) < Point(0, 1)
        True
        >>> Point(0, 0) < Point(1, 1)
        True
        >>> Point(0, 0) < Point(1, 0)
        True
        """
        return (self._raw < other._raw
                if isinstance(other, Point)
                else NotImplemented)

    @classmethod
    def from_raw(cls, raw: RawPoint) -> 'Point':
        """
        Constructs point from the combination of Python built-ins.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> Point.from_raw((1, 0)) == Point(1, 0)
        True
        """
        x, y = raw
        return cls(x, y)

    @property
    def x(self) -> Coordinate:
        """
        Returns ``x`` coordinate of the point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> Point(1, 0).x == 1
        True
        """
        return self._x

    @property
    def y(self) -> Coordinate:
        """
        Returns ``y`` coordinate of the point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> Point(1, 0).y == 0
        True
        """
        return self._y

    def distance_to(self, other: Geometry) -> Coordinate:
        """
        Returns distance between the point and the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> point = Point(1, 0)
        >>> point.distance_to(point) == 0
        True
        """
        return (self._distance_to_point(other)
                if isinstance(other, Point)
                else other.distance_to(self))

    def raw(self) -> RawPoint:
        """
        Returns the point as combination of Python built-ins.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> Point(1, 0).raw()
        (1, 0)
        """
        return self._raw

    def rotate(self,
               cosine: Coordinate,
               sine: Coordinate,
               point: Optional['Point'] = None) -> 'Point':
        """
        Rotates the point by given cosine & sine around given point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> point = Point(1, 0)
        >>> point.rotate(1, 0) == point
        True
        >>> point.rotate(0, 1, Point(1, 1)) == Point(2, 1)
        True
        """
        return (rotate_point_around_origin(self, cosine, sine)
                if point is None
                else rotate_translate_point(
                self, cosine, sine, *point_to_step(point, cosine, sine)))

    def scale(self,
              factor_x: Coordinate,
              factor_y: Optional[Coordinate] = None) -> 'Point':
        """
        Scales the point by given factor.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> point = Point(1, 0)
        >>> point.scale(1) == point.scale(1, 2) == point
        True
        """
        return scale_point(self, factor_x,
                           factor_x if factor_y is None else factor_y)

    def translate(self, step_x: Coordinate, step_y: Coordinate) -> 'Point':
        """
        Translates the point by given step.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> Point(1, 0).translate(1, 2) == Point(2, 2)
        True
        """
        return Point(self._x + step_x, self._y + step_y)

    def validate(self) -> None:
        """
        Checks if coordinates are finite.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> Point(0, 0).validate()
        """
        if not (isfinite(self._x) and isfinite(self._y)):
            raise ValueError('NaN/infinity coordinates are not supported.')

    def _distance_to_point(self, other: 'Point') -> Coordinate:
        return robust_sqrt((self._x - other._x) ** 2
                           + (self._y - other._y) ** 2)


def point_to_step(point: Point,
                  cosine: Coordinate,
                  sine: Coordinate) -> Tuple[Coordinate, Coordinate]:
    rotated_point = rotate_point_around_origin(point, cosine, sine)
    return point.x - rotated_point.x, point.y - rotated_point.y


def rotate_point_around_origin(point: Point,
                               cosine: Coordinate,
                               sine: Coordinate) -> Point:
    return Point(cosine * point._x - sine * point._y,
                 sine * point._x + cosine * point._y)


def rotate_translate_point(point: Point,
                           cosine: Coordinate,
                           sine: Coordinate,
                           step_x: Coordinate,
                           step_y: Coordinate) -> Point:
    return Point(cosine * point._x - sine * point._y + step_x,
                 sine * point._x + cosine * point._y + step_y)


def scale_point(point: Point,
                factor_x: Coordinate,
                factor_y: Coordinate) -> Point:
    return Point(point._x * factor_x, point._y * factor_y)
