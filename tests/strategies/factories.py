from typing import Optional

from hypothesis import strategies
from hypothesis_geometry import planar

from gon.hints import Coordinate
from gon.linear import (Loop,
                        Segment)
from gon.primitive import Point
from gon.shaped import Polygon
from tests.utils import Strategy


def coordinates_to_points(coordinates: Strategy[Coordinate]
                          ) -> Strategy[Point]:
    return strategies.builds(Point, coordinates, coordinates)


def coordinates_to_segments(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Segment]:
    return planar.segments(coordinates).map(Segment.from_raw)


def coordinates_to_loops(coordinates: Strategy[Coordinate],
                         *,
                         min_size: int = planar.TRIANGULAR_CONTOUR_SIZE,
                         max_size: Optional[int] = None
                         ) -> Strategy[Loop]:
    return (planar.contours(coordinates,
                            min_size=min_size,
                            max_size=max_size)
            .map(Loop.from_raw))


def coordinates_to_polygons(coordinates: Strategy[Coordinate],
                            min_size: int = planar.TRIANGULAR_CONTOUR_SIZE,
                            max_size: Optional[int] = None,
                            min_holes_size: int
                            = planar.EMPTY_MULTICONTOUR_SIZE,
                            max_holes_size: Optional[int] = None,
                            min_hole_size: int
                            = planar.TRIANGULAR_CONTOUR_SIZE,
                            max_hole_size: Optional[int] = None
                            ) -> Strategy[Polygon]:
    return (planar.polygons(coordinates,
                            min_size=min_size,
                            max_size=max_size,
                            min_holes_size=min_holes_size,
                            max_holes_size=max_holes_size,
                            min_hole_size=min_hole_size,
                            max_hole_size=max_hole_size)
            .map(Polygon.from_raw))
