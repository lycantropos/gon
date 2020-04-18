from abc import (ABC,
                 abstractmethod)
from typing import (Type,
                    TypeVar)

from orient.planar import Relation

from .hints import (Coordinate,
                    Domain)

RawGeometry = TypeVar('RawGeometry', tuple, list)


class Geometry(ABC):
    @abstractmethod
    def __eq__(self, other: 'Geometry') -> bool:
        """
        Checks if geometric objects are equal.
        """

    @abstractmethod
    def __hash__(self) -> int:
        """
        Returns hash of the geometric object.
        """

    @abstractmethod
    def __repr__(self) -> str:
        """
        Returns string representation of the geometric object.
        """

    @classmethod
    @abstractmethod
    def from_raw(cls: Type[Domain], raw: RawGeometry) -> Domain:
        """
        Constructs geometric object from combination of Python built-ins.
        """

    def disjoint(self, other: 'Geometry') -> bool:
        return self.relate(other) is Relation.DISJOINT

    @abstractmethod
    def raw(self) -> RawGeometry:
        """
        Returns geometric object as combination of Python built-ins.
        """

    @abstractmethod
    def relate(self, other: 'Geometry') -> Relation:
        """
        Finds relation between geometric objects.
        """

    @abstractmethod
    def validate(self) -> None:
        """
        Checks geometric object's constraints
        and raises error if any violation was found.
        """


class Compound(Geometry):
    @abstractmethod
    def __ge__(self, other: 'Geometry') -> bool:
        """
        Checks if the geometry is a superset of the other.
        """

    @abstractmethod
    def __gt__(self, other: 'Geometry') -> bool:
        """
        Checks if the geometry is a strict superset of the other.
        """

    @abstractmethod
    def __le__(self, other: 'Geometry') -> bool:
        """
        Checks if the geometry is a subset of the other.
        """

    @abstractmethod
    def __lt__(self, other: 'Geometry') -> bool:
        """
        Checks if the geometry is a strict subset of the other.
        """


class Linear(Compound):
    @property
    @abstractmethod
    def length(self) -> Coordinate:
        """
        Returns length of the geometry.
        """


class Shaped(Compound):
    def __ge__(self, other: 'Geometry') -> bool:
        """
        Checks if the geometry is a superset of the other.
        """
        return (self is other
                or (self.relate(other) in (Relation.EQUAL, Relation.COMPONENT,
                                           Relation.ENCLOSED, Relation.WITHIN)
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __gt__(self, other: 'Geometry') -> bool:
        """
        Checks if the geometry is a strict superset of the other.
        """
        return (self is not other
                and (self.relate(other) in (Relation.COMPONENT,
                                            Relation.ENCLOSED, Relation.WITHIN)
                     if isinstance(other, Compound)
                     else NotImplemented))

    def __le__(self, other: 'Geometry') -> bool:
        """
        Checks if the geometry is a subset of the other.
        """
        return (self is other
                or ((self.relate(other) in (Relation.COVER, Relation.ENCLOSES,
                                            Relation.COMPOSITE, Relation.EQUAL)
                     if isinstance(other, Shaped)
                     # shaped cannot be subset of linear
                     else False)
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __lt__(self, other: 'Geometry') -> bool:
        """
        Checks if the geometry is a strict subset of the other.
        """
        return (self is not other
                and ((self.relate(other) in (Relation.COVER,
                                             Relation.ENCLOSES,
                                             Relation.COMPOSITE)
                      if isinstance(other, Shaped)
                      # shaped cannot be strict subset of linear
                      else False)
                     if isinstance(other, Compound)
                     else NotImplemented))

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
