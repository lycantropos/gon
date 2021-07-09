from abc import (ABC,
                 abstractmethod)
from numbers import Real
from typing import (Generic,
                    Optional,
                    TypeVar)

from ground.base import Context
from ground.hints import (Point,
                          Scalar)
from symba.base import Expression

from .angle import Angle

Coordinate = TypeVar('Coordinate', Real, Expression)


class Geometry(Generic[Coordinate], ABC):
    __slots__ = ()

    @abstractmethod
    def distance_to(self, other: 'Geometry') -> Scalar:
        """
        Returns distance between geometric objects.
        """

    @abstractmethod
    def rotate(self,
               angle: Angle,
               point: Optional[Point[Coordinate]] = None
               ) -> 'Geometry[Coordinate]':
        """
        Rotates geometric object by given angle around given point.
        """

    @abstractmethod
    def scale(self,
              factor_x: Coordinate,
              factor_y: Optional[Coordinate] = None) -> 'Geometry[Coordinate]':
        """
        Scales geometric object by given factor.
        """

    @abstractmethod
    def translate(self,
                  step_x: Coordinate,
                  step_y: Coordinate) -> 'Geometry[Coordinate]':
        """
        Translates geometric object by given step.
        """

    @abstractmethod
    def validate(self) -> None:
        """
        Checks geometric object's constraints
        and raises error if any violation was found.
        """

    _context = ...  # type: Context
