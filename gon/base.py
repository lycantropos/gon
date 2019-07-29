from reprit.base import generate_repr

from .hints import Scalar
from .utils import validate_value


class Point:
    __slots__ = ('_x', '_y')

    def __new__(cls, x: Scalar, y: Scalar) -> 'Point':
        validate_value(x)
        validate_value(y)
        return super().__new__(cls)

    def __init__(self, x: Scalar, y: Scalar) -> None:
        self._x = x
        self._y = y

    @property
    def x(self) -> Scalar:
        return self._x

    @property
    def y(self) -> Scalar:
        return self._y

    __repr__ = generate_repr(__init__)

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    def __eq__(self, other: 'Point') -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self._x == other._x and self._y == other._y

    def squared_distance_to(self, destination: 'Point') -> Scalar:
        return Vector.from_points(self, destination).squared_length


class Vector:
    __slots__ = ('_x', '_y')

    def __new__(cls, x: Scalar, y: Scalar) -> 'Vector':
        validate_value(x)
        validate_value(y)
        return super().__new__(cls)

    def __init__(self, x: Scalar, y: Scalar) -> None:
        self._x = x
        self._y = y

    def __bool__(self) -> bool:
        """
        Based on:
            checking if vector is non-zero.

        Reference:
            https://en.wikipedia.org/wiki/Zero_element

        Time complexity:
            O(1)

        >>> zero_vector = Vector(0, 0)
        >>> not zero_vector
        True
        """
        return bool(self._x and self._y)

    @property
    def x(self) -> Scalar:
        return self._x

    @property
    def y(self) -> Scalar:
        return self._y

    __repr__ = generate_repr(__init__)

    @classmethod
    def from_points(cls, start: Point, end: Point) -> 'Vector':
        return cls(end.x - start.x, end.y - start.y)

    @property
    def squared_length(self) -> Scalar:
        return self.x ** 2 + self.y ** 2

    def cross_z(self, other: 'Vector') -> Scalar:
        """
        Based on:
            z-coordinate of planar vectors' cross product
            (assuming that their z-coordinates are zeros).

        Reference:
            https://en.wikipedia.org/wiki/Cross_product

        Time complexity:
            O(1)

        >>> basis_vector_x, basis_vector_y = Vector(1, 0), Vector(0, 1)
        >>> basis_vector_x.cross_z(basis_vector_y) == 1
        True
        >>> basis_vector_x.cross_z(basis_vector_x) == 0
        True
        >>> basis_vector_y.cross_z(basis_vector_y) == 0
        True
        """
        return self.x * other.y - self.y * other.x

    def dot(self, other: 'Vector') -> Scalar:
        return self.x * other.x + self.y * other.y
