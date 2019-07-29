from collections import (defaultdict,
                         deque)
from functools import partial
from heapq import nlargest
from typing import (Dict,
                    Iterable,
                    List,
                    Sequence,
                    Set,
                    Tuple)

from lz.iterating import flatten

from gon.angular import (Angle,
                         Orientation,
                         to_squared_cosine)
from gon.base import (Point,
                      Vector)
from gon.linear import (IntersectionKind,
                        Segment,
                        to_interval,
                        to_segment)
from .contracts import vertices_forms_convex_polygon
from .utils import (to_angles,
                    to_convex_hull,
                    to_edges)

Vertices = Sequence[Point]


def delaunay(points: Sequence[Point]) -> List[Vertices]:
    super_triangle_vertices = _to_super_triangle_vertices(points)
    result = {super_triangle_vertices}
    for point in points:
        is_invalid_triangle = partial(_is_point_inside_circumcircle, point)
        invalid_triangles = tuple(filter(is_invalid_triangle, result))
        hole_edges = _to_boundary(invalid_triangles)
        for vertices in invalid_triangles:
            result.remove(vertices)
        for edge in hole_edges:
            orientation = edge.orientation_with(point)
            if orientation == Orientation.COLLINEAR:
                continue
            vertices = (edge.end, edge.start, point)
            if orientation != Orientation.COUNTERCLOCKWISE:
                vertices = vertices[::-1]
            result.add(vertices)
    return [vertices
            for vertices in result
            if all(vertex not in super_triangle_vertices
                   for vertex in vertices)]


def _to_boundary(triangles_vertices: Iterable[Vertices]) -> Set[Segment]:
    result = set()
    for vertices in triangles_vertices:
        for edge in to_edges(vertices):
            if edge in result:
                result.remove(edge)
            else:
                result.add(edge)
    return result


def _to_super_triangle_vertices(points: Sequence[Point]) -> Vertices:
    bounding_triangle = _to_bounding_triangle_vertices(points)
    return tuple(Point(3 * point.x
                       - bounding_triangle[index - 1].x
                       - bounding_triangle[(index + 1)
                                           % len(bounding_triangle)].x,
                       3 * point.y
                       - bounding_triangle[index - 1].y
                       - bounding_triangle[(index + 1)
                                           % len(bounding_triangle)].y)
                 for index, point in enumerate(bounding_triangle))


def _to_bounding_triangle_vertices(points: Sequence[Point]) -> Vertices:
    convex_hull = to_convex_hull(points)
    base_angle = min(to_angles(convex_hull),
                     key=to_squared_cosine)
    first_farthest_point, second_farthest_point = nlargest(
            2, convex_hull,
            key=base_angle.vertex.squared_distance_to)

    def is_point_on_angle_rays(point: Point, angle: Angle) -> bool:
        return (Segment(angle.vertex,
                        angle.first_ray_point).orientation_with(point)
                == Orientation.COLLINEAR
                or Segment(angle.vertex,
                           angle.second_ray_point).orientation_with(point)
                == Orientation.COLLINEAR)

    if is_point_on_angle_rays(first_farthest_point, base_angle):
        if is_point_on_angle_rays(second_farthest_point, base_angle):
            result = (base_angle.vertex,
                      base_angle.second_ray_point,
                      base_angle.first_ray_point)
            if base_angle.orientation != Orientation.COUNTERCLOCKWISE:
                result = result[::-1]
            return result
        return _to_ccw_triangle_vertices(
                (base_angle.vertex,
                 _to_line_intersection_point(base_angle.vertex,
                                             base_angle.first_ray_point,
                                             first_farthest_point,
                                             second_farthest_point),
                 _to_line_intersection_point(base_angle.vertex,
                                             base_angle.second_ray_point,
                                             first_farthest_point,
                                             second_farthest_point)))
    else:
        perpendicular_point = Point(base_angle.vertex.y
                                    + first_farthest_point.x
                                    - first_farthest_point.y,
                                    first_farthest_point.x
                                    + first_farthest_point.y
                                    - base_angle.vertex.x)
        return _to_ccw_triangle_vertices(
                (base_angle.vertex,
                 _to_line_intersection_point(base_angle.vertex,
                                             base_angle.first_ray_point,
                                             first_farthest_point,
                                             perpendicular_point),
                 _to_line_intersection_point(base_angle.vertex,
                                             base_angle.second_ray_point,
                                             first_farthest_point,
                                             perpendicular_point)))


def _to_line_intersection_point(first_line_start: Point,
                                first_line_end: Point,
                                second_line_start: Point,
                                second_line_end: Point) -> Point:
    denominator = ((first_line_start.x - first_line_end.x)
                   * (second_line_start.y - second_line_end.y)
                   - (first_line_start.y - first_line_end.y)
                   * (second_line_start.x - second_line_end.x))
    first_line_coefficient = (second_line_start.x * second_line_end.y
                              - second_line_start.y * second_line_end.x)
    second_line_coefficient = (first_line_start.x * first_line_end.y
                               - first_line_start.y * first_line_end.x)
    return Point((second_line_coefficient
                  * (second_line_start.x - second_line_end.x)
                  - first_line_coefficient
                  * (first_line_start.x - first_line_end.x))
                 / denominator,
                 (second_line_coefficient
                  * (second_line_start.y - second_line_end.y)
                  - first_line_coefficient
                  * (first_line_start.y - first_line_end.y))
                 / denominator)


def constrained_delaunay(points: Sequence[Point],
                         *,
                         constraints: Iterable[Segment]) -> Sequence[Vertices]:
    result = delaunay(points)
    adjacency = _to_adjacency(result)
    neighbourhood = _to_neighbourhood(result,
                                      adjacency=adjacency)
    points_triangles = _to_points_triangles(result)
    result_edges = frozenset(flatten(map(to_edges, result)))
    boundary = {}
    for constraint in constraints:
        boundary[constraint] = constraint
        if constraint in result_edges:
            continue
        crossed_edges = _find_crossed_edges(constraint, result,
                                            neighbourhood=neighbourhood,
                                            points_triangles=points_triangles)
        new_edges = _resolve_crossings(constraint, result,
                                       adjacency=adjacency,
                                       crossed_edges=crossed_edges)
        _restore_delaunay_criterion(constraint, result,
                                    adjacency=adjacency,
                                    new_edges=new_edges)

    def is_outsider_lying_on_boundary(vertices: Vertices) -> bool:
        for edge in to_edges(vertices):
            try:
                boundary_edge = boundary[edge]
            except KeyError:
                continue
            if boundary_edge.start != edge.start:
                return True
        return False

    external_triangles = {index
                          for index, vertices in enumerate(result)
                          if is_outsider_lying_on_boundary(vertices)}
    boundary_vertices = frozenset(flatten((edge.start, edge.end)
                                          for edge in boundary))
    neighbourhood = _to_neighbourhood(result,
                                      adjacency=adjacency)

    def is_outsider_touching_boundary(index: int, vertices: Vertices) -> bool:
        neighbours = neighbourhood[index]
        return (all(vertex in boundary_vertices
                    for vertex in vertices)
                and neighbours
                and all(neighbour in external_triangles
                        for neighbour in neighbours))

    return [vertices
            for index, vertices in enumerate(result)
            if index not in external_triangles
            and not is_outsider_touching_boundary(index, vertices)]


def _to_points_triangles(triangulation: Sequence[Vertices]
                         ) -> Dict[Point, Set[int]]:
    result = defaultdict(set)
    for index, vertices in enumerate(triangulation):
        for point in vertices:
            result[point].add(index)
    return result


def _to_adjacency(triangulation: Sequence[Vertices]
                  ) -> Dict[Segment, Set[int]]:
    result = defaultdict(set)
    for index, vertices in enumerate(triangulation):
        _register_adjacent(index, vertices,
                           adjacency=result)
    return result


def _to_neighbourhood(triangulation: Sequence[Vertices],
                      *,
                      adjacency: Dict[Segment, Set[int]]
                      ) -> Dict[int, Set[int]]:
    result = defaultdict(set)
    for index, vertices in enumerate(triangulation):
        for edge in to_edges(vertices):
            result[index].update(adjacency[edge] - {index})
    return result


def _restore_delaunay_criterion(constraint: Segment,
                                triangulation: List[Vertices],
                                *,
                                adjacency: Dict[Segment, Set[int]],
                                new_edges: Set[Segment]) -> None:
    while True:
        no_swaps = True
        for edge in new_edges:
            if edge == constraint:
                continue
            adjacents = adjacency[edge]
            first_adjacent_index, second_adjacent_index = adjacents
            first_adjacent = triangulation[first_adjacent_index]
            second_adjacent = triangulation[second_adjacent_index]
            quadriliteral_vertices = to_convex_hull(first_adjacent
                                                    + second_adjacent)
            if not vertices_forms_convex_polygon(quadriliteral_vertices):
                continue
            edge_points = {edge.start, edge.end}
            first_non_edge_vertex, = set(first_adjacent) - edge_points
            second_non_edge_vertex, = set(second_adjacent) - edge_points
            if not (_is_point_inside_circumcircle(first_non_edge_vertex,
                                                  second_adjacent)
                    or _is_point_inside_circumcircle(first_non_edge_vertex,
                                                     second_adjacent)):
                continue
            anti_diagonal = to_segment(first_non_edge_vertex,
                                       second_non_edge_vertex)
            _swap_edges(edge, anti_diagonal,
                        adjacency=adjacency,
                        triangulation=triangulation)
            no_swaps = False
        if no_swaps:
            break


def _resolve_crossings(constraint: Segment,
                       triangulation: List[Vertices],
                       *,
                       adjacency: Dict[Segment, Set[int]],
                       crossed_edges: Set[Segment]) -> Set[Segment]:
    open_constraint = to_interval(constraint.start, constraint.end,
                                  start_inclusive=False,
                                  end_inclusive=False)
    result = set()
    crossed_edges = deque(crossed_edges,
                          maxlen=len(crossed_edges))
    while crossed_edges:
        edge = crossed_edges.popleft()
        first_adjacent, second_adjacent = adjacency[edge]
        quadriliteral_vertices = to_convex_hull(
                triangulation[first_adjacent] + triangulation[second_adjacent])
        if not vertices_forms_convex_polygon(quadriliteral_vertices):
            continue
        anti_diagonal = to_segment(*(set(quadriliteral_vertices)
                                     - {edge.start, edge.end}))
        _swap_edges(edge, anti_diagonal,
                    adjacency=adjacency,
                    triangulation=triangulation)
        if (anti_diagonal.relationship_with(open_constraint)
                is IntersectionKind.CROSS):
            crossed_edges.append(anti_diagonal)
        else:
            result.add(anti_diagonal)
    return result


def _find_crossed_edges(constraint: Segment,
                        triangulation: Sequence[Vertices],
                        *,
                        neighbourhood: Dict[int, Set[int]],
                        points_triangles: Dict[Point, Set[int]]
                        ) -> Set[Segment]:
    open_constraint = to_interval(constraint.start, constraint.end,
                                  start_inclusive=False,
                                  end_inclusive=False)
    step, target_indices = (points_triangles[constraint.start],
                            points_triangles[constraint.end])
    visited_points = {constraint.start}
    result = set()
    while True:
        next_step = set()
        for index in step:
            vertices = triangulation[index]
            for edge in to_edges(vertices):
                if (edge.start not in visited_points
                        and edge.start in open_constraint):
                    next_step.update(points_triangles[edge.start]
                                     - step)
                    visited_points.add(edge.start)
                    break
                elif (edge.end not in visited_points
                      and edge.end in open_constraint):
                    next_step.update(points_triangles[edge.end]
                                     - step)
                    visited_points.add(edge.end)
                    break
                relationship = edge.relationship_with(open_constraint)
                if relationship is IntersectionKind.NONE:
                    continue
                elif relationship is IntersectionKind.CROSS:
                    result.add(edge)
                    next_step.update(neighbourhood[index])
                    break
                else:
                    raise RuntimeError('Unexpected edge-to-constraint '
                                       'relationship: {}.'
                                       .format(relationship))
            else:
                continue
            break
        if step & target_indices:
            break
        step = next_step
    return result


def _swap_edges(src_edge: Segment, dst_edge: Segment,
                *,
                adjacency: Dict[Segment, Set[int]],
                triangulation: List[Vertices]) -> None:
    _update_adjacency(src_edge, dst_edge,
                      adjacency=adjacency)
    _update_triangulation(src_edge, dst_edge,
                          adjacency=adjacency,
                          triangulation=triangulation)
    del adjacency[src_edge]


def _update_triangulation(src_edge: Segment, dst_edge: Segment,
                          *,
                          adjacency: Dict[Segment, Set[int]],
                          triangulation: List[Vertices]) -> None:
    first_vertices, second_vertices = _to_replacements(src_edge, dst_edge)
    first_adjacent, second_adjacent = adjacency[src_edge]
    triangulation[first_adjacent] = first_vertices
    triangulation[second_adjacent] = second_vertices


def _update_adjacency(src_edge: Segment, dst_edge: Segment,
                      *,
                      adjacency: Dict[Segment, Set[int]]) -> None:
    first_vertices, second_vertices = _to_replacements(src_edge, dst_edge)
    adjacents = adjacency[src_edge]
    first_adjacent, second_adjacent = adjacents
    for edge in to_edges(first_vertices):
        adjacency[edge] -= adjacents
    for edge in to_edges(second_vertices):
        adjacency[edge] -= adjacents
    _register_adjacent(first_adjacent, first_vertices,
                       adjacency=adjacency)
    _register_adjacent(second_adjacent, second_vertices,
                       adjacency=adjacency)


def _to_replacements(src_edge: Segment,
                     dst_edge: Segment) -> Tuple[Vertices, Vertices]:
    first_vertices = _to_ccw_triangle_vertices((dst_edge.start, dst_edge.end,
                                                src_edge.start))
    second_vertices = _to_ccw_triangle_vertices((dst_edge.start, dst_edge.end,
                                                 src_edge.end))
    return first_vertices, second_vertices


def _register_adjacent(index: int, vertices: Vertices,
                       *,
                       adjacency: Dict[Segment, Set[int]]) -> None:
    for edge in to_edges(vertices):
        adjacency[edge].add(index)


def _to_ccw_triangle_vertices(result: Vertices) -> Vertices:
    if Angle(*result).orientation != Orientation.COUNTERCLOCKWISE:
        result = result[::-1]
    return result


def _is_point_inside_circumcircle(point: Point,
                                  triangle_vertices: Sequence[Point]) -> bool:
    first_vertex, second_vertex, third_vertex = triangle_vertices
    first_vector = Vector.from_points(point, first_vertex)
    second_vector = Vector.from_points(point, second_vertex)
    third_vector = Vector.from_points(point, third_vertex)
    return (first_vector.squared_length * second_vector.cross_z(third_vector)
            - second_vector.squared_length * first_vector.cross_z(third_vector)
            + third_vector.squared_length * first_vector.cross_z(second_vector)
            ) < 0
