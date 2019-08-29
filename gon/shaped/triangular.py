from collections import deque
from enum import (IntEnum,
                  unique)
from itertools import chain
from operator import attrgetter
from reprlib import recursive_repr
from typing import (AbstractSet,
                    Dict,
                    Iterable,
                    Iterator,
                    List,
                    MutableMapping,
                    Optional,
                    Sequence,
                    Set,
                    Tuple)

from lz.hints import Domain
from lz.iterating import (flatten,
                          grouper,
                          pairwise)
from reprit.base import generate_repr

from gon.angular import (Angle,
                         Orientation)
from gon.base import (Point,
                      Vector)
from gon.linear import (IntersectionKind,
                        Segment,
                        to_interval,
                        to_segment)
from .hints import Vertices
from .utils import (_to_sub_hull,
                    to_convex_hull,
                    to_edges,
                    to_nested_mapping)


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


class Feather:
    __slots__ = ('_start', '_end', '_left', '_right')

    def __init__(self, start: Point, end: Point,
                 *,
                 left: Optional['Feather'] = None,
                 right: Optional['Feather'] = None):
        self._start = start
        self._end = end
        self._left = left
        self._right = right

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def start(self) -> Point:
        return self._start

    @property
    def end(self) -> Point:
        return self._end

    @property
    def left(self) -> Optional['Feather']:
        return self._left

    @left.setter
    def left(self, value: 'Feather') -> None:
        if self._left is None:
            self._left, value._right = value, self
            self._right, value._left = value, self
        else:
            (self._left._right,
             value._left, value._right) = value, self._left, self
            self._left = value

    @property
    def right(self) -> Optional['Feather']:
        return self._right

    @right.setter
    def right(self, value: 'Feather') -> None:
        if self._right is None:
            self._right, value._left = value, self
            self._left, value._right = value, self
        else:
            (self._right._left,
             value._right, value._left) = value, self._right, self
            self._right = value

    def take_out(self) -> None:
        if self._left is not self._right:
            self._left._right = self._right
            self._right._left = self._left
        else:
            self._left._right = self._left._left = None
        self._left = self._right = None

    def orientation_with(self, point: Point) -> Orientation:
        return self.angle_with(point).orientation

    def angle_with(self, point: Point) -> Angle:
        return Angle(self._end, self._start, point)


class Wing:
    __slots__ = ('_start', '_current', '_feathers')

    def __init__(self, start: Point,
                 *,
                 current: Optional[Feather] = None,
                 feathers: Optional[Dict[Point, Feather]] = None):
        self._start = start
        self._current = current
        if feathers is None:
            feathers = {}
        self._feathers = feathers

    __repr__ = generate_repr(__init__)

    @property
    def start(self) -> Point:
        return self._start

    @property
    def current(self) -> Feather:
        return self._current

    @property
    def feathers(self) -> Dict[Point, Feather]:
        return self._feathers

    def iter_edges(self) -> Iterable[Segment]:
        return (to_segment(feather.start, feather.end)
                for feather in _iter_feathers(self._current))

    def insert(self, end: Point) -> None:
        feather = Feather(self._start, end)
        self._feathers[end] = feather
        if self._current is None:
            self._current = feather
        elif (self._current.orientation_with(end)
              is Orientation.COUNTERCLOCKWISE):
            if self._current.left is not None:
                self.approach_lefter(end)
            self._current.left = feather
            self._current = feather
        else:
            if self._current.right is not None:
                self.approach_righter(end)
            self._current.right = feather
            self._current = feather

    def remove(self, end: Point) -> None:
        target_feather = self._feathers.pop(end)
        self._current = target_feather.left or target_feather.right
        target_feather.take_out()

    def approach_righter(self, point: Point) -> None:
        angle = self._current.angle_with(point).reversed
        while True:
            next_angle = self._current.right.angle_with(point).reversed
            if next_angle > angle:
                break
            self.step_to_right()
            angle = next_angle

    def approach_lefter(self, point: Point) -> None:
        angle = self._current.angle_with(point)
        while True:
            next_angle = self._current.left.angle_with(point)
            if next_angle > angle:
                break
            self.step_to_left()
            angle = next_angle

    def step_to_right(self) -> None:
        self._current = self._current.right

    def step_to_left(self) -> None:
        self._current = self._current.left


def _iter_feathers(start: Feather,
                   *,
                   orientation: Orientation = Orientation.COUNTERCLOCKWISE
                   ) -> Iterable[Feather]:
    to_next = attrgetter('left' if orientation is Orientation.COUNTERCLOCKWISE
                         else 'right')
    feather = start
    while True:
        yield feather
        feather = to_next(feather)
        if feather is None or feather is start:
            break


class Triangulation:
    def __init__(self, points: Sequence[Point],
                 *,
                 wings: Optional[MutableMapping[Point, Wing]] = None) -> None:
        self._points = tuple(points)
        if wings is None:
            wings = {point: Wing(point) for point in points}
        self._wings = wings

    __repr__ = generate_repr(__init__)

    @property
    def points(self) -> Sequence[Point]:
        return self._points

    @property
    def wings(self) -> MutableMapping[Point, Wing]:
        return self._wings

    @property
    def edges(self) -> AbstractSet[Segment]:
        return set(self._iter_edges())

    def _iter_edges(self) -> Iterable[Segment]:
        for wing in self._wings.values():
            yield from wing.iter_edges()

    @property
    def boundary(self) -> AbstractSet[Segment]:
        return {edge
                for edge in self.edges
                if len(self.to_non_adjacent_vertices(edge)) == 1}

    @property
    def inner_edges(self) -> AbstractSet[Segment]:
        return self.edges - self.boundary

    def to_triangles_vertices(self) -> List[Vertices]:
        if len(self.points) == 3:
            return [_to_ccw_triangle_vertices(self.points)]
        result = {frozenset((edge.start, edge.end, point))
                  for edge in self.inner_edges
                  for point in self.to_non_adjacent_vertices(edge)}
        return [_to_ccw_triangle_vertices(tuple(vertices))
                for vertices in result]

    def add(self, edge: Segment) -> None:
        self._wings[edge.start].insert(edge.end)
        self._wings[edge.end].insert(edge.start)

    def update(self, edges: Iterable[Segment]) -> None:
        for edge in edges:
            self.add(edge)

    def remove(self, edge: Segment) -> None:
        self._wings[edge.start].remove(edge.end)
        self._wings[edge.end].remove(edge.start)

    def replace(self, edge: Segment, replacement: Segment) -> None:
        self.remove(edge)
        self.add(replacement)

    def to_non_adjacent_vertices(self, edge: Segment) -> Set[Point]:
        start_feather = self._wings[edge.start].feathers[edge.end]
        end_feather = self._wings[edge.end].feathers[edge.start]
        candidates = set()
        if start_feather.left.end == end_feather.right.end:
            candidates.add(start_feather.left.end)
        if start_feather.right.end == end_feather.left.end:
            candidates.add(start_feather.right.end)
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
    while max(map(len, result)) > max(_initializers):
        result = list(flatten(_split(part) if len(part) > max(_initializers)
                              else [part]
                              for part in result))
    result = [_initialize_triangulation(points) for points in result]
    while len(result) > 1:
        parts_to_merge_count = len(result) // 2 * 2
        result = ([_merge(result[offset], result[offset + 1])
                   for offset in range(0, parts_to_merge_count, 2)]
                  + result[parts_to_merge_count:])
    return result[0]


def _triangulate_two_points(points: Sequence[Point]) -> Triangulation:
    result = Triangulation(points)
    result.add(to_segment(*points))
    return result


def _triangulate_three_points(points: Sequence[Point]) -> Triangulation:
    result = Triangulation(points)
    if Angle(*points).orientation is Orientation.COLLINEAR:
        edges = [to_segment(start, end) for start, end in pairwise(points)]
    else:
        edges = list(to_edges(points))
    result.update(edges)
    return result


_initializers = {2: _triangulate_two_points,
                 3: _triangulate_three_points}


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


def _set_delaunay_criterion(triangulation: Triangulation,
                            *,
                            target_edges: Optional[AbstractSet[Segment]] = None
                            ) -> None:
    """
    Straightforward flip algorithm.

    Time complexity:
        O(n^2), where
        n -- points count.
    """
    if target_edges is None:
        target_edges = set(triangulation.inner_edges)
    while True:
        removed_edges = set()
        for edge in target_edges:
            first_non_edge_vertex, second_non_edge_vertex = (
                triangulation.to_non_adjacent_vertices(edge))
            if not _points_form_convex_quadrilateral((edge.start, edge.end,
                                                      first_non_edge_vertex,
                                                      second_non_edge_vertex)):
                continue
            if not (_is_point_inside_circumcircle(
                    _to_ccw_triangle_vertices((first_non_edge_vertex,
                                               edge.start, edge.end)),
                    second_non_edge_vertex)
                    or _is_point_inside_circumcircle(
                            _to_ccw_triangle_vertices((second_non_edge_vertex,
                                                       edge.start, edge.end)),
                            first_non_edge_vertex)):
                continue
            anti_diagonal = to_segment(first_non_edge_vertex,
                                       second_non_edge_vertex)
            removed_edges.add(edge)
            triangulation.replace(edge, anti_diagonal)
        if not removed_edges:
            break
        target_edges.difference_update(removed_edges)


def _split(sequence: Sequence[Domain],
           *,
           size: int = 2) -> List[Sequence[Domain]]:
    step, offset = divmod(len(sequence), size)
    return [sequence[number * step + min(number, offset):
                     (number + 1) * step + min(number + 1, offset)]
            for number in range(size)]


@unique
class EdgeKind(IntEnum):
    LEFT = -1
    UNKNOWN = 0
    RIGHT = 1


def _merge(left: Triangulation, right: Triangulation) -> Triangulation:
    merging_edges = list(_to_merging_edges(left, right))
    result = Triangulation(left.points + right.points,
                           wings=to_nested_mapping(left.wings, right.wings))
    result.update(merging_edges)
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
    def to_potential_candidates() -> Iterator[Point]:
        wing = triangulation.wings[base_edge.start]
        if (wing.current.orientation_with(base_edge.end)
                is Orientation.COUNTERCLOCKWISE):
            if wing.current.left is not None:
                wing.approach_lefter(base_edge.end)
                assert (wing.current.orientation_with(base_edge.end)
                        is Orientation.COUNTERCLOCKWISE)
                wing.step_to_left()
        else:
            if wing.current.right is not None:
                assert (wing.current.orientation_with(base_edge.end)
                        is Orientation.CLOCKWISE)
                wing.approach_righter(base_edge.end)
        for feather in _iter_feathers(wing.current):
            yield feather.end

    potential_candidates = to_potential_candidates()
    potential_candidate = next(potential_candidates, None)
    if potential_candidate is None:
        return potential_candidate
    while True:
        if (base_edge.orientation_with(potential_candidate)
                is not Orientation.COUNTERCLOCKWISE):
            return None
        next_potential_candidate = next(potential_candidates, None)
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
    def to_potential_candidates() -> Iterator[Point]:
        wing = triangulation.wings[base_edge.end]
        if (wing.current.orientation_with(base_edge.start)
                is Orientation.CLOCKWISE):
            if wing.current.right is not None:
                wing.approach_righter(base_edge.start)
                assert (wing.current.orientation_with(base_edge.start)
                        is Orientation.CLOCKWISE)
                wing.step_to_right()
        else:
            if wing.current.left is not None:
                assert (wing.current.orientation_with(base_edge.start)
                        is Orientation.COUNTERCLOCKWISE)
                wing.approach_lefter(base_edge.start)
        for feather in _iter_feathers(wing.current,
                                      orientation=Orientation.CLOCKWISE):
            yield feather.end

    potential_candidates = to_potential_candidates()
    potential_candidate = next(potential_candidates, None)
    if potential_candidate is None:
        return potential_candidate
    while True:
        if (base_edge.orientation_with(potential_candidate)
                is not Orientation.COUNTERCLOCKWISE):
            return None
        next_potential_candidate = next(potential_candidates, None)
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


def constrained_delaunay(points: Sequence[Point],
                         *,
                         boundary: Sequence[Segment],
                         extra_constraints: Optional[Iterable[Segment]] = None
                         ) -> List[Vertices]:
    result = _delaunay(points)
    if not extra_constraints and all(edge in result.boundary
                                     for edge in boundary):
        return result.to_triangles_vertices()
    _set_constraints(result,
                     constraints=(boundary if extra_constraints is None
                                  else chain(boundary, extra_constraints)))
    _set_boundary(result,
                  boundary=boundary)
    return result.to_triangles_vertices()


def _set_constraints(triangulation: Triangulation,
                     *,
                     constraints: Iterable[Segment]) -> None:
    triangulation_edges = frozenset(triangulation.edges)
    for constraint in constraints:
        if constraint in triangulation_edges:
            continue
        crossed_edges = _find_crossed_edges(constraint, triangulation)
        new_edges = _resolve_crossings(constraint, triangulation,
                                       crossed_edges=crossed_edges)
        _set_delaunay_criterion(triangulation,
                                target_edges=new_edges - {constraint})


def _set_boundary(triangulation: Triangulation,
                  *,
                  boundary: Sequence[Segment]) -> None:
    boundary = frozenset(boundary)
    non_boundary = set(triangulation.boundary) - boundary
    while non_boundary:
        edge = non_boundary.pop()
        non_edge_vertex, = triangulation.to_non_adjacent_vertices(edge)
        triangulation.remove(edge)
        candidates = (to_segment(edge.start, non_edge_vertex),
                      to_segment(non_edge_vertex, edge.end))
        non_boundary.update(candidate
                            for candidate in candidates
                            if candidate not in boundary)


def _resolve_crossings(constraint: Segment,
                       triangulation: Triangulation,
                       *,
                       crossed_edges: Set[Segment]) -> Set[Segment]:
    open_constraint = to_interval(constraint.start, constraint.end,
                                  start_inclusive=False,
                                  end_inclusive=False)
    result = set()
    crossed_edges = deque(crossed_edges,
                          maxlen=len(crossed_edges))
    while crossed_edges:
        edge = crossed_edges.popleft()
        (first_non_edge_vertex,
         second_non_edge_vertex) = triangulation.to_non_adjacent_vertices(edge)
        if not _points_form_convex_quadrilateral((edge.start, edge.end,
                                                  first_non_edge_vertex,
                                                  second_non_edge_vertex)):
            crossed_edges.append(edge)
            continue
        anti_diagonal = to_segment(first_non_edge_vertex,
                                   second_non_edge_vertex)
        triangulation.replace(edge, anti_diagonal)
        if (anti_diagonal.relationship_with(open_constraint)
                is IntersectionKind.CROSS):
            crossed_edges.append(anti_diagonal)
        else:
            result.add(anti_diagonal)
    return result


def _points_form_convex_quadrilateral(points: Sequence[Point]) -> bool:
    vertices = to_convex_hull(points)
    return (len(vertices) == 4
            and all(vertex in points for vertex in vertices))


def _find_crossed_edges(constraint: Segment,
                        triangulation: Triangulation) -> Set[Segment]:
    open_constraint = to_interval(constraint.start, constraint.end,
                                  start_inclusive=False,
                                  end_inclusive=False)
    return {edge
            for edge in triangulation.inner_edges
            if edge.relationship_with(open_constraint)
            is IntersectionKind.CROSS}
