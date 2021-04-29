from abc import abstractmethod

from ground.base import Relation
from sect.decomposition import Location

from .geometry import Geometry
from .hints import Coordinate
from .point import Point

Relation = Relation
Location = Location


class Compound(Geometry):
    __slots__ = ()

    @property
    @abstractmethod
    def centroid(self) -> Point:
        """
        Returns centroid of the geometry.
        """

    def disjoint(self, other: 'Compound') -> bool:
        """
        Checks if the geometry is disjoint from the other.
        """
        return self.relate(other) is Relation.DISJOINT

    @abstractmethod
    def locate(self, point: Point) -> Location:
        """
        Finds location of point relative to the geometry.
        """

    @abstractmethod
    def relate(self, other: 'Compound') -> Relation:
        """
        Finds relation between geometric objects.
        """

    @abstractmethod
    def __and__(self, other: 'Compound') -> 'Compound':
        """
        Returns intersection of the geometry with the other geometry.
        """

    @abstractmethod
    def __contains__(self, point: Point) -> bool:
        """
        Checks if the geometry contains the point.
        """

    @abstractmethod
    def __ge__(self, other: 'Compound') -> bool:
        """
        Checks if the geometry is a superset of the other.
        """

    @abstractmethod
    def __gt__(self, other: 'Compound') -> bool:
        """
        Checks if the geometry is a strict superset of the other.
        """

    @abstractmethod
    def __le__(self, other: 'Compound') -> bool:
        """
        Checks if the geometry is a subset of the other.
        """

    @abstractmethod
    def __lt__(self, other: 'Compound') -> bool:
        """
        Checks if the geometry is a strict subset of the other.
        """

    @abstractmethod
    def __or__(self, other: 'Compound') -> 'Compound':
        """
        Returns union of the geometry with the other geometry.
        """

    @abstractmethod
    def __sub__(self, other: 'Compound') -> 'Compound':
        """
        Returns difference of the geometry with the other geometry.
        """

    @abstractmethod
    def __xor__(self, other: 'Compound') -> 'Compound':
        """
        Returns symmetric difference of the geometry with the other geometry.
        """


class Linear(Geometry):
    __slots__ = ()

    @property
    @abstractmethod
    def length(self) -> Coordinate:
        """
        Returns length of the geometry.
        """


class Shaped(Geometry):
    __slots__ = ()

    @property
    @abstractmethod
    def area(self) -> Coordinate:
        """
        Returns area of the geometry.
        """

    @property
    @abstractmethod
    def perimeter(self) -> Coordinate:
        """
        Returns perimeter of the geometry.
        """


class Indexable(Compound):
    __slots__ = ()

    @abstractmethod
    def index(self) -> None:
        """
        Pre-processes geometry to potentially improve queries.
        """
