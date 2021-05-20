import math
from numbers import Real
from typing import Optional

from ground.hints import Scalar
from reprit.base import generate_repr
from symba.base import Expression

from .geometry import (Coordinate,
                       Geometry)
from .rotating import (point_to_step,
                       rotate_point_around_origin,
                       rotate_translate_point)
from .scaling import scale_point


class Point(Geometry[Coordinate]):
    __slots__ = '_coordinates', '_x', '_y'

    def __init__(self, x: Coordinate, y: Coordinate) -> None:
        """
        Initializes point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        """
        self._coordinates = self._x, self._y = x, y

    __repr__ = generate_repr(__init__)

    def __hash__(self) -> int:
        """
        Returns hash value of the point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point
        >>> hash(Point(0, 0)) == hash(Point(0, 0))
        True
        """
        return hash(self._coordinates)

    def __eq__(self, other: 'Point[Coordinate]') -> bool:
        """
        Checks if the point is equal to the other.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point
        >>> Point(0, 0) == Point(0, 0)
        True
        >>> Point(0, 0) == Point(0, 1)
        False
        >>> Point(0, 0) == Point(1, 1)
        False
        >>> Point(0, 0) == Point(1, 0)
        False
        """
        return (self.x == other.x and self.y == other.y
                if isinstance(other, Point)
                else NotImplemented)

    def __le__(self, other: 'Point[Coordinate]') -> bool:
        """
        Checks if the point is less than or equal to the other.
        Compares points lexicographically, ``x`` coordinates first.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        Reference:
            https://en.wikipedia.org/wiki/Lexicographical_order

        >>> from gon.base import Point
        >>> Point(0, 0) <= Point(0, 0)
        True
        >>> Point(0, 0) <= Point(0, 1)
        True
        >>> Point(0, 0) <= Point(1, 1)
        True
        >>> Point(0, 0) <= Point(1, 0)
        True
        """
        return (self._coordinates <= other._coordinates
                if isinstance(other, Point)
                else NotImplemented)

    def __lt__(self, other: 'Point[Coordinate]') -> bool:
        """
        Checks if the point is less than the other.
        Compares points lexicographically, ``x`` coordinates first.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        Reference:
            https://en.wikipedia.org/wiki/Lexicographical_order

        >>> from gon.base import Point
        >>> Point(0, 0) < Point(0, 0)
        False
        >>> Point(0, 0) < Point(0, 1)
        True
        >>> Point(0, 0) < Point(1, 1)
        True
        >>> Point(0, 0) < Point(1, 0)
        True
        """
        return (self._coordinates < other._coordinates
                if isinstance(other, Point)
                else NotImplemented)

    @property
    def x(self) -> Coordinate:
        """
        Returns abscissa of the point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point
        >>> Point(1, 0).x == 1
        True
        """
        return self._x

    @property
    def y(self) -> Coordinate:
        """
        Returns ordinate of the point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point
        >>> Point(1, 0).y == 0
        True
        """
        return self._y

    def distance_to(self, other: Geometry[Coordinate]) -> Scalar:
        """
        Returns distance between the point and the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point
        >>> point = Point(1, 0)
        >>> point.distance_to(point) == 0
        True
        """
        return (self._context.sqrt(self._context.points_squared_distance(
                self, other))
                if isinstance(other, Point)
                else other.distance_to(self))

    def rotate(self,
               cosine: Coordinate,
               sine: Coordinate,
               point: Optional['Point[Coordinate]'] = None
               ) -> 'Point[Coordinate]':
        """
        Rotates the point by given cosine & sine around given point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point
        >>> point = Point(1, 0)
        >>> point.rotate(1, 0) == point
        True
        >>> point.rotate(0, 1, Point(1, 1)) == Point(2, 1)
        True
        """
        return (rotate_point_around_origin(self, cosine, sine,
                                           self._context.point_cls)
                if point is None
                else rotate_translate_point(
                self, cosine, sine, *point_to_step(point, cosine, sine),
                self._context.point_cls))

    def scale(self,
              factor_x: Coordinate,
              factor_y: Optional[Coordinate] = None) -> 'Point[Coordinate]':
        """
        Scales the point by given factor.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point
        >>> point = Point(1, 0)
        >>> point.scale(1) == point.scale(1, 2) == point
        True
        """
        return scale_point(self, factor_x,
                           factor_x if factor_y is None else factor_y,
                           self._context.point_cls)

    def translate(self,
                  step_x: Coordinate,
                  step_y: Coordinate) -> 'Point[Coordinate]':
        """
        Translates the point by given step.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point
        >>> Point(1, 0).translate(1, 2) == Point(2, 2)
        True
        """
        return self._context.point_cls(self.x + step_x, self.y + step_y)

    def validate(self) -> None:
        """
        Checks if coordinates are finite.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point
        >>> Point(0, 0).validate()
        """
        if not (is_finite(self.x) and is_finite(self.y)):
            raise ValueError('NaN/infinity coordinates are not supported.')


def is_finite(value: Scalar) -> bool:
    return (math.isfinite(value)
            if isinstance(value, Real)
            else isinstance(value, Expression) and value.is_finite)
