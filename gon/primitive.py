import math
from typing import Tuple

from reprit.base import generate_repr

from .geometry import Geometry
from .hints import Coordinate

RawPoint = Tuple[Coordinate, Coordinate]


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

    def validate(self) -> None:
        """
        Checks if coordinates are finite.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> Point(0, 0).validate()
        """
        _validate_coordinate(self._x)
        _validate_coordinate(self._y)


def _validate_coordinate(value: Coordinate) -> None:
    if not math.isfinite(value):
        raise ValueError('NaN/infinity coordinates are not supported.')
