from typing import (Sequence,
                    Tuple)

from hypothesis import strategies
from lz.functional import identity
from lz.iterating import (first,
                          flatten)
from lz.logical import negate

from gon.angular import (Angle,
                         Orientation)
from gon.base import Point
from gon.hints import Scalar
from gon.shaped import (Polygon,
                        to_polygon,
                        triangular)
from gon.shaped.contracts import (self_intersects,
                                  vertices_forms_convex_polygon)
from gon.shaped.hints import Vertices
from gon.shaped.subdivisional import QuadEdge
from gon.shaped.utils import to_convex_hull
from tests.strategies import (scalars_strategies,
                              scalars_to_points,
                              scalars_to_triangles_vertices,
                              to_non_triangle_vertices_base)
from tests.utils import (Strategy, cleave_in_tuples, edge_to_ring,
                         points_do_not_lie_on_the_same_line, to_pairs,
                         to_triplets, unique_everseen)

triangles = (scalars_strategies
             .flatmap(scalars_to_triangles_vertices)
             .map(to_polygon))


def scalars_to_convex_vertices(scalars: Strategy[Scalar]
                               ) -> Strategy[Vertices]:
    return (scalars_to_triangles_vertices(scalars)
            | (to_non_triangle_vertices_base(scalars_to_points(scalars))
               .map(to_convex_hull)
               .filter(lambda vertices: len(vertices) >= 3)))


def scalars_to_concave_vertices(scalars: Strategy[Scalar]
                                ) -> Strategy[Vertices]:
    return (strategies.lists(scalars_to_points(scalars),
                             min_size=4,
                             unique=True)
            .filter(points_do_not_lie_on_the_same_line)
            .map(triangular.delaunay)
            .flatmap(to_triangulation_with_swappable_edges)
            .map(swap_edges)
            .map(triangulation_to_concave_vertices)
            .filter(lambda vertices: len(vertices) > 2)
            .filter(negate(vertices_forms_convex_polygon))
            .filter(negate(self_intersects)))


def to_triangulation_with_swappable_edges(
        triangulation: triangular.Triangulation
) -> Strategy[Tuple[triangular.Triangulation, Sequence[QuadEdge]]]:
    def neighbours_form_convex_quadrilateral(edge: QuadEdge) -> bool:
        return triangular._points_form_convex_quadrilateral(
                list(unique_everseen(flatten(
                        (edge.start, edge.end)
                        for edge in triangulation.to_neighbours(edge)))))

    swappable_edges = list(unique_everseen(
            [edge
             for edge in triangulation.to_edges()
             if neighbours_form_convex_quadrilateral(edge)],
            key=triangular._edge_to_segment))
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
        while (max(index, 2) < len(result)
               and Angle(result[index - 2], result[index - 1],
                         result[index]).orientation
               is Orientation.COLLINEAR):
            del result[index - 1]
    return result


def scalars_to_vertices(scalars: Strategy[Scalar]) -> Strategy[Vertices]:
    return (scalars_to_convex_vertices(scalars)
            | scalars_to_concave_vertices(scalars))


def to_tailed_triangles(scale: int) -> Polygon:
    """Creates specific polygon that increases triangulation code coverage."""
    return to_polygon([Point(0, 0), Point(scale, 0), Point(3 * scale, -scale),
                       Point(4 * scale, scale),
                       Point(2 * scale, 0), Point(scale, 100 * scale)])


def scalars_to_polygons(scalars: Strategy[Scalar]) -> Strategy[Polygon]:
    return (strategies.integers().filter(bool).map(to_tailed_triangles)
            | scalars_to_vertices(scalars).map(to_polygon))


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
