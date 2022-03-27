from typing import Generic

from ground.base import (Context,
                         Kind,
                         Orientation)
from ground.hints import (Point,
                          Scalar)
from reprit.base import generate_repr

Kind = Kind
Orientation = Orientation


class Angle(Generic[Scalar]):
    @classmethod
    def from_sides(cls,
                   vertex: Point[Scalar],
                   first_ray_point: Point[Scalar],
                   second_ray_point: Point[Scalar]) -> 'Angle[Scalar]':
        """
        Constructs angle from sides.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Angle, Point
        >>> angle = Angle.from_sides(Point(0, 0), Point(1, 0), Point(0, 1))
        >>> angle == Angle(0, 1)
        True
        """
        context = cls._context
        squared_lengths_product = (
                context.points_squared_distance(vertex, first_ray_point)
                * context.points_squared_distance(vertex, second_ray_point)
        )
        if not squared_lengths_product:
            return cls(1, 0)
        lengths_product_inverted = 1 / context.sqrt(squared_lengths_product)
        return cls(context.dot_product(vertex, first_ray_point, vertex,
                                       second_ray_point)
                   * lengths_product_inverted,
                   context.cross_product(vertex, first_ray_point, vertex,
                                         second_ray_point)
                   * lengths_product_inverted)

    @property
    def cosine(self) -> Scalar:
        """
        Returns cosine of the angle.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Angle
        >>> angle = Angle(0, 1)
        >>> angle.cosine == 0
        True
        """
        return self._cosine

    @property
    def kind(self) -> Kind:
        """
        Returns kind of the angle.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Angle, Kind
        >>> angle = Angle(0, 1)
        >>> angle.kind is Kind.RIGHT
        True
        """
        return Kind(to_sign(self.cosine))

    @property
    def orientation(self) -> Orientation:
        """
        Returns orientation of the angle.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Angle, Orientation
        >>> angle = Angle(0, 1)
        >>> angle.orientation is Orientation.COUNTERCLOCKWISE
        True
        """
        return Orientation(to_sign(self.sine))

    @property
    def sine(self) -> Scalar:
        """
        Returns sine of the angle.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Angle
        >>> angle = Angle(0, 1)
        >>> angle.sine == 1
        True
        """
        return self._sine

    __slots__ = '_cosine', '_sine'

    def __init__(self, cosine: Scalar, sine: Scalar) -> None:
        """
        Initializes angle.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        """
        self._cosine, self._sine = cosine, sine

    __repr__ = generate_repr(__init__)

    def __add__(self, other: 'Angle[Scalar]') -> 'Angle[Scalar]':
        """
        Returns sum of the angle with the other.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Angle
        >>> angle = Angle(0, 1)
        >>> angle + Angle(1, 0) == angle
        True
        """
        return (type(self)(self.cosine * other.cosine - self.sine * other.sine,
                           self.cosine * other.sine + self.sine * other.cosine)
                if isinstance(other, Angle)
                else NotImplemented)

    def __bool__(self) -> bool:
        """
        Checks that the angle is non-zero.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Angle
        >>> angle = Angle(0, 1)
        >>> bool(angle)
        True
        """
        return bool(self.sine)

    def __eq__(self, other: 'Angle') -> bool:
        """
        Checks if the angle is equal to the other.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Angle
        >>> angle = Angle(0, 1)
        >>> angle == angle
        True
        """
        return (self.cosine == other.cosine and self.sine == other.sine
                if isinstance(other, Angle)
                else NotImplemented)

    def __hash__(self) -> int:
        """
        Returns hash value of the angle.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Angle
        >>> angle = Angle(0, 1)
        >>> hash(angle) == hash(angle)
        True
        """
        return hash((self.cosine, self.sine))

    def __neg__(self) -> 'Angle[Scalar]':
        """
        Returns the angle negated.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Angle
        >>> angle = Angle(0, 1)
        >>> -angle == Angle(0, -1)
        True
        """
        return type(self)(self.cosine, -self.sine)

    def __pos__(self) -> 'Angle[Scalar]':
        """
        Returns the angle positive.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Angle
        >>> angle = Angle(0, 1)
        >>> +angle == angle
        True
        """
        return self

    def __sub__(self, other: 'Angle[Scalar]') -> 'Angle[Scalar]':
        """
        Returns difference of the angle with the other.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Angle
        >>> angle = Angle(0, 1)
        >>> angle - Angle(1, 0) == angle
        True
        """
        return (type(self)(self.cosine * other.cosine + self.sine * other.sine,
                           self.sine * other.cosine - self.cosine * other.sine)
                if isinstance(other, Angle)
                else NotImplemented)

    def validate(self) -> None:
        """
        Checks if the angle is valid.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Angle
        >>> angle = Angle(0, 1)
        >>> angle.validate()
        """
        if square(self.cosine) + square(self.sine) != 1:
            raise ValueError('Pythagorean trigonometric identity is unmet.')

    _context = ...  # type: Context


def square(value: Scalar) -> Scalar:
    return value * value


def to_sign(value: Scalar) -> int:
    return 1 if value > 0 else (-1 if value else 0)
