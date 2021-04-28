from abc import (ABC,
                 abstractmethod)
from typing import (TYPE_CHECKING,
                    Optional)

from symba.base import Expression

from .hints import Coordinate

if TYPE_CHECKING:
    from .primitive import Point


class Geometry(ABC):
    __slots__ = ()

    @abstractmethod
    def distance_to(self, other: 'Geometry') -> Expression:
        """
        Returns distance between geometric objects.
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
