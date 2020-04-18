from abc import abstractmethod

from .angular import Orientation
from .geometry import Geometry


class Oriented(Geometry):
    @property
    @abstractmethod
    def orientation(self) -> Orientation:
        """
        Returns orientation of the geometry.
        """
