from abc import (ABC,
                 abstractmethod)
from typing import (Generic,
                    Optional,
                    TypeVar)

from ground.base import Context
from ground.hints import (Point,
                          Scalar)

from .angle import Angle

_T = TypeVar('_T')


class Geometry(Generic[Scalar], ABC):
    __slots__ = ()

    @abstractmethod
    def distance_to(self, other: 'Geometry[Scalar]') -> Scalar:
        """
        Returns distance between geometric objects.
        """

    @abstractmethod
    def rotate(self: _T,
               angle: Angle[Scalar],
               point: Optional[Point[Scalar]] = None) -> _T:
        """
        Rotates geometric object by given angle around given point.
        """

    @abstractmethod
    def scale(self,
              factor_x: Scalar,
              factor_y: Optional[Scalar] = None) -> 'Geometry[Scalar]':
        """
        Scales geometric object by given factor.
        """

    @abstractmethod
    def translate(self: _T, step_x: Scalar, step_y: Scalar) -> _T:
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
