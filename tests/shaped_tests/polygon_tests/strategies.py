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
            .map(points_to_concave_vertices)
            .filter(negate(vertices_forms_convex_polygon)))


def points_to_concave_vertices(points: Sequence[Point]) -> Vertices:
    triangulation = triangular.delaunay(points)
    boundary = triangulation.to_boundary_edges()

    def is_mouth(edge: QuadEdge) -> bool:
        neighbours = triangulation.to_neighbours(edge)
        return len(neighbours) == 2 and not (neighbours & boundary)

    mouths = {edge: triangulation.to_neighbours(edge)
              for edge in unique_everseen(boundary,
                                          key=triangular._edge_to_segment)
              if is_mouth(edge)}

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
    return [vertex
            for index, vertex in enumerate(vertices)
            if Angle(vertices[index - 1], vertex,
                     vertices[(index + 1) % len(vertices)]).orientation
            is not Orientation.COLLINEAR]


concave_vertices = (points_strategies.flatmap(to_concave_vertices)
                    .filter(negate(self_intersects)))
vertices = concave_vertices | convex_vertices
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
