from functools import partial
from typing import Optional

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
from gon.raw import (RAW_EMPTY,
                     RawMix)
from tests.utils import (Strategy,
                         call,
                         pack)

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
    points = coordinates_to_points(coordinates)
    return strategies.builds(pack(Multipoint),
                             strategies.lists(points,
                                              min_size=1,
                                              unique=True))


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
    return planar.segments(coordinates).map(Segment.from_raw)


def coordinates_to_multisegments(coordinates: Strategy[Coordinate]
                                 ) -> Strategy[Multisegment]:
    return (planar.multisegments(coordinates,
                                 min_size=1,
                                 max_size=MAX_LINEAR_SIZE)
            .map(Multisegment.from_raw))


def coordinates_to_contours(coordinates: Strategy[Coordinate],
                            *,
                            min_size: int = planar.TRIANGULAR_CONTOUR_SIZE,
                            max_size: int = MAX_LINEAR_SIZE
                            ) -> Strategy[Contour]:
    return (planar.contours(coordinates,
                            min_size=min_size,
                            max_size=max_size)
            .map(Contour.from_raw))


def coordinates_to_mixes(coordinates: Strategy[Coordinate]) -> Strategy[Mix]:
    return coordinates_to_raw_mixes(coordinates).map(Mix.from_raw)


def coordinates_to_raw_mixes(coordinates: Strategy[Coordinate]
                             ) -> Strategy[RawMix]:
    def coordinate_to_raw_empty(index: int, raw_mix: RawMix) -> RawMix:
        return (raw_mix
                if raw_mix[index]
                else raw_mix[:index] + (RAW_EMPTY,) + raw_mix[index + 1:])

    return ((planar.mixes(coordinates,
                          min_multipoint_size=1,
                          min_multisegment_size=1)
             .map(partial(coordinate_to_raw_empty, 2)))
            | (planar.mixes(coordinates,
                            min_multipoint_size=1,
                            min_multipolygon_size=1)
               .map(partial(coordinate_to_raw_empty, 1)))
            | (planar.mixes(coordinates,
                            min_multisegment_size=1,
                            min_multipolygon_size=1)
               .map(partial(coordinate_to_raw_empty, 0))))


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
