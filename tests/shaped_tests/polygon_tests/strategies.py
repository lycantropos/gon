from collections import defaultdict
from operator import attrgetter
from typing import (Sequence,
                    Set,
                    Tuple)

from hypothesis import strategies
from lz.iterating import flatten
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
    triangulation = triangular.delaunay(points)
    points_triangles = triangular._to_points_triangles(triangulation)
    boundary = triangular._to_boundary(triangulation)
    boundary_points = set(flatten((edge.start, edge.end) for edge in boundary))

    def is_mouth(triangle_vertices: Vertices) -> bool:
        return (sum(vertex in boundary_points
                    for vertex in triangle_vertices) == 2
                and sum(edge in boundary
                        for edge in to_edges(triangle_vertices)) == 1)

    mouths = {index: triangle
              for index, triangle in enumerate(triangulation)
              if is_mouth(triangle)}
    neighbourhood = triangular._to_neighbourhood(
            triangulation,
            adjacency=triangular._to_adjacency(triangulation))
    for _ in range(len(points) - len(boundary)):
        try:
            index, triangle_vertices = mouths.popitem()
        except KeyError:
            break
        mouth_vertex = next(vertex
                            for vertex in triangle_vertices
                            if vertex not in boundary_points)
        edges = set(to_edges(triangle_vertices))
        boundary_points.update(triangle_vertices)
        boundary.symmetric_difference_update(edges)
        for connected in points_triangles[mouth_vertex]:
            connected_triangle_vertices = triangulation[connected]
            if is_mouth(connected_triangle_vertices):
                mouths[connected] = concave_vertices
            else:
                mouths.pop(connected, None)
            for vertex in set(connected_triangle_vertices) - {mouth_vertex}:
                points_triangles[vertex].discard(index)
        for neighbour in neighbourhood[index]:
            neighbour_vertices = triangulation[neighbour]
            if is_mouth(neighbour_vertices):
                mouths[neighbour] = neighbour_vertices
            else:
                mouths.pop(neighbour, None)
            neighbourhood[neighbour].remove(index)
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
