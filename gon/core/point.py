import math
from numbers import Real
from typing import Optional

from ground.hints import Scalar
from reprit.base import generate_repr
from symba.base import Expression

from .angle import Angle
from .geometry import Geometry


class Point(Geometry[Scalar]):
    __slots__ = '_coordinates', '_x', '_y'

    def __init__(self, x: Scalar, y: Scalar) -> None:
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

    def __eq__(self, other: 'Point[Scalar]') -> bool:
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

    def __le__(self, other: 'Point[Scalar]') -> bool:
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

    def __lt__(self, other: 'Point[Scalar]') -> bool:
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
    def x(self) -> Scalar:
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
    def y(self) -> Scalar:
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

    def distance_to(self, other: Geometry[Scalar]) -> Scalar:
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
        if isinstance(other, Point):
            return self._context.sqrt(self._context.points_squared_distance(
                    self, other
            ))
        else:
            return other.distance_to(self)

    def rotate(self,
               angle: Angle,
               point: Optional['Point[Scalar]'] = None) -> 'Point[Scalar]':
        """
        Rotates the point by given angle around given point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Angle, Point
        >>> point = Point(1, 0)
        >>> point.rotate(Angle(1, 0)) == point
        True
        >>> point.rotate(Angle(0, 1), Point(1, 1)) == Point(2, 1)
        True
        """
        return (self._context.rotate_point_around_origin(self, angle.cosine,
                                                         angle.sine)
                if point is None
                else self._context.rotate_point(self, angle.cosine, angle.sine,
                                                point))

    def scale(self,
              factor_x: Scalar,
              factor_y: Optional[Scalar] = None) -> 'Point[Scalar]':
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
        return self._context.scale_point(
                self, factor_x, factor_x if factor_y is None else factor_y)

    def translate(self, step_x: Scalar, step_y: Scalar) -> 'Point[Scalar]':
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
        return self._context.translate_point(self, step_x, step_y)

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
