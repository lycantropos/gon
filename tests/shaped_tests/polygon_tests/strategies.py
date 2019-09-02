from collections import defaultdict
from typing import (Sequence,
                    Set,
                    Tuple)

from hypothesis import strategies
from lz.iterating import first
from lz.logical import negate

from gon.angular import (Angle,
                         Orientation)
from gon.base import Point
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
from tests.utils import (Strategy,
                         points_do_not_lie_on_the_same_line,
                         unique_everseen)

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
                             unique=True)
            .filter(points_do_not_lie_on_the_same_line)
            .map(points_to_concave_vertices)
            .filter(bool)
            .filter(vertices_forms_strict_polygon)
            .filter(negate(vertices_forms_convex_polygon)))


def points_to_concave_vertices(points: Sequence[Point]) -> Vertices:
    triangulation = triangular._delaunay(points)
    boundary = triangulation.to_boundary_edges()

    def is_mouth(edge: triangular.QuadEdge) -> bool:
        neighbours = triangulation.to_neighbours(edge)
        return len(neighbours) == 2 and not (neighbours & boundary)

    mouths = {edge: triangulation.to_neighbours(edge)
              for edge in unique_everseen(boundary,
                                          key=triangular._edge_to_segment)
              if is_mouth(edge)}

    for _ in range(len(points) - len(boundary)):
        try:
            edge, neighbours = mouths.popitem()
        except KeyError:
            break
        boundary.remove(edge)
        boundary.remove(edge.opposite)
        triangulation.delete(edge)
        boundary.update(neighbours)
        mouths.update((edge, triangulation.to_neighbours(edge))
                      for edge in neighbours
                      if is_mouth(edge))
        start = edge = first(neighbours).opposite
        while edge.left_from_start is not start:
            mouths.pop(edge.left_from_end, None)
            mouths.pop(edge.left_from_end.opposite, None)
            mouths.pop(edge.right_from_end, None)
            mouths.pop(edge.right_from_end.opposite, None)
            edge = edge.left_from_start
    return boundary_to_vertices({to_segment(edge.start, edge.end)
                                 for edge in boundary})


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


def shrink_collinear_vertices(vertices: Vertices) -> Vertices:
    return [vertex
            for index, vertex in enumerate(vertices)
            if Angle(vertices[index - 1], vertex,
                     vertices[(index + 1) % len(vertices)]).orientation
            is not Orientation.COLLINEAR]


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
