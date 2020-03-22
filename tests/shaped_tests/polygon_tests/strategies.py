from typing import Tuple

from hypothesis import strategies
from hypothesis_geometry import planar
from lz.functional import (identity,
                           pack)
from lz.iterating import mapper

from gon.base import Point
from gon.hints import Coordinate
from gon.shaped import (Polygon,
                        SimplePolygon,
                        to_polygon)
from tests.strategies import (scalars_strategies,
                              scalars_to_points,
                              triangular_contours)
from tests.utils import (Strategy,
                         cleave_in_tuples,
                         to_pairs,
                         to_triplets)

triangles = triangular_contours.map(to_polygon)


def scalars_to_polygons(scalars: Strategy[Coordinate]) -> Strategy[Polygon]:
    return (planar.contours(scalars)
            .map(mapper(pack(Point)))
            .map(list)
            .map(SimplePolygon))


polygons_strategies = scalars_strategies.map(scalars_to_polygons)
polygons = polygons_strategies.flatmap(identity)
polygons_pairs = polygons_strategies.flatmap(to_pairs)
polygons_triplets = polygons_strategies.flatmap(to_triplets)
non_polygons = strategies.builds(object)
polygons_with_points = (scalars_strategies
                        .flatmap(cleave_in_tuples(scalars_to_polygons,
                                                  scalars_to_points)))


def to_polygons_with_contours_indices(polygon: Polygon
                                      ) -> Strategy[Tuple[Polygon, int]]:
    indices = strategies.integers(min_value=0,
                                  max_value=len(polygon.contour))
    return strategies.tuples(strategies.just(polygon), indices)


polygons_with_contours_indices = (polygons
                                  .flatmap(to_polygons_with_contours_indices))
