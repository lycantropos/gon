from typing import Tuple

from hypothesis import strategies
from hypothesis_geometry import planar
from lz.functional import pack
from lz.iterating import mapper

from gon.base import Point
from gon.hints import Coordinate
from gon.shaped import (Polygon,
                        SimplePolygon,
                        to_polygon)
from tests.strategies import (coordinates_strategies,
                              coordinates_to_points,
                              triangular_contours)
from tests.utils import (Strategy,
                         cleave_in_tuples,
                         to_pairs,
                         to_triplets)

triangles = triangular_contours.map(to_polygon)


def coordinates_to_polygons(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Polygon]:
    return (planar.contours(coordinates)
            .map(mapper(pack(Point)))
            .map(list)
            .map(SimplePolygon))


polygons = coordinates_strategies.flatmap(coordinates_to_polygons)
polygons_strategies = coordinates_strategies.map(coordinates_to_polygons)
polygons_pairs = polygons_strategies.flatmap(to_pairs)
polygons_triplets = polygons_strategies.flatmap(to_triplets)
polygons_with_points = (coordinates_strategies
                        .flatmap(cleave_in_tuples(coordinates_to_polygons,
                                                  coordinates_to_points)))


def to_polygons_with_contours_indices(polygon: Polygon
                                      ) -> Strategy[Tuple[Polygon, int]]:
    indices = strategies.integers(min_value=0,
                                  max_value=len(polygon.contour))
    return strategies.tuples(strategies.just(polygon), indices)


polygons_with_contours_indices = (polygons
                                  .flatmap(to_polygons_with_contours_indices))
