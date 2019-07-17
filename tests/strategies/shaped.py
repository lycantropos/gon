from functools import partial
from operator import (attrgetter,
                      itemgetter)
from typing import (Sequence,
                    Tuple)

from hypothesis import strategies
from lz.functional import (compose,
                           pack)
from lz.logical import negate
from lz.replication import replicator

from gon.angular import (Angle,
                         Orientation)
from gon.base import (Point,
                      Vector)
from gon.hints import Scalar
from gon.linear import (Interval,
                        Segment)
from gon.shaped import (Polygon,
                        _to_non_neighbours,
                        self_intersects,
                        to_convex_hull,
                        to_edges,
                        vertices_forms_angles)
from tests.utils import Strategy
from .base import (points_strategies,
                   scalars_to_points)
from .linear import segment_to_scalars

to_triplets_strategy = compose(pack(strategies.tuples), replicator(3))
triangles_vertices = (points_strategies
                      .flatmap(to_triplets_strategy)
                      .filter(vertices_forms_angles))
to_non_triangle_vertices_base = partial(strategies.lists,
                                        min_size=4,
                                        unique_by=(attrgetter('x'),
                                                   attrgetter('y')))
invalid_vertices = points_strategies.flatmap(to_non_triangle_vertices_base)
invalid_vertices = (invalid_vertices.filter(self_intersects)
                    | invalid_vertices.filter(negate(vertices_forms_angles)))
triangles = (triangles_vertices
             .map(Polygon))


def to_convex_vertices(points: Strategy[Point]) -> Strategy[Sequence[Point]]:
    return (to_non_triangle_vertices_base(points)
            .map(to_convex_hull)
            .filter(lambda vertices: len(vertices) >= 3))


convex_polygons = (triangles
                   | (points_strategies
                      .flatmap(to_convex_vertices)
                      .map(Polygon)))


def to_concave_vertices(points: Strategy[Point]) -> Strategy[Sequence[Point]]:
    return (strategies.lists(points,
                             min_size=4,
                             unique_by=(attrgetter('x'), attrgetter('y')))
            .map(points_to_concave_vertices))


def points_to_concave_vertices(points: Sequence[Point]) -> Sequence[Point]:
    result = list(to_convex_hull(points))
    rest_points = [point for point in points if point not in result]
    for point in rest_points:
        edges = tuple(to_edges(result))

        def forms_angle_with_neighbours(indexed_edge: Tuple[int, Segment]
                                        ) -> bool:
            index, edge = indexed_edge
            point_start_segment = Segment(point, edge.start)
            point_end_segment = Segment(point, edge.end)
            prior_edge, next_edge = _to_neighbours(index, edges)
            return (point_start_segment.orientation_with(prior_edge.start)
                    != Orientation.COLLINEAR
                    and point_end_segment.orientation_with(prior_edge.end)
                    != Orientation.COLLINEAR
                    and point_start_segment.orientation_with(next_edge.start)
                    != Orientation.COLLINEAR
                    and point_end_segment.orientation_with(prior_edge.end)
                    != Orientation.COLLINEAR)

        def is_visible_edge(indexed_edge: Tuple[int, Segment]) -> bool:
            index, edge = indexed_edge
            point_start_segment = Segment(point, edge.start)
            point_end_segment = Segment(point, edge.end)
            prior_edge, next_edge = _to_neighbours(index, edges)
            prior_edge_interval = Interval(prior_edge.start,
                                           prior_edge.end,
                                           start_inclusive=True,
                                           end_inclusive=False)
            next_edge_interval = Interval(next_edge.start,
                                          next_edge.end,
                                          start_inclusive=False,
                                          end_inclusive=True)
            if (prior_edge_interval.intersects_with(point_start_segment)
                    or next_edge_interval.intersects_with(point_start_segment)
                    or prior_edge_interval.intersects_with(point_end_segment)
                    or next_edge_interval.intersects_with(point_end_segment)):
                return False
            non_neighbours_edges = _to_non_neighbours(index, edges)
            return not (any(point_start_segment.intersects_with(non_neighbour)
                            for non_neighbour in non_neighbours_edges)
                        or any(point_end_segment.intersects_with(non_neighbour)
                               for non_neighbour in non_neighbours_edges))

        indexed_edges = filter(forms_angle_with_neighbours, enumerate(edges))
        indexed_edges = filter(is_visible_edge, indexed_edges)
        try:
            indexed_edge = min(indexed_edges,
                               key=compose(partial(squared_distance_to_point,
                                                   point=point),
                                           itemgetter(1)))
        except ValueError:
            continue
        else:
            index, _ = indexed_edge
        result.insert(index + 1, point)
    return result


def _to_neighbours(index: int,
                   edges: Sequence[Segment]) -> Sequence[Segment]:
    return edges[index - 1], edges[(index + 1) % len(edges)]


def squared_distance_to_point(segment: Segment,
                              *,
                              point: Point) -> Scalar:
    if not (Angle(segment.start, point, segment.end).is_acute
            and Angle(segment.end, point, segment.start).is_acute):
        return min(point.squared_distance_to(segment.start),
                   point.squared_distance_to(segment.end))
    segment_vector = Vector.from_points(segment.start, segment.end)
    return ((segment_vector.y * point.x
             - segment_vector.x * point.y
             + segment.end.x * segment.start.y
             - segment.end.y * segment.start.x) ** 2
            / segment_vector.squared_length)


concave_polygons = (points_strategies
                    .flatmap(to_concave_vertices)
                    .map(Polygon)
                    .filter(lambda polygon: not polygon.is_convex))
polygons = concave_polygons | convex_polygons


def to_polygon_with_points(polygon: Polygon
                           ) -> Strategy[Tuple[Segment, Point]]:
    scalars = strategies.one_of(list(map(segment_to_scalars,
                                         to_edges(polygon.vertices))))
    return strategies.tuples(strategies.just(polygon),
                             scalars_to_points(scalars))


polygons_with_points = polygons.flatmap(to_polygon_with_points)
