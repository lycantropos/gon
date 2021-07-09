from typing import Generic

from ground.base import Context
from reprit.base import generate_repr

from .angular import (Kind,
                      Orientation)
from .geometry import Coordinate
from .point import Point


class Vector(Generic[Coordinate]):
    @classmethod
    def from_position(cls, end: Point[Coordinate]) -> 'Vector[Coordinate]':
        """
        Constructs position vector.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Vector
        >>> vector = Vector.from_position(Point(2, 0))
        >>> vector == Vector(Point(0, 0), Point(2, 0))
        True
        """
        return cls(cls._context.origin, end)

    @property
    def end(self) -> Point[Coordinate]:
        """
        Returns end of the vector.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Vector
        >>> vector = Vector(Point(0, 0), Point(2, 0))
        >>> vector.end == Point(2, 0)
        True
        """
        return self._end

    @property
    def length(self) -> Coordinate:
        """
        Returns length of the vector.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Vector
        >>> vector = Vector(Point(0, 0), Point(2, 0))
        >>> vector.length == 2
        True
        """
        return self._context.sqrt(self._context.points_squared_distance(
                self.start, self.end))

    @property
    def start(self) -> Point[Coordinate]:
        """
        Returns start of the vector.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Vector
        >>> vector = Vector(Point(0, 0), Point(2, 0))
        >>> vector.start == Point(0, 0)
        True
        """
        return self._start

    __slots__ = '_start', '_end'

    def __init__(self,
                 start: Point[Coordinate],
                 end: Point[Coordinate]) -> None:
        """
        Initializes vector.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        """
        self._end, self._start = end, start

    __repr__ = generate_repr(__init__)

    def __add__(self, other: 'Vector[Coordinate]') -> 'Vector[Coordinate]':
        """
        Returns sum of the vector with the other.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Vector
        >>> vector = Vector(Point(0, 0), Point(2, 0))
        >>> vector + Vector(Point(0, 0), Point(0, 0)) == vector
        True
        """
        return (type(self)(_add_points(self.start, other.start),
                           _add_points(self.end, other.end))
                if isinstance(other, Vector)
                else NotImplemented)

    def __bool__(self) -> bool:
        """
        Checks that the vector is non-zero.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Vector
        >>> vector = Vector(Point(0, 0), Point(2, 0))
        >>> bool(vector)
        True
        """
        return self.start != self.end

    def __eq__(self, other: 'Vector[Coordinate]') -> bool:
        """
        Checks if the vector is equal to the other.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Vector
        >>> vector = Vector(Point(0, 0), Point(2, 0))
        >>> vector == vector
        True
        """
        return (_sub_points(self.end, self.start)
                == _sub_points(other.end, other.start)
                if isinstance(other, Vector)
                else NotImplemented)

    def __hash__(self) -> int:
        """
        Returns hash value of the vector.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Vector
        >>> vector = Vector(Point(0, 0), Point(2, 0))
        >>> hash(vector) == hash(vector)
        True
        >>> hash(vector) != hash(-vector)
        True
        """
        return hash(_sub_points(self.end, self.start))

    def __mul__(self, factor: Coordinate) -> 'Vector[Coordinate]':
        """
        Scales the vector by given factor.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Vector
        >>> vector = Vector(Point(0, 0), Point(2, 0))
        >>> vector * 1 == vector
        True
        """
        return type(self)(self.start.scale(factor), self.end.scale(factor))

    def __neg__(self) -> 'Vector[Coordinate]':
        """
        Returns the vector negated.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Vector
        >>> vector = Vector(Point(0, 0), Point(2, 0))
        >>> -vector == Vector(Point(2, 0), Point(0, 0))
        True
        """
        return type(self)(self.end, self.start)

    def __pos__(self) -> 'Vector[Coordinate]':
        """
        Returns the vector positive.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Vector
        >>> vector = Vector(Point(0, 0), Point(2, 0))
        >>> +vector == vector
        True
        """
        return self

    __rmul__ = __mul__

    def __sub__(self, other: 'Vector[Coordinate]') -> 'Vector':
        """
        Returns difference of the vector with the other.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Vector
        >>> vector = Vector(Point(0, 0), Point(2, 0))
        >>> vector - Vector(Point(0, 0), Point(0, 0)) == vector
        True
        """
        return type(self)(_sub_points(self.start, other.start),
                          _sub_points(self.end, other.end))

    def cross(self, other: 'Vector[Coordinate]') -> Coordinate:
        """
        Returns cross product of the vector with the other.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Vector
        >>> vector = Vector(Point(0, 0), Point(2, 0))
        >>> vector.cross(vector) == 0
        True
        """
        return self._context.cross_product(self.start, self.end, other.start,
                                           other.end)

    def dot(self, other: 'Vector[Coordinate]') -> Coordinate:
        """
        Returns dot product of the vector with the other.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Vector
        >>> vector = Vector(Point(0, 0), Point(2, 0))
        >>> vector.dot(vector) == 4
        True
        """
        return self._context.dot_product(self.start, self.end, other.start,
                                         other.end)

    def kind_of(self, point: Point[Coordinate]) -> Kind:
        """
        Returns kind of angle formed by the vector and given point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Kind, Point, Vector
        >>> vector = Vector(Point(0, 0), Point(2, 0))
        >>> vector.kind_of(vector.end) is Kind.ACUTE
        True
        """
        return self._context.angle_kind(self.start, self.end, point)

    def orientation_of(self, point: Point[Coordinate]) -> Orientation:
        """
        Returns orientation of angle formed by the vector and given point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Orientation, Point, Vector
        >>> vector = Vector(Point(0, 0), Point(2, 0))
        >>> vector.orientation_of(vector.end) is Orientation.COLLINEAR
        True
        """
        return self._context.angle_orientation(self.start, self.end, point)

    def validate(self) -> None:
        """
        Checks if vector is finite.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> from gon.base import Point, Vector
        >>> vector = Vector(Point(0, 0), Point(2, 0))
        >>> vector.validate()
        """
        self.start.validate()
        self.end.validate()
        _sub_points(self.end, self.start).validate()

    _context = ...  # type: Context


def _add_points(first: Point[Coordinate],
                second: Point[Coordinate]) -> Point[Coordinate]:
    return first.translate(second.x, second.y)


def _sub_points(minuend: Point[Coordinate],
                subtrahend: Point[Coordinate]) -> Point[Coordinate]:
    return minuend.translate(-subtrahend.x, -subtrahend.y)
