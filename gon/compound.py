from abc import abstractmethod

from orient.planar import Relation

from .geometry import Geometry
from .hints import Coordinate

Relation = Relation


class Compound(Geometry):
    @abstractmethod
    def __contains__(self, other: 'Geometry') -> bool:
        """
        Checks if the geometry contains the other.
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

    def disjoint(self, other: 'Compound') -> bool:
        """
        Checks if the geometry is disjoint with the other.
        """
        return self.relate(other) is Relation.DISJOINT

    @abstractmethod
    def relate(self, other: 'Compound') -> Relation:
        """
        Finds relation between geometric objects.
        """


class Linear(Geometry):
    @property
    @abstractmethod
    def length(self) -> Coordinate:
        """
        Returns length of the geometry.
        """


class Shaped(Geometry):
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
    @abstractmethod
    def index(self) -> None:
        """
        Pre-processes geometry to potentially improve queries time complexity.
        """
