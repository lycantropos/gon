from abc import (ABC,
                 abstractmethod)
from typing import (TYPE_CHECKING,
                    Optional,
                    Type,
                    TypeVar)

from .hints import (Coordinate,
                    Domain)

if TYPE_CHECKING:
    from .primitive import Point

RawGeometry = TypeVar('RawGeometry', None, tuple, list)


class Geometry(ABC):
    __slots__ = ()

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

    @abstractmethod
    def distance_to(self, other: 'Geometry') -> Coordinate:
        """
        Returns distance between geometric objects.
        """

    @abstractmethod
    def raw(self) -> RawGeometry:
        """
        Returns geometric object as combination of Python built-ins.
        """

    @abstractmethod
    def rotate(self,
               cosine: Coordinate,
               sine: Coordinate,
               point: Optional['Point'] = None) -> 'Geometry':
        """
        Rotates geometric object by given cosine & sine around given point.
        """

    @abstractmethod
    def scale(self,
              factor_x: Coordinate,
              factor_y: Optional[Coordinate] = None) -> 'Geometry':
        """
        Scales geometric object by given factor.
        """

    @abstractmethod
    def translate(self, step_x: Coordinate, step_y: Coordinate) -> 'Geometry':
        """
        Translates geometric object by given step.
        """

    @abstractmethod
    def validate(self) -> None:
        """
        Checks geometric object's constraints
        and raises error if any violation was found.
        """
