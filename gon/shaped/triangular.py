import math
from collections import (defaultdict,
                         deque)
from enum import (IntEnum,
                  unique)
from functools import partial
from heapq import nlargest
from operator import attrgetter
from statistics import mean
from typing import (Container,
                    Dict,
                    Iterable,
                    List,
                    Sequence,
                    Set,
                    Tuple)

from lz.hints import Sortable
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
        for vertices in invalid_triangles:
            result.remove(vertices)
        for edge in _to_boundary(invalid_triangles):
            orientation = edge.orientation_with(point)
            if orientation is Orientation.COLLINEAR:
                continue
            vertices = (edge.end, edge.start, point)
            if orientation is not Orientation.CLOCKWISE:
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
    leftmost_point = min(points,
                         key=attrgetter('x', 'y'))
    max_squared_distance = max(map(leftmost_point.squared_distance_to, points))
    centroid = _to_centroid(bounding_triangle)
    delta_x = (max(point.x for point in points)
               - min(point.x for point in points))
    delta_y = (max(point.y for point in points)
               - min(point.y for point in points))
    aspect_ratio = (delta_x / delta_y
                    if delta_x > delta_y
                    else delta_y / delta_x)
    scale = max((2 + math.sqrt(max_squared_distance
                               / min(Vector.from_points(vertex, centroid)
                                     .squared_length
                                     for vertex in bounding_triangle))),
                # handles "thin" cases
                math.sqrt(aspect_ratio))

    def scale_vertex(vertex: Point) -> Point:
        vector = Vector.from_points(centroid, vertex)
        return Point(centroid.x + vector.x * scale,
                     centroid.y + vector.y * scale)

    return tuple(map(scale_vertex, bounding_triangle))


def _to_centroid(points: Sequence[Point]) -> Point:
    return Point(mean(point.x for point in points),
                 mean(point.y for point in points))


def _to_bounding_triangle_vertices(points: Sequence[Point]) -> Vertices:
    convex_hull = to_convex_hull(points)
    base_angle = min(to_angles(convex_hull),
                     key=to_squared_cosine)
    first_farthest_point, second_farthest_point = nlargest(
            2, convex_hull,
            key=base_angle.vertex.squared_distance_to)

    def is_point_on_angle_rays(point: Point, angle: Angle) -> bool:
        return (to_segment(angle.vertex, angle.first_ray_point)
                .orientation_with(point) is Orientation.COLLINEAR
                or to_segment(angle.vertex, angle.second_ray_point)
                .orientation_with(point) is Orientation.COLLINEAR)

    if is_point_on_angle_rays(first_farthest_point, base_angle):
        if is_point_on_angle_rays(second_farthest_point, base_angle):
            result = (base_angle.vertex,
                      base_angle.second_ray_point,
                      base_angle.first_ray_point)
            if base_angle.orientation is not Orientation.CLOCKWISE:
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
    first_line_vector = Vector.from_points(first_line_start, first_line_end)
    second_line_vector = Vector.from_points(second_line_start, second_line_end)
    denominator = first_line_vector.cross_z(second_line_vector)
    first_line_coefficient = (Vector.from_point(second_line_start)
                              .cross_z(Vector.from_point(second_line_end)))
    second_line_coefficient = (Vector.from_point(first_line_start)
                               .cross_z(Vector.from_point(first_line_end)))
    return Point((first_line_coefficient * first_line_vector.x
                  - second_line_coefficient * second_line_vector.x)
                 / denominator,
                 (first_line_coefficient * first_line_vector.y
                  - second_line_coefficient * second_line_vector.y)
                 / denominator)


@unique
class TriangleKind(IntEnum):
    UNKNOWN = 0
    INNER = 1
    OUTER = 2


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
    return _filter_outsiders(result,
                             adjacency=adjacency,
                             boundary=boundary)


def _filter_outsiders(triangulation: List[Vertices],
                      *,
                      adjacency: Dict[Segment, Set[int]],
                      boundary: Dict[Segment, Segment]) -> List[Vertices]:
    vertices_edges = defaultdict(set)
    for edge in boundary:
        vertices_edges[edge.start].add(edge)
        vertices_edges[edge.end].add(edge)
    edges_neighbourhood = {}
    for edge in boundary:
        edges_neighbourhood[edge] = (list(vertices_edges[edge.start] - {edge})
                                     + list(vertices_edges[edge.end] - {edge}))

    def classify_lying_on_boundary(
            vertices: Vertices,
            *,
            boundary_vertices: Container[Point] =
            frozenset(flatten((edge.start, edge.end)
                              for edge in boundary))) -> TriangleKind:
        if not all(vertex in boundary_vertices
                   for vertex in vertices):
            return TriangleKind.INNER
        edges = set(to_edges(vertices))
        boundary_edges = {edge for edge in edges if edge in boundary}
        if not boundary_edges:
            return TriangleKind.UNKNOWN
        elif len(boundary_edges) == 1:
            edge, = boundary_edges
            oriented_boundary_edge = boundary[edge]
            if edge.start != oriented_boundary_edge.start:
                return TriangleKind.OUTER
            else:
                return TriangleKind.INNER
        elif len(boundary_edges) == 2:
            first_edge, second_edge = map(boundary.get, boundary_edges)
            invalid_order = first_edge.end != second_edge.start
            if invalid_order:
                first_edge, second_edge = second_edge, first_edge
            previous_edge = edges_neighbourhood[first_edge][0]
            previous_orientation = Angle(previous_edge.start,
                                         previous_edge.end,
                                         first_edge.end).orientation
            current_orientation = Angle(first_edge.start,
                                        first_edge.end,
                                        second_edge.end).orientation
            if previous_orientation is Orientation.CLOCKWISE:
                if current_orientation is Orientation.COUNTERCLOCKWISE:
                    return TriangleKind.OUTER
                else:
                    return TriangleKind.INNER
            elif current_orientation is Orientation.CLOCKWISE:
                return TriangleKind.INNER
            else:
                return TriangleKind.OUTER
        else:
            # degenerate case with single triangle
            return TriangleKind.INNER

    triangles_kinds = {index: classify_lying_on_boundary(vertices)
                       for index, vertices in enumerate(triangulation)}
    neighbourhood = _to_neighbourhood(triangulation,
                                      adjacency=adjacency)

    def sorting_key(index: int) -> Sortable:
        neighbours = neighbourhood[index]
        neighbours_kinds = {neighbour: triangles_kinds[neighbour]
                            for neighbour in neighbours}
        unprocessed_neighbours = {
            neighbour: kind
            for neighbour, kind in neighbours_kinds.items()
            if kind is TriangleKind.UNKNOWN}
        return (len(unprocessed_neighbours),
                set(unprocessed_neighbours.keys()) | {index})

    unprocessed = sorted((index
                          for index, kind in triangles_kinds.items()
                          if kind is TriangleKind.UNKNOWN),
                         key=sorting_key)

    def is_touching_boundary_outsider(index: int) -> bool:
        neighbours = neighbourhood[index]
        if not neighbours:
            return False
        return all(is_neighbour_outsider(index, neighbour)
                   for neighbour in neighbours)

    def is_neighbour_outsider(index: int, neighbour: int,
                              *,
                              excluded: Set[int] = frozenset()) -> bool:
        neighbour_kind = triangles_kinds[neighbour]
        return (neighbour_kind is TriangleKind.OUTER
                # special case of two outside adjacent triangles
                or neighbour_kind is TriangleKind.UNKNOWN
                and all(is_neighbour_outsider(neighbour, post_neighbour,
                                              excluded=excluded | {index})
                        for post_neighbour in neighbourhood[neighbour]
                        - {index} - excluded))

    for index in unprocessed:
        triangles_kinds[index] = (TriangleKind.OUTER
                                  if is_touching_boundary_outsider(index)
                                  else TriangleKind.INNER)
    return [vertices
            for index, vertices in enumerate(triangulation)
            if triangles_kinds[index] is TriangleKind.INNER]


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
        vertices = to_convex_hull(triangulation[first_adjacent]
                                  + triangulation[second_adjacent])
        if not (len(vertices) == 4
                and vertices_forms_convex_polygon(vertices)):
            crossed_edges.append(edge)
            continue
        anti_diagonal = to_segment(*(set(vertices)
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


def _to_ccw_triangle_vertices(vertices: Vertices) -> Vertices:
    if Angle(*vertices).orientation is not Orientation.CLOCKWISE:
        vertices = vertices[::-1]
    return vertices


def _is_point_inside_circumcircle(point: Point,
                                  triangle_vertices: Vertices) -> bool:
    first_vertex, second_vertex, third_vertex = triangle_vertices
    first_vector = Vector.from_points(point, first_vertex)
    second_vector = Vector.from_points(point, second_vertex)
    third_vector = Vector.from_points(point, third_vertex)
    return (first_vector.squared_length * second_vector.cross_z(third_vector)
            - second_vector.squared_length * first_vector.cross_z(third_vector)
            + third_vector.squared_length * first_vector.cross_z(second_vector)
            ) > 0
