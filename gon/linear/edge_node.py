from typing import Union

from locus import kd

from gon.hints import Coordinate
from gon.primitive import RawPoint
from .hints import RawContour
from .utils import squared_raw_segment_point_distance


class EdgeNode(kd.Node):
    """
    Custom kd-tree node class for searching contour edge
    which is the nearest to point.
    """
    __slots__ = '_edge_start',

    def __init__(self,
                 contour: RawContour,
                 index: int,
                 point: RawPoint,
                 axis: int,
                 left: Union['EdgeNode', kd.NIL],
                 right: Union['EdgeNode', kd.NIL]) -> None:
        super().__init__(index, point, axis, left, right)
        self._edge_start = contour[index - 1]

    def distance_to_coordinate(self, coordinate: Coordinate) -> Coordinate:
        start_coordinate, end_coordinate = (self._edge_start[self.axis],
                                            self.coordinate)
        return ((start_coordinate - coordinate) ** 2
                if coordinate < start_coordinate
                else ((coordinate - end_coordinate) ** 2
                      if end_coordinate < coordinate
                      else 0))

    def distance_to_point(self, point: RawPoint) -> Coordinate:
        return squared_raw_segment_point_distance(self._edge_start,
                                                  self.point, point)
