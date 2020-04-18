from abc import abstractmethod

from .geometry import Geometry


class Oriented(Geometry):
    @abstractmethod
    def reverse(self) -> 'Oriented':
        """
        Returns the geometry reversed.
        """
