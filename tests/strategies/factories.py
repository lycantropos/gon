from typing import Optional

from hypothesis import strategies
from hypothesis_geometry import planar

from gon.discrete import Multipoint
from gon.hints import Coordinate
from gon.linear import (Contour,
                        Multisegment,
                        Segment)
from gon.primitive import Point
from gon.shaped import (Multipolygon,
                        Polygon)
from tests.utils import (Strategy,
                         pack)


def coordinates_to_points(coordinates: Strategy[Coordinate]
                          ) -> Strategy[Point]:
    return strategies.builds(Point, coordinates, coordinates)


def coordinates_to_multipoints(coordinates: Strategy[Coordinate]
                               ) -> Strategy[Multipoint]:
    points = coordinates_to_points(coordinates)
    return strategies.builds(pack(Multipoint),
                             strategies.lists(points,
                                              min_size=1,
                                              unique=True))


def coordinates_to_segments(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Segment]:
    return planar.segments(coordinates).map(Segment.from_raw)


def coordinates_to_multisegments(coordinates: Strategy[Coordinate]
                                 ) -> Strategy[Multisegment]:
    return planar.multisegments(coordinates,
                                min_size=1).map(Multisegment.from_raw)


def coordinates_to_contours(coordinates: Strategy[Coordinate],
                            *,
                            min_size: int = planar.TRIANGULAR_CONTOUR_SIZE,
                            max_size: Optional[int] = None
                            ) -> Strategy[Contour]:
    return (planar.contours(coordinates,
                            min_size=min_size,
                            max_size=max_size)
            .map(Contour.from_raw))


def coordinates_to_polygons(coordinates: Strategy[Coordinate],
                            *,
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


def coordinates_to_multipolygons(coordinates: Strategy[Coordinate],
                                 *,
                                 min_size: int = 1,
                                 max_size: Optional[int] = None,
                                 min_border_size: int
                                 = planar.TRIANGULAR_CONTOUR_SIZE,
                                 max_border_size: Optional[int] = None,
                                 min_holes_size: int
                                 = planar.EMPTY_MULTICONTOUR_SIZE,
                                 max_holes_size: Optional[int] = None,
                                 min_hole_size: int
                                 = planar.TRIANGULAR_CONTOUR_SIZE,
                                 max_hole_size: Optional[int] = None
                                 ) -> Strategy[Multipolygon]:
    return (planar.multipolygons(coordinates,
                                 min_size=min_size,
                                 max_size=max_size,
                                 min_border_size=min_border_size,
                                 max_border_size=max_border_size,
                                 min_holes_size=min_holes_size,
                                 max_holes_size=max_holes_size,
                                 min_hole_size=min_hole_size,
                                 max_hole_size=max_hole_size)
            .map(Multipolygon.from_raw))
