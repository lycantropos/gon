from typing import Tuple

from hypothesis import strategies
from hypothesis_geometry import planar
from lz.functional import (identity,
                           pack)
from lz.iterating import mapper

from gon.base import Point
from gon.hints import Scalar
from gon.shaped import (Polygon,
                        SimplePolygon,
                        to_polygon)
from tests.strategies import (scalars_strategies,
                              scalars_to_points,
                              triangles_vertices)
from tests.utils import (Strategy,
                         cleave_in_tuples,
                         to_pairs,
                         to_triplets)

triangles = triangles_vertices.map(to_polygon)


def to_tailed_triangles(scale: int) -> Polygon:
    """Creates specific polygon that increases triangulation code coverage."""
    return to_polygon([Point(0, 0), Point(scale, 0), Point(3 * scale, -scale),
                       Point(4 * scale, scale),
                       Point(2 * scale, 0), Point(scale, 100 * scale)])


def scalars_to_polygons(scalars: Strategy[Scalar]) -> Strategy[Polygon]:
    return (strategies.integers().filter(bool).map(to_tailed_triangles)
            | (planar.contours(scalars)
               .map(mapper(pack(Point)))
               .map(list)
               .map(SimplePolygon)))


polygons_strategies = scalars_strategies.map(scalars_to_polygons)
polygons = polygons_strategies.flatmap(identity)
polygons_pairs = polygons_strategies.flatmap(to_pairs)
polygons_triplets = polygons_strategies.flatmap(to_triplets)
non_polygons = strategies.builds(object)
polygons_with_points = (scalars_strategies
                        .flatmap(cleave_in_tuples(scalars_to_polygons,
                                                  scalars_to_points)))


def to_polygon_with_vertices_indices(polygon: Polygon
                                     ) -> Strategy[Tuple[Polygon, int]]:
    indices = strategies.integers(min_value=0,
                                  max_value=len(polygon.vertices))
    return strategies.tuples(strategies.just(polygon), indices)


polygons_with_vertices_indices = (polygons
                                  .flatmap(to_polygon_with_vertices_indices))
