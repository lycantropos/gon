from typing import (Optional,
                    Tuple)

from hypothesis import strategies
from hypothesis_geometry import planar

from gon.base import (EMPTY,
                      Contour,
                      Linear,
                      Mix,
                      Multipoint,
                      Multipolygon,
                      Multisegment,
                      Point,
                      Polygon,
                      Segment,
                      Shaped)
from gon.hints import (Coordinate,
                       Maybe)
from tests.utils import (Strategy,
                         call)

MAX_LINEAR_SIZE = 5


def to_non_zero_coordinates(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Coordinate]:
    return coordinates.filter(bool)


def to_zero_coordinates(coordinates: Strategy[Coordinate]
                        ) -> Strategy[Coordinate]:
    return strategies.builds(call, coordinates.map(type))


def coordinates_to_points(coordinates: Strategy[Coordinate]
                          ) -> Strategy[Point]:
    return strategies.builds(Point, coordinates, coordinates)


def coordinates_to_maybe_multipoints(coordinates: Strategy[Coordinate]
                                     ) -> Strategy[Maybe[Multipoint]]:
    return strategies.just(EMPTY) | coordinates_to_multipoints(coordinates)


def coordinates_to_maybe_linear_geometries(coordinates: Strategy[Coordinate]
                                           ) -> Strategy[Maybe[Linear]]:
    return (strategies.just(EMPTY)
            | coordinates_to_linear_geometries(coordinates))


def coordinates_to_maybe_shaped_geometries(coordinates: Strategy[Coordinate]
                                           ) -> Strategy[Maybe[Shaped]]:
    return (strategies.just(EMPTY)
            | coordinates_to_shaped_geometries(coordinates))


def coordinates_to_multipoints(coordinates: Strategy[Coordinate]
                               ) -> Strategy[Multipoint]:
    return planar.multipoints(coordinates,
                              min_size=1)


def coordinates_to_linear_geometries(coordinates: Strategy[Coordinate]
                                     ) -> Strategy[Linear]:
    return (coordinates_to_segments(coordinates)
            | coordinates_to_multisegments(coordinates)
            | coordinates_to_contours(coordinates))


def coordinates_to_shaped_geometries(coordinates: Strategy[Coordinate]
                                     ) -> Strategy[Shaped]:
    return (coordinates_to_polygons(coordinates)
            | coordinates_to_multipolygons(coordinates))


def coordinates_to_segments(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Segment]:
    return planar.segments(coordinates)


def coordinates_to_multisegments(coordinates: Strategy[Coordinate]
                                 ) -> Strategy[Multisegment]:
    return planar.multisegments(coordinates,
                                min_size=2,
                                max_size=MAX_LINEAR_SIZE)


def coordinates_to_contours(coordinates: Strategy[Coordinate],
                            *,
                            min_size: int = 3,
                            max_size: int = MAX_LINEAR_SIZE
                            ) -> Strategy[Contour]:
    return planar.contours(coordinates,
                           min_size=min_size,
                           max_size=max_size)


def coordinates_to_mixes(coordinates: Strategy[Coordinate]) -> Strategy[Mix]:
    def from_components(components
                        : Tuple[Multipoint, Multisegment, Multipolygon]
                        ) -> Mix:
        multipoint, multisegment, multipolygon = components
        return Mix(multipoint if multipoint.points else EMPTY,
                   multisegment if multisegment.segments else EMPTY,
                   multipolygon if multipolygon.polygons else EMPTY)

    return ((planar.mixes(coordinates,
                          min_multipoint_size=1,
                          min_multisegment_size=2)
             .map(from_components))
            | (planar.mixes(coordinates,
                            min_multipoint_size=1,
                            min_multipolygon_size=2)
               .map(from_components))
            | (planar.mixes(coordinates,
                            min_multisegment_size=1,
                            min_multipolygon_size=2)
               .map(from_components)))


def coordinates_to_polygons(coordinates: Strategy[Coordinate],
                            *,
                            min_size: int = 3,
                            max_size: Optional[int] = None,
                            min_holes_size: int = 0,
                            max_holes_size: Optional[int] = None,
                            min_hole_size: int = 3,
                            max_hole_size: Optional[int] = None
                            ) -> Strategy[Polygon]:
    return planar.polygons(coordinates,
                           min_size=min_size,
                           max_size=max_size,
                           min_holes_size=min_holes_size,
                           max_holes_size=max_holes_size,
                           min_hole_size=min_hole_size,
                           max_hole_size=max_hole_size)


def coordinates_to_multipolygons(coordinates: Strategy[Coordinate],
                                 *,
                                 min_size: int = 2,
                                 max_size: Optional[int] = None,
                                 min_border_size: int = 3,
                                 max_border_size: Optional[int] = None,
                                 min_holes_size: int = 0,
                                 max_holes_size: Optional[int] = None,
                                 min_hole_size: int = 3,
                                 max_hole_size: Optional[int] = None
                                 ) -> Strategy[Multipolygon]:
    return planar.multipolygons(coordinates,
                                min_size=min_size,
                                max_size=max_size,
                                min_border_size=min_border_size,
                                max_border_size=max_border_size,
                                min_holes_size=min_holes_size,
                                max_holes_size=max_holes_size,
                                min_hole_size=min_hole_size,
                                max_hole_size=max_hole_size)
