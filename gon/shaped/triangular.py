import heapq
from collections import (defaultdict,
                         deque)
from enum import (IntEnum,
                  unique)
from operator import attrgetter
from types import MappingProxyType
from typing import (AbstractSet,
                    Container,
                    DefaultDict,
                    Dict,
                    Iterable,
                    List,
                    Mapping,
                    Optional,
                    Sequence,
                    Set,
                    Tuple)

from lz.functional import flatmap
from lz.hints import (Domain,
                      Sortable)
from lz.iterating import (flatten,
                          grouper)
from memoir import cached
from reprit.base import generate_repr

from gon.angular import (Angle,
                         Orientation)
from gon.base import (Point,
                      Vector)
from gon.linear import (IntersectionKind,
                        Segment,
                        to_interval,
                        to_segment)
from .contracts import vertices_forms_convex_polygon
from .utils import (_to_sub_hull,
                    to_convex_hull,
                    to_edges)

Vertices = Sequence[Point]


def _to_ccw_triangle_vertices(vertices: Vertices) -> Vertices:
    if Angle(*vertices).orientation is not Orientation.CLOCKWISE:
        vertices = vertices[::-1]
    return vertices


def _is_point_inside_circumcircle(vertices: Vertices, point: Point) -> bool:
    first_vertex, second_vertex, third_vertex = vertices
    first_vector = Vector.from_points(point, first_vertex)
    second_vector = Vector.from_points(point, second_vertex)
    third_vector = Vector.from_points(point, third_vertex)
    return (first_vector.squared_length
            * second_vector.cross_z(third_vector)
            - second_vector.squared_length
            * first_vector.cross_z(third_vector)
            + third_vector.squared_length
            * first_vector.cross_z(second_vector)) > 0


def _incremental_delaunay(points: Iterable[Point],
                          super_triangle_vertices: Vertices) -> Set[Vertices]:
    result = {tuple(super_triangle_vertices)}
    for point in points:
        invalid_triangles = [vertices
                             for vertices in result
                             if _is_point_inside_circumcircle(vertices, point)]
        result.difference_update(invalid_triangles)
        result.update(
                _to_ccw_triangle_vertices((edge.end, edge.start, point))
                for edge in _to_boundary(invalid_triangles)
                if edge.orientation_with(point) is not Orientation.COLLINEAR)
    return result


def _to_non_strict_convex_hull(sorted_points: Sequence[Point]) -> List[Point]:
    """
    Builds non-strict convex hull from lexicographically sorted points,
    i.e. points lying on edges are not filtered out.

    Time complexity:
        O(n), where
        n -- points count.
    """

    def _to_sub_hull(points: Iterable[Point]) -> List[Point]:
        result = []
        for point in points:
            while len(result) >= 2:
                if (Angle(result[-1], result[-2], point).orientation
                        is Orientation.CLOCKWISE):
                    del result[-1]
                else:
                    break
            result.append(point)
        return result

    lower = _to_sub_hull(sorted_points)
    upper = _to_sub_hull(reversed(sorted_points))
    convex_hull = lower[:-1] + upper[:-1]
    return convex_hull


class Triangulation:
    def __init__(self, points: Sequence[Point],
                 *,
                 linkage: Optional[DefaultDict[Point, Set[Point]]] = None
                 ) -> None:
        self._points = tuple(points)
        if linkage is None:
            linkage = defaultdict(set)
        self._linkage = linkage

    __repr__ = generate_repr(__init__)

    @property
    def points(self) -> Sequence[Point]:
        return self._points

    def to_adjacency(self) -> Dict[Segment, Set[Point]]:
        return {edge: self._to_non_adjacent_vertices(edge)
                for edge in self.edges}

    @property
    def linkage(self) -> Mapping[Point, Set[Point]]:
        return MappingProxyType(self._linkage)

    @property
    def edges(self) -> Set[Segment]:
        return set(self._iter_edges())

    def _iter_edges(self) -> Iterable[Segment]:
        visited = set()
        for start, connected in self._linkage.items():
            for end in connected - visited:
                yield to_segment(start, end)
            visited.add(start)

    @cached.property_
    def boundary(self) -> AbstractSet[Segment]:
        return frozenset(to_edges(_to_non_strict_convex_hull(self._points)))

    @property
    def inner_edges(self) -> Set[Segment]:
        return self.edges - self.boundary

    def to_triangles_vertices(self) -> List[Vertices]:
        if len(self.points) == 3:
            return [self.points]
        adjacency = self.to_adjacency()
        result = {frozenset((edge.start, edge.end, point))
                  for edge in self.inner_edges
                  for point in adjacency[edge]}
        return [_to_ccw_triangle_vertices(tuple(vertices))
                for vertices in result]

    def update(self, edges: Iterable[Segment]) -> None:
        for edge in edges:
            self.add(edge)

    def add(self, edge: Segment) -> None:
        self._linkage[edge.start].add(edge.end)
        self._linkage[edge.end].add(edge.start)

    def remove(self, edge: Segment) -> None:
        self._linkage[edge.start].remove(edge.end)
        self._linkage[edge.end].remove(edge.start)

    def _to_non_adjacent_vertices(self, edge: Segment) -> Set[Point]:
        return _to_visible_non_adjacent_vertices(self._linkage[edge.start]
                                                 & self._linkage[edge.end],
                                                 edge)


def _to_visible_non_adjacent_vertices(candidates, edge):
    if len(candidates) <= 2:
        return candidates
    else:
        return {min(points,
                    key=edge.angle_with
                    if orientation is Orientation.COUNTERCLOCKWISE
                    else edge.reversed.angle_with)
                for (orientation,
                     points) in grouper(edge.orientation_with)(candidates)
                if orientation is not Orientation.COLLINEAR}


def delaunay(points: Sequence[Point]) -> List[Vertices]:
    return _delaunay(points).to_triangles_vertices()


def _delaunay(points: Sequence[Point]) -> Triangulation:
    result = [tuple(sorted(points,
                           key=attrgetter('x', 'y')))]
    while max(map(len, result)) > 5:
        result = list(flatten(_split(part) if len(part) > 5 else [part]
                              for part in result))
    result = [_initialize_triangulation(points) for points in result]
    while len(result) > 1:
        parts_to_merge_count = len(result) // 2 * 2
        result = ([_merge(result[offset], result[offset + 1])
                   for offset in range(0, parts_to_merge_count, 2)]
                  + result[parts_to_merge_count:])
    return result[0]


def _triangulate_three_points(points: Sequence[Point]) -> Triangulation:
    result = Triangulation(points)
    result.update(to_edges(points))
    return result


def _triangulate_four_points(points: Sequence[Point]) -> Triangulation:
    result = Triangulation(points)
    convex_hull = to_convex_hull(points)
    if len(convex_hull) == 2:
        result.update(to_edges(points))
    elif len(convex_hull) == 3:
        for vertices in _incremental_delaunay(set(points)
                                              - set(convex_hull),
                                              convex_hull):
            result.update(to_edges(vertices))
    else:
        *triangle_vertices, rest_vertex = convex_hull
        if _is_point_inside_circumcircle(triangle_vertices, rest_vertex):
            convex_hull = convex_hull[::-1]
        for vertices in (_to_ccw_triangle_vertices(convex_hull[:3]),
                         _to_ccw_triangle_vertices(convex_hull[2:]
                                                   + convex_hull[:1])):
            result.update(to_edges(vertices))
    return result


def _triangulate_five_points(points: Sequence[Point]) -> Triangulation:
    result = Triangulation(points)
    convex_hull = to_convex_hull(points)
    if len(convex_hull) == 2:
        result.update(to_edges(points))
    elif len(convex_hull) == 3:
        for vertices in _incremental_delaunay(set(points) - set(convex_hull),
                                              convex_hull):
            result.update(to_edges(vertices))
    elif len(convex_hull) == 4:
        extra_point, = set(points) - set(convex_hull)
        for edge in to_edges(convex_hull):
            if edge.orientation_with(extra_point) is Orientation.COLLINEAR:
                continue
            result.update(to_edges((edge.start, edge.end, extra_point)))
        _set_delaunay_criterion(result)
    else:
        for index in range(1, len(convex_hull) - 1):
            result.update(to_edges(convex_hull[:1]
                                   + convex_hull[index:index + 2]))
        _set_delaunay_criterion(result)
    return result


_initializers = {3: _triangulate_three_points,
                 4: _triangulate_four_points,
                 5: _triangulate_five_points}


def _initialize_triangulation(points: Sequence[Point]) -> Triangulation:
    try:
        initializer = _initializers[len(points)]
    except KeyError:
        raise ValueError('Unsupported points count: '
                         'should be one of {expected_counts}, '
                         'but found {actual_count}.'
                         .format(expected_counts=
                                 ', '.join(map(str, _initializers)),
                                 actual_count=len(points)))
    else:
        return initializer(points)


def _set_delaunay_criterion(triangulation: Triangulation) -> None:
    """
    Straightforward flip algorithm.

    Time complexity:
        O(n^2), where
        n -- points count.
    """
    adjacency = triangulation.to_adjacency()
    while True:
        no_flips = True
        for edge in triangulation.inner_edges:
            first_non_edge_vertex, second_non_edge_vertex = adjacency[edge]
            if not (_is_point_inside_circumcircle(
                    _to_ccw_triangle_vertices((first_non_edge_vertex,
                                               edge.start, edge.end)),
                    second_non_edge_vertex)
                    or _is_point_inside_circumcircle(
                            _to_ccw_triangle_vertices((second_non_edge_vertex,
                                                       edge.start, edge.end)),
                            first_non_edge_vertex)):
                continue
            replacement = to_segment(first_non_edge_vertex,
                                     second_non_edge_vertex)
            adjacency[replacement] = {edge.start, edge.end}
            adjacency[to_segment(edge.start,
                                 first_non_edge_vertex)].remove(edge.end)
            adjacency[to_segment(edge.start,
                                 second_non_edge_vertex)].remove(edge.end)
            adjacency[to_segment(first_non_edge_vertex,
                                 edge.end)].remove(edge.start)
            adjacency[to_segment(second_non_edge_vertex,
                                 edge.end)].remove(edge.start)
            (adjacency[to_segment(edge.start,
                                  first_non_edge_vertex)]
             .add(second_non_edge_vertex))
            (adjacency[to_segment(edge.start,
                                  second_non_edge_vertex)]
             .add(first_non_edge_vertex))
            (adjacency[to_segment(first_non_edge_vertex,
                                  edge.end)]
             .add(second_non_edge_vertex))
            (adjacency[to_segment(second_non_edge_vertex,
                                  edge.end)]
             .add(first_non_edge_vertex))
            del adjacency[edge]
            triangulation.remove(edge)
            triangulation.add(replacement)
            no_flips = False
        if no_flips:
            break


def _split(sequence: Sequence[Domain],
           *,
           size: int = 2) -> List[Sequence[Domain]]:
    step, offset = divmod(len(sequence), size)
    return [sequence[number * step + min(number, offset):
                     (number + 1) * step + min(number + 1, offset)]
            for number in range(size)]


class EdgeKind(IntEnum):
    LEFT = -1
    UNKNOWN = 0
    RIGHT = 1


def _merge(left: Triangulation, right: Triangulation) -> Triangulation:
    result = Triangulation(left.points + right.points)
    # operations order matters:
    # while searching for merging edges
    # both triangulations gets modified
    result.update(_to_merging_edges(left, right))
    result.update(left.edges)
    result.update(right.edges)
    return result


def _to_merging_edges(left: Triangulation,
                      right: Triangulation) -> Iterable[Segment]:
    base_edge, previous_edge_type = (_find_base_edge(left, right),
                                     EdgeKind.UNKNOWN)
    while base_edge is not None:
        yield base_edge
        base_edge, previous_edge_type = _to_next_base_edge(base_edge,
                                                           previous_edge_type,
                                                           left, right)


def _find_base_edge(left: Triangulation, right: Triangulation) -> Segment:
    candidates = iter(
            set(to_edges(_to_sub_hull(left.points + right.points)))
            - set(to_edges(_to_sub_hull(left.points)))
            - set(to_edges(_to_sub_hull(right.points))))
    result = next(candidates)
    for candidate in candidates:
        if _is_segment_not_below_another(result, candidate):
            result = candidate
    return result


def _is_segment_not_below_another(first_segment: Segment,
                                  second_segment: Segment) -> bool:
    if first_segment.start.x > first_segment.end.x:
        first_segment = first_segment.reversed
    return (first_segment.orientation_with(second_segment.start)
            is not Orientation.COUNTERCLOCKWISE
            and first_segment.orientation_with(second_segment.end)
            is not Orientation.COUNTERCLOCKWISE)


def _find_left_candidate(base_edge: Segment,
                         triangulation: Triangulation) -> Optional[Point]:
    angles = [Angle(base_edge.end, base_edge.start, point)
              for point in triangulation.linkage[base_edge.start]]
    heapq.heapify(angles)

    def to_potential_candidate(candidates_angles: List[Angle] = angles
                               ) -> Optional[Point]:
        try:
            angle = heapq.heappop(candidates_angles)
        except IndexError:
            return None
        return angle.second_ray_point

    potential_candidate = to_potential_candidate()
    if potential_candidate is None:
        return potential_candidate
    while True:
        if (base_edge.orientation_with(potential_candidate)
                is not Orientation.COUNTERCLOCKWISE):
            return None
        next_potential_candidate = to_potential_candidate()
        if next_potential_candidate is None:
            return potential_candidate
        elif _is_point_inside_circumcircle(
                _to_ccw_triangle_vertices((base_edge.start,
                                           base_edge.end,
                                           potential_candidate)),
                next_potential_candidate):
            triangulation.remove(to_segment(base_edge.start,
                                            potential_candidate))
            potential_candidate = next_potential_candidate
        else:
            return potential_candidate


def _find_right_candidate(base_edge: Segment,
                          triangulation: Triangulation) -> Optional[Point]:
    angles = [Angle(point, base_edge.end, base_edge.start)
              for point in triangulation.linkage[base_edge.end]]
    heapq.heapify(angles)

    def to_potential_candidate(candidates_angles: List[Angle] = angles
                               ) -> Optional[Point]:
        try:
            angle = heapq.heappop(candidates_angles)
        except IndexError:
            return None
        return angle.first_ray_point

    potential_candidate = to_potential_candidate()
    if potential_candidate is None:
        return potential_candidate
    while True:
        if (base_edge.orientation_with(potential_candidate)
                is not Orientation.COUNTERCLOCKWISE):
            return None
        next_potential_candidate = to_potential_candidate()
        if next_potential_candidate is None:
            return potential_candidate
        elif _is_point_inside_circumcircle(
                _to_ccw_triangle_vertices((base_edge.start,
                                           base_edge.end,
                                           potential_candidate)),
                next_potential_candidate):
            triangulation.remove(to_segment(potential_candidate,
                                            base_edge.end))
            potential_candidate = next_potential_candidate
        else:
            return potential_candidate


def _to_next_base_edge(base_edge: Segment,
                       previous_edge_kind: EdgeKind,
                       left: Triangulation,
                       right: Triangulation
                       ) -> Tuple[Optional[Segment], EdgeKind]:
    left_candidate = _find_left_candidate(base_edge, left)
    right_candidate = _find_right_candidate(base_edge, right)
    if left_candidate is None:
        if right_candidate is None:
            return None, EdgeKind.UNKNOWN
        return to_segment(base_edge.start, right_candidate), EdgeKind.RIGHT
    else:
        if right_candidate is None:
            return to_segment(left_candidate, base_edge.end), EdgeKind.LEFT
        elif previous_edge_kind is EdgeKind.LEFT:
            if not _is_point_inside_circumcircle(
                    _to_ccw_triangle_vertices((base_edge.start,
                                               base_edge.end,
                                               right_candidate)),
                    left_candidate):
                return (to_segment(base_edge.start, right_candidate),
                        EdgeKind.RIGHT)
            else:
                return to_segment(left_candidate, base_edge.end), EdgeKind.LEFT
        else:
            if not (_is_point_inside_circumcircle(
                    _to_ccw_triangle_vertices((base_edge.start,
                                               base_edge.end,
                                               left_candidate)),
                    right_candidate)):
                return to_segment(left_candidate, base_edge.end), EdgeKind.LEFT
            else:
                return (to_segment(base_edge.start, right_candidate),
                        EdgeKind.RIGHT)


def _to_boundary(polygons_vertices: Iterable[Vertices]) -> Set[Segment]:
    result = set()
    for vertices in polygons_vertices:
        result.symmetric_difference_update(to_edges(vertices))
    return result


def constrained_delaunay(points: Sequence[Point],
                         *,
                         constraints: Iterable[Segment]) -> List[Vertices]:
    result = delaunay(points)
    adjacency = _to_adjacency(result)
    neighbourhood = _to_neighbourhood(result,
                                      adjacency=adjacency)
    points_triangles = _to_points_triangles(result)
    result_edges = frozenset(flatmap(to_edges,
                                     (triangle_vertices
                                      for triangle_vertices in result)))
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
        _restore_delaunay_criterion(result,
                                    adjacency=adjacency,
                                    new_edges=new_edges - {constraint})
    return _filter_outsiders(result,
                             adjacency=adjacency,
                             boundary=boundary)


@unique
class TriangleKind(IntEnum):
    UNKNOWN = 0
    INNER = 1
    OUTER = 2


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
            triangle_vertices: Vertices,
            *,
            boundary_vertices: Container[Point] =
            frozenset(flatten((edge.start, edge.end)
                              for edge in boundary))) -> TriangleKind:
        if not all(vertex in boundary_vertices
                   for vertex in triangle_vertices):
            return TriangleKind.INNER
        edges = set(to_edges(triangle_vertices))
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
    return [triangle_vertices
            for index, triangle_vertices in enumerate(triangulation)
            if triangles_kinds[index] is TriangleKind.INNER]


def _to_points_triangles(triangulation: Sequence[Vertices]
                         ) -> Dict[Point, Set[int]]:
    result = defaultdict(set)
    for index, triangle_vertices in enumerate(triangulation):
        for vertex in triangle_vertices:
            result[vertex].add(index)
    result.default_factory = None
    return result


def _to_adjacency(triangulation: Iterable[Vertices]
                  ) -> Dict[Segment, Set[int]]:
    result = defaultdict(set)
    for index, triangle_vertices in enumerate(triangulation):
        _register_adjacent(index, triangle_vertices,
                           adjacency=result)
    result.default_factory = None
    return result


def _to_neighbourhood(triangulation: Sequence[Vertices],
                      *,
                      adjacency: Dict[Segment, Set[int]]
                      ) -> Dict[int, Set[int]]:
    result = defaultdict(set)
    for index, triangle_vertices in enumerate(triangulation):
        for edge in to_edges(triangle_vertices):
            result[index].update(adjacency[edge] - {index})
    result.default_factory = None
    return result


def _restore_delaunay_criterion(triangulation: List[Vertices],
                                *,
                                adjacency: Dict[Segment, Set[int]],
                                new_edges: Set[Segment]) -> None:
    while True:
        no_swaps = True
        for edge in new_edges:
            adjacents = adjacency[edge]
            first_adjacent_index, second_adjacent_index = adjacents
            first_adjacent = triangulation[first_adjacent_index]
            second_adjacent = triangulation[second_adjacent_index]
            quadriliteral_vertices = to_convex_hull(first_adjacent
                                                    + second_adjacent)
            if not vertices_forms_convex_polygon(quadriliteral_vertices):
                continue
            edge_points = {edge.start, edge.end}
            first_non_edge_vertex, = (set(first_adjacent)
                                      - edge_points)
            second_non_edge_vertex, = (set(second_adjacent)
                                       - edge_points)
            if not (_is_point_inside_circumcircle(first_adjacent,
                                                  second_non_edge_vertex)
                    or _is_point_inside_circumcircle(second_adjacent,
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
            triangle_vertices = triangulation[index]
            for edge in to_edges(triangle_vertices):
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
    (first_triangle_vertices,
     second_triangle_vertices) = _to_replacements(src_edge, dst_edge)
    adjacents = adjacency[src_edge]
    first_adjacent, second_adjacent = adjacents
    for edge in to_edges(first_triangle_vertices):
        adjacency[edge] -= adjacents
    for edge in to_edges(second_triangle_vertices):
        adjacency[edge] -= adjacents
    _register_adjacent(first_adjacent, first_triangle_vertices,
                       adjacency=adjacency)
    _register_adjacent(second_adjacent, second_triangle_vertices,
                       adjacency=adjacency)


def _to_replacements(src_edge: Segment,
                     dst_edge: Segment) -> Tuple[Vertices, Vertices]:
    return (_to_ccw_triangle_vertices((dst_edge.start, dst_edge.end,
                                       src_edge.start)),
            _to_ccw_triangle_vertices((dst_edge.start, dst_edge.end,
                                       src_edge.end)))


def _register_adjacent(index: int, triangle_vertices: Vertices,
                       *,
                       adjacency: Dict[Segment, Set[int]]) -> None:
    for edge in to_edges(triangle_vertices):
        adjacency[edge].add(index)
