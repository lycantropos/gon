from abc import abstractmethod

from ground.base import (Location,
                         Relation)
from ground.hints import (Point,
                          Scalar)

from .geometry import Geometry

Relation = Relation
Location = Location


class Compound(Geometry[Scalar]):
    __slots__ = ()

    @property
    @abstractmethod
    def centroid(self) -> Point[Scalar]:
        """
        Returns centroid of the geometry.
        """

    def disjoint(self, other: 'Compound[Scalar]') -> bool:
        """
        Checks if the geometry is disjoint from the other.
        """
        return self.relate(other) is Relation.DISJOINT

    @abstractmethod
    def locate(self, point: Point[Scalar]) -> Location:
        """
        Finds location of point relative to the geometry.
        """

    @abstractmethod
    def relate(self, other: 'Compound[Scalar]') -> Relation:
        """
        Finds relation between geometric objects.
        """

    @abstractmethod
    def __and__(self, other: 'Compound[Scalar]') -> 'Compound[Scalar]':
        """
        Returns intersection of the geometry with the other geometry.
        """

    @abstractmethod
    def __contains__(self, point: Point[Scalar]) -> bool:
        """
        Checks if the geometry contains the point.
        """

    @abstractmethod
    def __ge__(self, other: 'Compound[Scalar]') -> bool:
        """
        Checks if the geometry is a superset of the other.
        """

    @abstractmethod
    def __gt__(self, other: 'Compound[Scalar]') -> bool:
        """
        Checks if the geometry is a strict superset of the other.
        """

    @abstractmethod
    def __le__(self, other: 'Compound[Scalar]') -> bool:
        """
        Checks if the geometry is a subset of the other.
        """

    @abstractmethod
    def __lt__(self, other: 'Compound[Scalar]') -> bool:
        """
        Checks if the geometry is a strict subset of the other.
        """

    @abstractmethod
    def __or__(self, other: 'Compound[Scalar]') -> 'Compound[Scalar]':
        """
        Returns union of the geometry with the other geometry.
        """

    @abstractmethod
    def __sub__(self, other: 'Compound[Scalar]') -> 'Compound[Scalar]':
        """
        Returns difference of the geometry with the other geometry.
        """

    @abstractmethod
    def __xor__(self, other: 'Compound[Scalar]') -> 'Compound[Scalar]':
        """
        Returns symmetric difference of the geometry with the other geometry.
        """


class Linear(Geometry[Scalar]):
    __slots__ = ()

    @property
    @abstractmethod
    def length(self) -> Scalar:
        """
        Returns length of the geometry.
        """


class Shaped(Geometry[Scalar]):
    __slots__ = ()

    @property
    @abstractmethod
    def area(self) -> Scalar:
        """
        Returns area of the geometry.
        """

    @property
    @abstractmethod
    def perimeter(self) -> Scalar:
        """
        Returns perimeter of the geometry.
        """


class Indexable(Compound[Scalar]):
    __slots__ = ()

    @abstractmethod
    def index(self) -> None:
        """
        Pre-processes geometry to potentially improve queries.
        """
