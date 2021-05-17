from abc import (ABC,
                 abstractmethod)
from typing import (TYPE_CHECKING,
                    Optional)

from .hints import Scalar

if TYPE_CHECKING:
    from .point import Point


class Geometry(ABC):
    __slots__ = ()

    @abstractmethod
    def distance_to(self, other: 'Geometry') -> Scalar:
        """
        Returns distance between geometric objects.
        """

    @abstractmethod
    def rotate(self,
               cosine: Scalar,
               sine: Scalar,
               point: Optional['Point'] = None) -> 'Geometry':
        """
        Rotates geometric object by given cosine & sine around given point.
        """

    @abstractmethod
    def scale(self,
              factor_x: Scalar,
              factor_y: Optional[Scalar] = None) -> 'Geometry':
        """
        Scales geometric object by given factor.
        """

    @abstractmethod
    def translate(self, step_x: Scalar, step_y: Scalar) -> 'Geometry':
        """
        Translates geometric object by given step.
        """

    @abstractmethod
    def validate(self) -> None:
        """
        Checks geometric object's constraints
        and raises error if any violation was found.
        """
