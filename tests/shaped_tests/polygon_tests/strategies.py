from collections import defaultdict
from operator import attrgetter
from typing import (Sequence,
                    Set,
                    Tuple)

from hypothesis import strategies
from lz.iterating import (first,
                          flatten)
from lz.logical import negate

from gon.angular import (Angle,
                         Orientation)
from gon.base import (Point,
                      Vector)
from gon.hints import Scalar
from gon.linear import (Segment,
                        to_segment)
from gon.shaped import (Polygon,
                        to_polygon,
                        triangular)
from gon.shaped.contracts import (self_intersects,
                                  vertices_forms_convex_polygon,
                                  vertices_forms_strict_polygon)
from gon.shaped.hints import Vertices
from gon.shaped.utils import (to_convex_hull,
                              to_edges)
from tests.strategies import (points_strategies,
                              scalars_to_points,
                              segment_to_scalars,
                              to_non_triangle_vertices_base,
                              triangles_vertices)
from tests.utils import Strategy

triangles = triangles_vertices.map(to_polygon)


def to_convex_vertices(points: Strategy[Point]) -> Strategy[Vertices]:
    return (to_non_triangle_vertices_base(points)
            .map(to_convex_hull)
            .filter(lambda vertices: len(vertices) >= 3))


convex_vertices = (triangles_vertices
                   | points_strategies.flatmap(to_convex_vertices))


def to_concave_vertices(points: Strategy[Point]) -> Strategy[Vertices]:
    return (strategies.lists(points,
                             min_size=4,
                             unique_by=(attrgetter('x'), attrgetter('y')))
            .map(points_to_concave_vertices)
            .filter(bool)
            .filter(vertices_forms_strict_polygon)
            .filter(negate(vertices_forms_convex_polygon)))


def points_to_concave_vertices(points: Sequence[Point]) -> Vertices:
    triangulation = triangular._delaunay(points)
    boundary = set(triangulation.boundary)
    boundary_points = set(flatten((edge.start, edge.end) for edge in boundary))
    adjacency = {edge: triangulation.to_non_adjacent_vertices(edge)
                 for edge in triangulation.edges}
    reversed_adjacency = defaultdict(set)
    for edge, non_adjacent_vertices in adjacency.items():
        for vertex in non_adjacent_vertices:
            reversed_adjacency[vertex].add(edge)

    def is_mouth(edge: Segment) -> bool:
        return _is_mouth(triangulation.to_non_adjacent_vertices(edge))

    def _is_mouth(non_adjacent_vertices: Set[Point]) -> bool:
        return (len(non_adjacent_vertices) == 1
                and not (non_adjacent_vertices & boundary_points))

    mouths = {edge: first(non_adjacent_vertices)
              for edge, non_adjacent_vertices in adjacency.items()
              if _is_mouth(non_adjacent_vertices)}
    for _ in range(len(points) - len(boundary)):
        try:
            edge, non_adjacent_vertex = mouths.popitem()
        except KeyError:
            break
        triangulation.remove(edge)
        boundary.remove(edge)
        new_boundary_edges = (to_segment(edge.start, non_adjacent_vertex),
                              to_segment(non_adjacent_vertex, edge.end))
        boundary.update(new_boundary_edges)
        boundary_points.add(non_adjacent_vertex)
        mouths.update((edge,
                       first(triangulation.to_non_adjacent_vertices(edge)))
                      for edge in new_boundary_edges
                      if is_mouth(edge))
        for edge in reversed_adjacency[non_adjacent_vertex]:
            mouths.pop(edge, None)
    return boundary_to_vertices(boundary)


def shrink_collinear_vertices(vertices: Vertices) -> Vertices:
    result = []
    for index, vertex in enumerate(vertices):
        angle = Angle(vertices[index - 1], vertex,
                      vertices[(index + 1) % len(vertices)])
        if angle.orientation is Orientation.COLLINEAR:
            continue
        result.append(vertex)
    return result


def boundary_to_vertices(boundary: Set[Segment]) -> Vertices:
    connectivity = defaultdict(dict)
    for edge in boundary:
        connectivity[edge.start][edge.end] = edge
        connectivity[edge.end][edge.start] = to_segment(edge.end, edge.start)
    edge = min(boundary,
               key=lambda edge: min(edge.start.x, edge.end.x))
    result = [edge.start]
    for _ in range(len(boundary) - 1):
        edge = next(candidate
                    for endpoint, candidate in connectivity[edge.end].items()
                    if endpoint != edge.start)
        result.append(edge.start)
    return shrink_collinear_vertices(result)


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
                    .filter(negate(self_intersects)))
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
