from typing import (Sequence,
                    Tuple)

from hypothesis import strategies
from lz.iterating import (first,
                          flatten)
from lz.logical import negate

from gon.angular import (Angle,
                         Orientation)
from gon.base import Point
from gon.shaped import (Polygon,
                        to_polygon,
                        triangular)
from gon.shaped.contracts import (self_intersects,
                                  vertices_forms_convex_polygon)
from gon.shaped.hints import Vertices
from gon.shaped.subdivisional import QuadEdge
from gon.shaped.utils import (to_convex_hull,
                              to_edges)
from tests.strategies import (points_strategies,
                              scalars_to_points,
                              segment_to_scalars,
                              to_non_triangle_vertices_base,
                              triangles_vertices)
from tests.utils import (Strategy,
                         edge_to_ring,
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
            .map(triangular.delaunay)
            .flatmap(to_triangulation_with_swappable_edges)
            .map(swap_edges)
            .map(triangulation_to_concave_vertices)
            .filter(negate(vertices_forms_convex_polygon))
            .filter(negate(self_intersects)))


def to_triangulation_with_swappable_edges(
        triangulation: triangular.Triangulation
) -> Strategy[Tuple[triangular.Triangulation, Sequence[QuadEdge]]]:
    swappable_edges = [edge for edge in triangulation.to_edges() if
                       triangulation.to_neighbours(edge) == 4]
    edges_to_swap = (strategies.sampled_from(swappable_edges)
                     if swappable_edges
                     else strategies.nothing())
    return strategies.tuples(strategies.just(triangulation),
                             strategies.lists(edges_to_swap,
                                              unique=True))


def swap_edges(
        triangulation_with_swappable_edges: Tuple[triangular.Triangulation,
                                                  Sequence[QuadEdge]]
) -> triangular.Triangulation:
    triangulation, swappable_edges = triangulation_with_swappable_edges
    for edge in swappable_edges:
        assert edge != triangulation.left_edge
        assert edge != triangulation.right_edge
        assert triangulation.to_neighbours(edge) == 4
        edge.swap()
    return triangulation


def triangulation_to_concave_vertices(triangulation: triangular.Triangulation
                                      ) -> Vertices:
    boundary = triangulation.to_boundary_edges()

    def is_mouth(edge: QuadEdge) -> bool:
        neighbours = triangulation.to_neighbours(edge)
        return len(neighbours) == 2 and not (neighbours & boundary)

    mouths = {edge: triangulation.to_neighbours(edge)
              for edge in unique_everseen(boundary,
                                          key=triangular._edge_to_segment)
              if is_mouth(edge)}
    points = set(flatten((edge.start, edge.end)
                         for edge in triangulation.to_edges()))
    for _ in range(len(points) - len(boundary) // 2):
        try:
            edge, neighbours = mouths.popitem()
        except KeyError:
            break
        boundary.remove(edge)
        boundary.remove(edge.opposite)
        triangulation.delete(edge)
        boundary.update(flatten((neighbour, neighbour.opposite)
                                for neighbour in neighbours))
        mouths.update((edge, triangulation.to_neighbours(edge))
                      for edge in neighbours
                      if is_mouth(edge))
        for edge in edge_to_ring(first(neighbours).opposite):
            mouths.pop(edge.left_from_end, None)
            mouths.pop(edge.left_from_end.opposite, None)
            mouths.pop(edge.right_from_end, None)
            mouths.pop(edge.right_from_end.opposite, None)
    boundary_endpoints = [edge.start
                          for edge in triangulation._to_boundary_edges()]
    return shrink_collinear_vertices(boundary_endpoints)


def shrink_collinear_vertices(vertices: Vertices) -> Vertices:
    result = [vertices[0], vertices[1]]
    for vertex in vertices[2:]:
        while (len(result) > 2 and
               Angle(result[-2], result[-1], vertex).orientation
               is Orientation.COLLINEAR):
            del result[-1]
        result.append(vertex)
    for index in range(len(result)):
        if index >= len(result):
            break
        if (Angle(result[index - 2], result[index - 1],
                  result[index]).orientation
                is Orientation.COLLINEAR):
            del result[index - 1]
    return result


concave_vertices = points_strategies.flatmap(to_concave_vertices)
vertices = concave_vertices | convex_vertices
polygons = vertices.map(to_polygon)


def to_polygons_with_points(polygon: Polygon
                            ) -> Strategy[Tuple[Polygon, Point]]:
    scalars = strategies.one_of(list(map(segment_to_scalars,
                                         to_edges(polygon.vertices))))
    return strategies.tuples(strategies.just(polygon),
                             scalars_to_points(scalars))


polygons_with_points = polygons.flatmap(to_polygons_with_points)


def to_polygon_with_vertices_indices(polygon: Polygon
                                     ) -> Strategy[Tuple[Polygon, int]]:
    indices = strategies.integers(min_value=0,
                                  max_value=len(polygon.vertices))
    return strategies.tuples(strategies.just(polygon), indices)


polygons_with_vertices_indices = (polygons
                                  .flatmap(to_polygon_with_vertices_indices))
