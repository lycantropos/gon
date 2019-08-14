import math
from collections import (defaultdict,
                         deque)
from enum import (IntEnum,
                  unique)
from functools import (partial,
                       reduce)
from statistics import mean
from typing import (Container,
                    Dict,
                    Iterable,
                    List,
                    Sequence,
                    Set,
                    Tuple)

from lz.functional import flatmap
from lz.hints import Sortable
from lz.iterating import flatten
from memoir import cached
from reprit.base import generate_repr

from gon.angular import (Angle,
                         Orientation,
                         to_half_angle_cosine,
                         to_half_angle_sine,
                         to_squared_sine)
from gon.base import (Point,
                      Vector)
from gon.hints import Scalar
from gon.linear import (IntersectionKind,
                        Segment,
                        to_interval,
                        to_segment)
from .contracts import vertices_forms_convex_polygon
from .utils import (to_angles,
                    to_convex_hull,
                    to_edges)


class Circle:
    __slots__ = ('_center', '_squared_radius', '__weakref__')

    def __init__(self, center: Point, squared_radius: Scalar) -> None:
        self._center = center
        self._squared_radius = squared_radius

    @property
    def center(self) -> Point:
        return self._center

    @property
    def squared_radius(self) -> Scalar:
        return self._squared_radius

    @cached.property_
    def radius(self) -> Scalar:
        return math.sqrt(self._squared_radius)

    __repr__ = generate_repr(__init__)

    def __hash__(self) -> int:
        return hash((self._center, self._squared_radius))

    def __eq__(self, other: 'Circle') -> bool:
        if not isinstance(other, Circle):
            return NotImplemented
        return (self._center == other._center
                and self._squared_radius == other._squared_radius)

    def merge(self, other: 'Circle') -> 'Circle':
        center = _to_centroid([self.center, other.center])
        if center == self.center or center == other.center:
            squared_radius = max(self.squared_radius, other.squared_radius)
        else:
            squared_radius = max(
                    map(center.squared_distance_to,
                        list(self.intersections_with_line(center, self.center))
                        + list(other.intersections_with_line(center,
                                                             other.center))))
        return Circle(center, squared_radius)

    def intersections_with_line(self,
                                line_segment_start: Point,
                                line_segment_end: Point) -> Iterable[Point]:
        line_vector = (Vector.from_points(line_segment_start, line_segment_end)
                       .normalized)
        scale = Vector.from_points(line_segment_start,
                                   self._center).dot(line_vector)
        nearest_line_point_to_center = Point(
                scale * line_vector.x + line_segment_start.x,
                scale * line_vector.y + line_segment_start.y)
        squared_distance_to_nearest_point = self._center.squared_distance_to(
                nearest_line_point_to_center)
        if squared_distance_to_nearest_point < self._squared_radius:
            distance_to_intersection_point = math.sqrt(
                    self._squared_radius - squared_distance_to_nearest_point)
            yield Point((scale - distance_to_intersection_point)
                        * line_vector.x
                        + line_segment_start.x,
                        (scale - distance_to_intersection_point)
                        * line_vector.y
                        + line_segment_start.y)
            yield Point((scale + distance_to_intersection_point)
                        * line_vector.x
                        + line_segment_start.x,
                        (scale + distance_to_intersection_point)
                        * line_vector.y
                        + line_segment_start.y)
        elif squared_distance_to_nearest_point == self._squared_radius:
            yield nearest_line_point_to_center

    def tangent_line_point(self, tangent_point: Point) -> Point:
        radius_vector = Vector.from_points(self._center, tangent_point)
        if abs(radius_vector.x) > abs(radius_vector.y):
            result_y = 2 * (tangent_point.y + 1)
            return Point((self._squared_radius
                          - radius_vector.y * (result_y - self._center.y))
                         / radius_vector.x
                         + self._center.x,
                         result_y)
        else:
            result_x = 2 * (tangent_point.y + 1)
            return Point(result_x,
                         (self._squared_radius
                          - radius_vector.x * (result_x - self._center.x))
                         / radius_vector.y
                         + self._center.y)


Vertices = Sequence[Point]


class Triangle:
    __slots__ = ('_vertices', '__weakref__')

    def __init__(self, vertices: Vertices) -> None:
        if Angle(*vertices).orientation is not Orientation.CLOCKWISE:
            vertices = vertices[::-1]
        self._vertices = tuple(vertices)

    @property
    def vertices(self) -> Vertices:
        return self._vertices

    __repr__ = generate_repr(__init__)

    def __hash__(self) -> int:
        return hash(self._vertices)

    def __eq__(self, other: 'Triangle') -> bool:
        if not isinstance(other, Triangle):
            return NotImplemented
        return self._vertices == other._vertices

    def is_point_inside_circumcircle(self, point: Point) -> bool:
        first_vertex, second_vertex, third_vertex = self.vertices
        first_vector = Vector.from_points(point, first_vertex)
        second_vector = Vector.from_points(point, second_vertex)
        third_vector = Vector.from_points(point, third_vertex)
        return (first_vector.squared_length
                * second_vector.cross_z(third_vector)
                - second_vector.squared_length
                * first_vector.cross_z(third_vector)
                + third_vector.squared_length
                * first_vector.cross_z(second_vector)) > 0


def delaunay(points: Sequence[Point]) -> List[Triangle]:
    super_triangle_vertices = _to_super_triangle_vertices(points)
    result = {Triangle(super_triangle_vertices)}
    for point in points:
        invalid_triangles = [triangle
                             for triangle in result
                             if triangle.is_point_inside_circumcircle(point)]
        result.difference_update(invalid_triangles)
        result.update(Triangle((edge.end, edge.start, point))
                      for edge in _to_boundary(invalid_triangles))
    return [triangle
            for triangle in result
            if all(vertex not in super_triangle_vertices
                   for vertex in triangle.vertices)]


def _to_boundary(triangles: Iterable[Triangle]) -> Set[Segment]:
    return _to_polygons_vertices_boundary(triangle.vertices
                                          for triangle in triangles)


def _to_polygons_vertices_boundary(polygons_vertices: Iterable[Vertices]
                                   ) -> Set[Segment]:
    result = set()
    for vertices in polygons_vertices:
        for edge in to_edges(vertices):
            if edge in result:
                result.remove(edge)
            else:
                result.add(edge)
    return result


def _to_super_triangle_vertices(points: Sequence[Point]) -> Vertices:
    convex_hull = to_convex_hull(points)
    bounding_triangle = _to_bounding_triangle_vertices(convex_hull)

    def scale_vertex(vertex: Point,
                     *,
                     scale: Scalar,
                     centroid: Point = _to_centroid(bounding_triangle)
                     ) -> Point:
        vector = Vector.from_points(centroid, vertex)
        return Point(centroid.x + vector.x * scale,
                     centroid.y + vector.y * scale)

    result = tuple(map(partial(scale_vertex,
                               scale=2),
                       bounding_triangle))
    circumcircle = _to_circumcircle(result)
    base_circle = reduce(Circle.merge,
                         [_to_circumcircle((edge.start, edge.end, point))
                          for edge in to_edges(result)
                          for point in points])
    max_distance_between_circumferences = (circumcircle.center
                                           .distance_to(base_circle.center)
                                           + circumcircle.radius
                                           + base_circle.radius)
    scale = max_distance_between_circumferences / min(circumcircle.radius,
                                                      base_circle.radius)
    return tuple(map(partial(scale_vertex,
                             scale=scale),
                     result))


def _to_bounding_triangle_vertices(convex_vertices: Vertices) -> Vertices:
    def angle_sorting_key(angle: Angle) -> Sortable:
        squared_sine = to_squared_sine(angle)
        # we are not interested in angles with 0 and 180 degrees
        return squared_sine != 0, squared_sine

    base_angle = min(to_angles(convex_vertices),
                     key=angle_sorting_key)
    point = max(convex_vertices,
                key=base_angle.vertex.squared_distance_to)

    def is_point_on_angle_rays(point: Point, angle: Angle) -> bool:
        return (to_segment(angle.vertex, angle.first_ray_point)
                .orientation_with(point) is Orientation.COLLINEAR
                or to_segment(angle.vertex, angle.second_ray_point)
                .orientation_with(point) is Orientation.COLLINEAR)

    if is_point_on_angle_rays(point, base_angle):
        base_circle = Circle(base_angle.vertex,
                             base_angle.vertex.squared_distance_to(point))
        bisector_point = _move_to_circumference(_to_bisector_point(base_angle),
                                                base_circle)
        tangent_line_point = base_circle.tangent_line_point(bisector_point)
        return (base_angle.vertex,
                _to_lines_intersection_point(bisector_point,
                                             tangent_line_point,
                                             base_angle.vertex,
                                             base_angle.first_ray_point),
                _to_lines_intersection_point(bisector_point,
                                             tangent_line_point,
                                             base_angle.vertex,
                                             base_angle.second_ray_point))
    else:
        circle = Circle(base_angle.vertex,
                        base_angle.vertex.squared_distance_to(point))
        tangent_line_point = circle.tangent_line_point(point)
        return (base_angle.vertex,
                _to_lines_intersection_point(base_angle.vertex,
                                             base_angle.first_ray_point,
                                             point,
                                             tangent_line_point),
                _to_lines_intersection_point(base_angle.vertex,
                                             base_angle.second_ray_point,
                                             point,
                                             tangent_line_point))


def _move_to_circumference(point: Point, circle: Circle) -> Point:
    return min(circle.intersections_with_line(circle.center, point),
               key=point.squared_distance_to)


def _to_bisector_point(angle: Angle) -> Point:
    rotation_sine = to_half_angle_sine(angle)
    rotation_cosine = to_half_angle_cosine(angle)
    ray_point = (angle.first_ray_point
                 if angle.orientation is Orientation.COUNTERCLOCKWISE
                 else angle.second_ray_point)
    return Point(ray_point.x * rotation_cosine
                 - ray_point.y * rotation_sine,
                 ray_point.x * rotation_sine
                 + ray_point.y * rotation_cosine)


def _to_centroid(points: Sequence[Point]) -> Point:
    return Point(mean(point.x for point in points),
                 mean(point.y for point in points))


def _to_lines_intersection_point(first_line_start: Point,
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


def constrained_delaunay(points: Sequence[Point],
                         *,
                         constraints: Iterable[Segment]) -> Sequence[Triangle]:
    result = delaunay(points)
    adjacency = _to_adjacency(result)
    neighbourhood = _to_neighbourhood(result,
                                      adjacency=adjacency)
    points_triangles = _to_points_triangles(result)
    result_edges = frozenset(flatmap(to_edges, (triangle.vertices
                                                for triangle in result)))
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


@unique
class TriangleKind(IntEnum):
    UNKNOWN = 0
    INNER = 1
    OUTER = 2


def _filter_outsiders(triangulation: List[Triangle],
                      *,
                      adjacency: Dict[Segment, Set[int]],
                      boundary: Dict[Segment, Segment]) -> List[Triangle]:
    vertices_edges = defaultdict(set)
    for edge in boundary:
        vertices_edges[edge.start].add(edge)
        vertices_edges[edge.end].add(edge)
    edges_neighbourhood = {}
    for edge in boundary:
        edges_neighbourhood[edge] = (list(vertices_edges[edge.start] - {edge})
                                     + list(vertices_edges[edge.end] - {edge}))

    def classify_lying_on_boundary(
            triangle: Triangle,
            *,
            boundary_vertices: Container[Point] =
            frozenset(flatten((edge.start, edge.end)
                              for edge in boundary))) -> TriangleKind:
        if not all(vertex in boundary_vertices
                   for vertex in triangle.vertices):
            return TriangleKind.INNER
        edges = set(to_edges(triangle.vertices))
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

    triangles_kinds = {index: classify_lying_on_boundary(triangle)
                       for index, triangle in enumerate(triangulation)}
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
    return [triangle
            for index, triangle in enumerate(triangulation)
            if triangles_kinds[index] is TriangleKind.INNER]


def _to_points_triangles(triangulation: Sequence[Triangle]
                         ) -> Dict[Point, Set[int]]:
    result = defaultdict(set)
    for index, triangle in enumerate(triangulation):
        for vertex in triangle.vertices:
            result[vertex].add(index)
    result.default_factory = None
    return result


def _to_adjacency(triangulation: Sequence[Triangle]
                  ) -> Dict[Segment, Set[int]]:
    result = defaultdict(set)
    for index, triangle in enumerate(triangulation):
        _register_adjacent(index, triangle,
                           adjacency=result)
    result.default_factory = None
    return result


def _to_neighbourhood(triangulation: Sequence[Triangle],
                      *,
                      adjacency: Dict[Segment, Set[int]]
                      ) -> Dict[int, Set[int]]:
    result = defaultdict(set)
    for index, triangle in enumerate(triangulation):
        for edge in to_edges(triangle.vertices):
            result[index].update(adjacency[edge] - {index})
    result.default_factory = None
    return result


def _restore_delaunay_criterion(constraint: Segment,
                                triangulation: List[Triangle],
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
            quadriliteral_vertices = to_convex_hull(first_adjacent.vertices
                                                    + second_adjacent.vertices)
            if not vertices_forms_convex_polygon(quadriliteral_vertices):
                continue
            edge_points = {edge.start, edge.end}
            first_non_edge_vertex, = set(first_adjacent) - edge_points
            second_non_edge_vertex, = set(second_adjacent) - edge_points
            if not (first_adjacent.is_point_inside_circumcircle(
                    second_non_edge_vertex)
                    or second_adjacent.is_point_inside_circumcircle(
                            first_non_edge_vertex)):
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
                       triangulation: List[Triangle],
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
        vertices = to_convex_hull(triangulation[first_adjacent].vertices
                                  + triangulation[second_adjacent].vertices)
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
                        triangulation: Sequence[Triangle],
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
            triangle = triangulation[index]
            for edge in to_edges(triangle.vertices):
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
                triangulation: List[Triangle]) -> None:
    _update_adjacency(src_edge, dst_edge,
                      adjacency=adjacency)
    _update_triangulation(src_edge, dst_edge,
                          adjacency=adjacency,
                          triangulation=triangulation)
    del adjacency[src_edge]


def _update_triangulation(src_edge: Segment, dst_edge: Segment,
                          *,
                          adjacency: Dict[Segment, Set[int]],
                          triangulation: List[Triangle]) -> None:
    first_vertices, second_vertices = _to_replacements(src_edge, dst_edge)
    first_adjacent, second_adjacent = adjacency[src_edge]
    triangulation[first_adjacent] = first_vertices
    triangulation[second_adjacent] = second_vertices


def _update_adjacency(src_edge: Segment, dst_edge: Segment,
                      *,
                      adjacency: Dict[Segment, Set[int]]) -> None:
    first_triangle, second_triangle = _to_replacements(src_edge, dst_edge)
    adjacents = adjacency[src_edge]
    first_adjacent, second_adjacent = adjacents
    for edge in to_edges(first_triangle.vertices):
        adjacency[edge] -= adjacents
    for edge in to_edges(second_triangle.vertices):
        adjacency[edge] -= adjacents
    _register_adjacent(first_adjacent, first_triangle,
                       adjacency=adjacency)
    _register_adjacent(second_adjacent, second_triangle,
                       adjacency=adjacency)


def _to_replacements(src_edge: Segment,
                     dst_edge: Segment) -> Tuple[Triangle, Triangle]:
    return (Triangle((dst_edge.start, dst_edge.end, src_edge.start)),
            Triangle((dst_edge.start, dst_edge.end, src_edge.end)))


def _register_adjacent(index: int, triangle: Triangle,
                       *,
                       adjacency: Dict[Segment, Set[int]]) -> None:
    for edge in to_edges(triangle.vertices):
        adjacency[edge].add(index)


def _to_circumcircle(vertices: Vertices) -> Circle:
    first_vertex, second_vertex, third_vertex = vertices
    denominator = (2 * (first_vertex.x * (second_vertex.y - third_vertex.y)
                        + second_vertex.x * (third_vertex.y - first_vertex.y)
                        + third_vertex.x * (first_vertex.y - second_vertex.y)))
    center_x = ((first_vertex.x ** 2 + first_vertex.y ** 2)
                * (second_vertex.y - third_vertex.y)
                + (second_vertex.x ** 2 + second_vertex.y ** 2)
                * (third_vertex.y - first_vertex.y)
                + (third_vertex.x ** 2 + third_vertex.y ** 2)
                * (first_vertex.y - second_vertex.y)) / denominator
    center_y = ((first_vertex.x ** 2 + first_vertex.y ** 2)
                * (third_vertex.x - second_vertex.x)
                + (second_vertex.x ** 2 + second_vertex.y ** 2)
                * (first_vertex.x - third_vertex.x)
                + (third_vertex.x ** 2 + third_vertex.y ** 2)
                * (second_vertex.x - first_vertex.x)) / denominator
    squared_radius = ((first_vertex.x - center_x) ** 2
                      + (first_vertex.y - center_y) ** 2)
    return Circle(Point(center_x, center_y), squared_radius)
