from operator import (methodcaller,
                      ne)
from typing import (Sequence,
                    Tuple)

from hypothesis import strategies
from lz.functional import (compose,
                           pack)
from lz.replication import (duplicate,
                            replicator)

from gon.base import Point
from gon.shaped import (Polygon,
                        Segment,
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
    coordinates = [segment.start.x, segment.start.y,
                   segment.end.x, segment.end.y]
    coordinates_type, = set(map(type, coordinates))
    scalars = scalars_strategies_factories[coordinates_type](
            min_value=min(coordinates),
            max_value=max(coordinates))
    return strategies.tuples(strategies.just(segment),
                             scalars_to_points(scalars))


segments_with_points = segments.flatmap(to_segment_with_points)
segments_pairs = points_strategies.flatmap(compose(pack(strategies.tuples),
                                                   duplicate,
                                                   points_to_segments))

to_triangles_vertices = compose(pack(strategies.tuples), replicator(3))
triangles_vertices = (points_strategies
                      .flatmap(to_triangles_vertices)
                      .filter(vertices_forms_angles))
triangles = (triangles_vertices
             .map(Polygon))


def to_vertices(points: Strategy[Point]) -> Strategy[Sequence[Point]]:
    return (to_triangles_vertices(points)
            .filter(vertices_forms_angles))


polygons = (points_strategies
            .flatmap(to_vertices)
            .map(Polygon))
