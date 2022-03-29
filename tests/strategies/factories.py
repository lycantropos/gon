from functools import partial

from hypothesis import strategies
from hypothesis_geometry import planar

from gon.base import (Angle,
                      Linear,
                      Multipoint,
                      Shaped,
                      Vector)
from gon.hints import (Maybe,
                       Scalar)
from tests.utils import (Strategy,
                         call,
                         pack,
                         to_pairs,
                         to_triplets)

MAX_LINEAR_SIZE = 5


def to_non_zero_coordinates(coordinates: Strategy[Scalar]) -> Strategy[Scalar]:
    return coordinates.filter(bool)


def to_zero_coordinates(coordinates: Strategy[Scalar]) -> Strategy[Scalar]:
    return strategies.builds(call, coordinates.map(type))


empty_geometries = planar.empty_geometries()


def coordinates_to_angles(coordinates: Strategy[Scalar]
                          ) -> Strategy[Angle[Scalar]]:
    return (to_triplets(coordinates_to_points(coordinates))
            .map(pack(Angle.from_sides)))


coordinates_to_points = planar.points


def coordinates_to_maybe_multipoints(coordinates: Strategy[Scalar]
                                     ) -> Strategy[Maybe[Multipoint[Scalar]]]:
    return empty_geometries | coordinates_to_multipoints(coordinates)


def coordinates_to_maybe_linear_geometries(coordinates: Strategy[Scalar]
                                           ) -> Strategy[
    Maybe[Linear[Scalar]]]:
    return empty_geometries | coordinates_to_linear_geometries(coordinates)


def coordinates_to_maybe_shaped_geometries(
        coordinates: Strategy[Scalar]
) -> Strategy[Maybe[Shaped[Scalar]]]:
    return empty_geometries | coordinates_to_shaped_geometries(coordinates)


coordinates_to_multipoints = planar.multipoints


def coordinates_to_linear_geometries(coordinates: Strategy[Scalar]
                                     ) -> Strategy[Linear[Scalar]]:
    return (coordinates_to_segments(coordinates)
            | coordinates_to_multisegments(coordinates)
            | coordinates_to_contours(coordinates))


def coordinates_to_shaped_geometries(coordinates: Strategy[Scalar]
                                     ) -> Strategy[Shaped[Scalar]]:
    return (coordinates_to_polygons(coordinates)
            | coordinates_to_multipolygons(coordinates))


coordinates_to_segments = planar.segments
coordinates_to_multisegments = partial(planar.multisegments,
                                       max_size=MAX_LINEAR_SIZE)
coordinates_to_contours = partial(planar.contours,
                                  max_size=MAX_LINEAR_SIZE)
coordinates_to_mixes = partial(planar.mixes,
                               max_segments_size=MAX_LINEAR_SIZE)
coordinates_to_polygons = planar.polygons
coordinates_to_multipolygons = planar.multipolygons


def coordinates_to_vectors(coordinates: Strategy[Scalar]
                           ) -> Strategy[Vector[Scalar]]:
    return strategies.builds(pack(Vector),
                             to_pairs(coordinates_to_points(coordinates)))
