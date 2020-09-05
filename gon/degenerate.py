from typing import (Optional,
                    Union)

from reprit.base import generate_repr

from .compound import (Compound,
                       Location,
                       Relation)
from .geometry import Geometry
from .hints import (Coordinate,
                    Domain)
from .primitive import Point

try:
    from typing import NoReturn
except ImportError:
    from typing_extensions import NoReturn

RAW_EMPTY = None
RawEmpty = type(RAW_EMPTY)


class Empty(Compound):
    __slots__ = ()

    _instance = None

    def __new__(cls) -> 'Empty':
        """
        Returns empty geometry instance.

        Based on singleton pattern.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        Reference:
            https://en.wikipedia.org/wiki/Singleton_pattern
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    __repr__ = generate_repr(__new__)

    def __and__(self, other: Compound) -> Compound:
        """
        Returns intersection of the empty geometry with the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY & EMPTY is EMPTY
        True
        """
        return (self
                if isinstance(other, Compound)
                else NotImplemented)

    __rand__ = __and__

    def __contains__(self, other: Geometry) -> bool:
        """
        Checks if the empty geometry contains the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY in EMPTY
        False
        """
        return False

    def __eq__(self, other: 'Empty') -> bool:
        """
        Checks if empty geometries are equal.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY == EMPTY
        True
        """
        return (self is other
                if isinstance(other, Geometry)
                else NotImplemented)

    def __ge__(self, other: Compound) -> bool:
        """
        Checks if the empty geometry is a superset of the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY >= EMPTY
        True
        """
        return (self is other
                if isinstance(other, Compound)
                else NotImplemented)

    def __gt__(self, other: Compound) -> bool:
        """
        Checks if the empty geometry is a strict superset
        of the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY > EMPTY
        False
        """
        return (False
                if isinstance(other, Compound)
                else NotImplemented)

    def __hash__(self) -> int:
        """
        Returns hash value of the empty geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> hash(EMPTY) == hash(EMPTY)
        True
        """
        return 0

    def __le__(self, other: Compound) -> bool:
        """
        Checks if the empty geometry is a subset of the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY <= EMPTY
        True
        """
        return (True
                if isinstance(other, Compound)
                else NotImplemented)

    def __lt__(self, other: Compound) -> bool:
        """
        Checks if the empty geometry is a strict subset of the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY < EMPTY
        False
        """
        return (self is not other
                if isinstance(other, Compound)
                else NotImplemented)

    def __or__(self, other: Compound) -> Compound:
        """
        Returns union of the empty geometry with the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY | EMPTY is EMPTY
        True
        """
        return (other
                if isinstance(other, Compound)
                else NotImplemented)

    __ror__ = __or__

    def __sub__(self, other: Compound) -> Compound:
        """
        Returns difference of the empty geometry with the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY - EMPTY is EMPTY
        True
        """
        return (self
                if isinstance(other, Compound)
                else NotImplemented)

    def __rsub__(self, other: Compound) -> Compound:
        """
        Returns difference of the other geometry with the empty geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        """
        return (other
                if isinstance(other, Compound)
                else NotImplemented)

    def __xor__(self, other: Compound) -> Compound:
        """
        Returns symmetric difference of the empty geometry
        with the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY ^ EMPTY is EMPTY
        True
        """
        return (other
                if isinstance(other, Compound)
                else NotImplemented)

    __rxor__ = __xor__

    @classmethod
    def from_raw(cls, raw: RawEmpty) -> Domain:
        """
        Constructs empty geometry from the combination of Python built-ins.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> Empty.from_raw(RAW_EMPTY) is EMPTY
        True
        """
        assert raw is RAW_EMPTY
        return cls()

    @property
    def centroid(self) -> NoReturn:
        raise ValueError('Empty geometry has no points.')

    def distance_to(self, other: Geometry) -> NoReturn:
        raise ValueError('Empty geometry has no points.')

    def locate(self, point: Point) -> Location:
        """
        Finds location of the point relative to the empty geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY.locate(Point(0, 0)) is Location.EXTERIOR
        True
        """
        return Location.EXTERIOR

    def raw(self) -> RawEmpty:
        """
        Returns the empty geometry as combination of Python built-ins.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY.raw()
        """
        return RAW_EMPTY

    def relate(self, other: Compound) -> Relation:
        """
        Finds relation between the empty geometry and the other geometry.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY.relate(EMPTY) is Relation.DISJOINT
        True
        """
        return Relation.DISJOINT

    def rotate(self,
               cosine: Coordinate,
               sine: Coordinate,
               point: Optional[Point] = None) -> 'Geometry':
        """
        Rotates the empty geometry by given cosine & sine around given point.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY.rotate(1, 0) is EMPTY.rotate(0, 1, Point(1, 1)) is EMPTY
        True
        """
        return self

    def scale(self,
              factor_x: Coordinate,
              factor_y: Optional[Coordinate] = None) -> 'Empty':
        """
        Scales the empty geometry by given factor.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY.scale(1) is EMPTY.scale(1, 2) is EMPTY
        True
        """
        return self

    def translate(self, step_x: Coordinate, step_y: Coordinate) -> 'Empty':
        """
        Translates the empty geometry by given step.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``

        >>> EMPTY.translate(1, 2) is EMPTY
        True
        """
        return self

    def validate(self) -> None:
        """
        Checks if the empty geometry is valid.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        """
        # empty geometry considered to be always valid


Maybe = Union[Empty, Domain]
EMPTY = Empty()
