from functools import partial
from operator import (attrgetter,
                      itemgetter)
from typing import (Sequence,
                    Tuple)

from hypothesis import strategies
from lz.functional import compose
from lz.logical import negate

from gon.angular import (Angle,
                         Orientation)
from gon.base import (Point,
                      Vector)
from gon.hints import Scalar
from gon.linear import (Segment,
                        to_interval,
                        to_segment)
from gon.shaped import (Polygon,
                        _to_non_neighbours,
                        _vertices_forms_convex_polygon,
                        to_convex_hull,
                        to_edges,
                        to_polygon,
                        vertices_forms_angles)
from tests.strategies import (points_strategies,
                              scalars_to_points,
                              segment_to_scalars,
                              to_non_triangle_vertices_base,
                              triangles_vertices)
from tests.utils import Strategy

triangles = triangles_vertices.map(to_polygon)


def to_convex_vertices(points: Strategy[Point]) -> Strategy[Sequence[Point]]:
    return (to_non_triangle_vertices_base(points)
            .map(to_convex_hull)
            .filter(lambda vertices: len(vertices) >= 3))


convex_vertices = (triangles_vertices
                   | points_strategies.flatmap(to_convex_vertices))


def to_concave_vertices(points: Strategy[Point]) -> Strategy[Sequence[Point]]:
    return (strategies.lists(points,
                             min_size=4,
                             unique_by=(attrgetter('x'), attrgetter('y')))
            .map(split_by_convex_hull)
            .filter(itemgetter(1))
            .map(combine_vertices)
            .filter(itemgetter(1))
            .map(itemgetter(0))
            .filter(vertices_forms_angles))


def split_by_convex_hull(points: Sequence[Point]
                         ) -> Tuple[Sequence[Point], Sequence[Point]]:
    convex_hull = to_convex_hull(points)
    rest_points = [point for point in points if point not in convex_hull]
    return convex_hull, rest_points


def combine_vertices(convex_hull_rest_points: Tuple[Sequence[Point],
                                                    Sequence[Point]]
                     ) -> Tuple[Sequence[Point], int]:
    result, rest_points = convex_hull_rest_points
    inserted_points_count = 0
    for point in rest_points:
        edges = tuple(to_edges(result))

        def forms_angle_with_neighbours(indexed_edge: Tuple[int, Segment]
                                        ) -> bool:
            index, edge = indexed_edge
            point_start_segment = to_segment(point, edge.start)
            point_end_segment = to_segment(point, edge.end)
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
            point_start_segment = to_segment(point, edge.start)
            point_end_segment = to_segment(point, edge.end)
            prior_edge, next_edge = _to_neighbours(index, edges)
            prior_edge_interval = to_interval(prior_edge.start,
                                              prior_edge.end,
                                              start_inclusive=True,
                                              end_inclusive=False)
            next_edge_interval = to_interval(next_edge.start,
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
        inserted_points_count += 1
    return result, inserted_points_count


def _to_neighbours(index: int,
                   edges: Sequence[Segment]) -> Sequence[Segment]:
    return edges[index - 1], edges[(index + 1) % len(edges)]


def squared_distance_to_point(segment: Segment,
                              *,
                              point: Point) -> Scalar:
    if not (Angle(point, segment.start, segment.end).is_acute
            and Angle(point, segment.end, segment.start).is_acute):
        return min(point.squared_distance_to(segment.start),
                   point.squared_distance_to(segment.end))
    segment_vector = Vector.from_points(segment.start, segment.end)
    return ((segment_vector.y * point.x
             - segment_vector.x * point.y
             + segment.end.x * segment.start.y
             - segment.end.y * segment.start.x) ** 2
            / segment_vector.squared_length)


concave_vertices = (points_strategies.flatmap(to_concave_vertices)
                    .filter(negate(_vertices_forms_convex_polygon)))
vertices = convex_vertices | concave_vertices
polygons = vertices.map(to_polygon)


def to_polygon_with_points(polygon: Polygon
                           ) -> Strategy[Tuple[Polygon, Point]]:
    scalars = strategies.one_of(list(map(segment_to_scalars,
                                         to_edges(polygon.vertices))))
    return strategies.tuples(strategies.just(polygon),
                             scalars_to_points(scalars))


polygons_with_points = polygons.flatmap(to_polygon_with_points)


def to_polygon_with_vertices_indices(polygon: Polygon
                                     ) -> Strategy[Tuple[Polygon, int]]:
    indices = strategies.integers(min_value=0,
                                  max_value=len(polygon.vertices))
    return strategies.tuples(strategies.just(polygon), indices)


polygons_with_vertices_indices = (polygons
                                  .flatmap(to_polygon_with_vertices_indices))
