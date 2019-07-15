from itertools import (product,
                       starmap)
from operator import (attrgetter,
                      methodcaller,
                      ne)
from typing import (Sequence,
                    Tuple)

from hypothesis import strategies
from lz.functional import (compose,
                           pack)
from lz.replication import (duplicate,
                            replicator)

from gon.base import (Orientation,
                      Point,
                      to_orientation)
from gon.hints import Scalar
from gon.shaped import (Polygon,
                        Segment,
                        to_convex_hull,
                        to_edges,
                        vertices_forms_angles)
from tests.utils import Strategy
from .base import (points_strategies,
                   scalars_strategies_factories,
                   scalars_to_points)

points_to_segments = compose(methodcaller(Strategy.map.__name__,
                                          pack(Segment)),
                             methodcaller(Strategy.filter.__name__,
                                          pack(ne)),
                             pack(strategies.tuples),
                             duplicate)
segments = points_strategies.flatmap(points_to_segments)


def to_segment_with_points(segment: Segment
                           ) -> Strategy[Tuple[Segment, Point]]:
    return strategies.tuples(strategies.just(segment),
                             scalars_to_points(segment_to_scalars(segment)))


def segment_to_scalars(segment: Segment) -> Strategy[Scalar]:
    coordinates = [segment.start.x, segment.start.y,
                   segment.end.x, segment.end.y]
    coordinates_type, = set(map(type, coordinates))
    strategy_factory = scalars_strategies_factories[coordinates_type]
    return strategy_factory(min_value=min(coordinates),
                            max_value=max(coordinates))


segments_with_points = segments.flatmap(to_segment_with_points)
segments_pairs = points_strategies.flatmap(compose(pack(strategies.tuples),
                                                   duplicate,
                                                   points_to_segments))

to_triplets_strategy = compose(pack(strategies.tuples), replicator(3))
triangles_vertices = (points_strategies
                      .flatmap(to_triplets_strategy)
                      .filter(vertices_forms_angles))
triangles = (triangles_vertices
             .map(Polygon))


def to_convex_vertices(points: Strategy[Point]) -> Strategy[Sequence[Point]]:
    return (strategies.lists(points,
                             min_size=4,
                             unique_by=(attrgetter('x'), attrgetter('y')))
            .filter(in_general_position)
            .map(to_convex_hull))


def in_general_position(points: Sequence[Point]) -> bool:
    return all(orientation != Orientation.COLLINEAR
               for orientation in starmap(to_orientation, product(points,
                                                                  repeat=3)))


convex_polygons = (triangles
                   | (points_strategies
                      .flatmap(to_convex_vertices)
                      .map(Polygon)))
# TODO: add concave polygons support
polygons = convex_polygons


def to_polygon_with_points(polygon: Polygon
                           ) -> Strategy[Tuple[Segment, Point]]:
    scalars = strategies.one_of(list(map(segment_to_scalars,
                                         to_edges(polygon.vertices))))
    return strategies.tuples(strategies.just(polygon),
                             scalars_to_points(scalars))


polygons_with_points = polygons.flatmap(to_polygon_with_points)
