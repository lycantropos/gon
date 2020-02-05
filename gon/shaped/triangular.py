from collections import deque
from itertools import chain
from operator import attrgetter
from typing import (Iterable,
                    List,
                    Optional,
                    Sequence,
                    Set)

from lz.functional import compose
from lz.hints import Domain
from lz.iterating import flatten
from reprit.base import generate_repr

from gon import documentation
from gon.angular import (Angle,
                         Orientation)
from gon.base import Point
from gon.linear import (IntersectionKind,
                        Segment,
                        to_interval,
                        to_segment)
from .contracts import is_point_inside_circumcircle
from .hints import Contour
from .subdivisional import QuadEdge
from .utils import to_convex_hull


class Triangulation:
    __slots__ = ('_left_edge', '_right_edge')

    def __init__(self, left_edge: QuadEdge, right_edge: QuadEdge) -> None:
        self._left_edge = left_edge
        self._right_edge = right_edge

    __repr__ = generate_repr(__init__)

    @property
    def left_edge(self) -> QuadEdge:
        return self._left_edge

    @property
    def right_edge(self) -> QuadEdge:
        return self._right_edge

    def merge_with(self, other: 'Triangulation') -> 'Triangulation':
        _merge(self._find_base_edge(other))
        return Triangulation(self._left_edge, other._right_edge)

    def _find_base_edge(self, other: 'Triangulation') -> QuadEdge:
        while True:
            if (self._right_edge.orientation_with(other._left_edge.start)
                    is Orientation.COUNTERCLOCKWISE):
                self._right_edge = self._right_edge.left_from_end
            elif (other._left_edge.orientation_with(self._right_edge.start)
                  is Orientation.CLOCKWISE):
                other._left_edge = other._left_edge.right_from_end
            else:
                break
        base_edge = other._left_edge.opposite.connect(self._right_edge)
        if self._right_edge.start == self._left_edge.start:
            self._left_edge = base_edge.opposite
        if other._left_edge.start == other._right_edge.start:
            other._right_edge = base_edge
        return base_edge

    def to_triangles_contours(self) -> List[Contour]:
        return list(self._to_triangles_vertices())

    def _to_triangles_vertices(self) -> Iterable[Contour]:
        visited_vertices_sets = set()
        edges = self.to_edges()
        edges_endpoints = {frozenset((edge.start, edge.end)) for edge in edges}
        for edge in edges:
            if (edge.orientation_with(edge.left_from_start.end)
                    is Orientation.COUNTERCLOCKWISE):
                vertices = (edge.start, edge.end, edge.left_from_start.end)
                vertices_set = frozenset(vertices)
                if vertices_set not in visited_vertices_sets:
                    if (frozenset((edge.end, edge.left_from_start.end))
                            not in edges_endpoints):
                        continue
                    visited_vertices_sets.add(vertices_set)
                    yield vertices

    @staticmethod
    def to_non_adjacent_vertices(edge: QuadEdge) -> Set[Point]:
        return {neighbour.end
                for neighbour in Triangulation._to_incidents(edge)}

    def to_edges(self) -> Set[QuadEdge]:
        result = {self.right_edge, self.left_edge}
        queue = [self.right_edge.left_from_start,
                 self.right_edge.left_from_end,
                 self.right_edge.right_from_start,
                 self.right_edge.right_from_end]
        while queue:
            edge = queue.pop()
            if edge not in result:
                result.update((edge, edge.opposite))
                queue.extend((edge.left_from_start, edge.left_from_end,
                              edge.right_from_start, edge.right_from_end))
        return result

    def to_boundary_edges(self) -> Set[QuadEdge]:
        return set(flatten((edge, edge.opposite)
                           for edge in self._to_boundary_edges()))

    def _to_boundary_edges(self) -> Iterable[QuadEdge]:
        start = self.left_edge
        edge = start
        while True:
            yield edge
            if edge.right_from_end is start:
                break
            edge = edge.right_from_end

    def to_inner_edges(self) -> Set[QuadEdge]:
        return self.to_edges() - self.to_boundary_edges()

    @staticmethod
    def to_neighbours(edge: QuadEdge) -> Set[QuadEdge]:
        return set(Triangulation._to_neighbours(edge))

    @staticmethod
    def _to_neighbours(edge: QuadEdge) -> Iterable[QuadEdge]:
        yield from Triangulation._to_incidents(edge)
        yield from Triangulation._to_incidents(edge.opposite)

    @staticmethod
    def _to_incidents(edge: QuadEdge) -> Iterable[QuadEdge]:
        if (edge.orientation_with(edge.right_from_start.end)
                is Orientation.CLOCKWISE):
            yield edge.right_from_start
        if (edge.orientation_with(edge.left_from_start.end)
                is Orientation.COUNTERCLOCKWISE):
            yield edge.left_from_start

    def delete(self, edge: QuadEdge) -> None:
        if edge is self.right_edge or edge.opposite is self.right_edge:
            self._right_edge = self._right_edge.right_from_end.opposite
        if edge is self.left_edge or edge.opposite is self.left_edge:
            self._left_edge = self._left_edge.left_from_start
        edge.delete()


@documentation.setup(docstring='Returns Delaunay triangulation of the points.',
                     reference='http://tiny.cc/delaunay_triangulation',
                     time_complexity='O(n * log n), where\n'
                                     'n -- polygon\'s vertices count')
def delaunay(points: Sequence[Point]) -> Triangulation:
    result = [tuple(sorted(points,
                           key=attrgetter('x', 'y')))]
    while max(map(len, result)) > max(_initializers):
        result = list(flatten(_split(part) if len(part) > max(_initializers)
                              else [part]
                              for part in result))
    result = [_initialize_triangulation(points) for points in result]
    while len(result) > 1:
        parts_to_merge_count = len(result) // 2 * 2
        result = ([result[offset].merge_with(result[offset + 1])
                   for offset in range(0, parts_to_merge_count, 2)]
                  + result[parts_to_merge_count:])
    return result[0]


def _split(sequence: Sequence[Domain],
           *,
           size: int = 2) -> List[Sequence[Domain]]:
    step, offset = divmod(len(sequence), size)
    return [sequence[number * step + min(number, offset):
                     (number + 1) * step + min(number + 1, offset)]
            for number in range(size)]


def _triangulate_two_points(sorted_points: Sequence[Point]) -> Triangulation:
    first_edge = QuadEdge.factory(*sorted_points)
    return Triangulation(first_edge, first_edge.opposite)


def _triangulate_three_points(sorted_points: Sequence[Point]) -> Triangulation:
    left_point, mid_point, right_point = sorted_points
    first_edge, second_edge = (QuadEdge.factory(left_point, mid_point),
                               QuadEdge.factory(mid_point, right_point))
    first_edge.opposite.splice(second_edge)
    orientation = Angle(left_point, mid_point, right_point).orientation
    if orientation is Orientation.COUNTERCLOCKWISE:
        third_edge = second_edge.connect(first_edge)
        return Triangulation(third_edge.opposite, third_edge)
    elif orientation is Orientation.CLOCKWISE:
        second_edge.connect(first_edge)
        return Triangulation(first_edge, second_edge.opposite)
    else:
        return Triangulation(first_edge, second_edge.opposite)


_initializers = {2: _triangulate_two_points,
                 3: _triangulate_three_points}


def _initialize_triangulation(points: Sequence[Point]) -> Triangulation:
    return _initializers[len(points)](points)


def _merge(base_edge: QuadEdge) -> None:
    while True:
        left_candidate = _to_left_candidate(base_edge)
        right_candidate = _to_right_candidate(base_edge)
        if left_candidate is right_candidate is None:
            break
        elif (left_candidate is None
              or right_candidate is not None
              and is_point_inside_circumcircle(left_candidate.end,
                                               base_edge.end,
                                               base_edge.start,
                                               right_candidate.end)):
            base_edge = right_candidate.connect(base_edge.opposite)
        else:
            base_edge = base_edge.opposite.connect(left_candidate.opposite)


def _to_left_candidate(base_edge: QuadEdge) -> Optional[QuadEdge]:
    result = base_edge.opposite.left_from_start
    if base_edge.orientation_with(result.end) is not Orientation.CLOCKWISE:
        return None
    while (is_point_inside_circumcircle(base_edge.end, base_edge.start,
                                        result.end, result.left_from_start.end)
           and (base_edge.orientation_with(result.left_from_start.end)
                is Orientation.CLOCKWISE)):
        next_candidate = result.left_from_start
        result.delete()
        result = next_candidate
    return result


def _to_right_candidate(base_edge: QuadEdge) -> Optional[QuadEdge]:
    result = base_edge.right_from_start
    if base_edge.orientation_with(result.end) is not Orientation.CLOCKWISE:
        return None
    while (is_point_inside_circumcircle(base_edge.end, base_edge.start,
                                        result.end,
                                        result.right_from_start.end)
           and (base_edge.orientation_with(result.right_from_start.end)
                is Orientation.CLOCKWISE)):
        next_candidate = result.right_from_start
        result.delete()
        result = next_candidate
    return result


@documentation.setup(docstring='Returns constrained Delaunay triangulation '
                               'of the points.',
                     reference='http://tiny.cc/constrained_delaunay',
                     time_complexity='O(n * log n) for convex polygons,\n'
                                     'O(n^2) for concave polygons, where\n'
                                     'n -- polygon\'s vertices count')
def constrained_delaunay(points: Sequence[Point],
                         *,
                         boundary: Sequence[Segment],
                         extra_constraints: Optional[Iterable[Segment]] = None
                         ) -> Triangulation:
    result = delaunay(points)
    initial_boundary_segments = frozenset(map(_edge_to_segment,
                                              result.to_boundary_edges()))
    if not extra_constraints and all(edge in initial_boundary_segments
                                     for edge in boundary):
        return result
    _set_constraints(result,
                     constraints=(boundary if extra_constraints is None
                                  else chain(boundary, extra_constraints)))
    _set_boundary(result,
                  boundary=boundary)
    return result


delaunay_contours = compose(Triangulation.to_triangles_contours,
                            delaunay)
constrained_delaunay_contours = compose(Triangulation.to_triangles_contours,
                                        constrained_delaunay)


def _set_constraints(triangulation: Triangulation,
                     *,
                     constraints: Iterable[Segment]) -> None:
    triangulation_segments = set(map(_edge_to_segment,
                                     triangulation.to_edges()))
    for constraint in constraints:
        if constraint in triangulation_segments:
            continue
        crossed_edges = _find_crossed_edges(constraint, triangulation)
        new_edges = _resolve_crossings(constraint, triangulation,
                                       crossed_edges=crossed_edges)
        _set_delaunay_criterion(edge
                                for edge in new_edges
                                if _edge_to_segment(edge) != constraint)


@documentation.setup(docstring='Straightforward flip algorithm.',
                     time_complexity='O(n^2), where\n'
                                     'n -- points count')
def _set_delaunay_criterion(target_edges: Iterable[QuadEdge]) -> None:
    target_edges = set(target_edges)
    while True:
        edges_to_swap = {edge
                         for edge in target_edges
                         if _should_be_swapped(edge)}
        if not edges_to_swap:
            break
        for edge in edges_to_swap:
            edge.swap()
        target_edges.difference_update(edges_to_swap)


def _should_be_swapped(edge: QuadEdge) -> bool:
    return (_points_form_convex_quadrilateral(
            (edge.start, edge.left_from_start.end,
             edge.end, edge.right_from_start.end))
            and _is_non_delaunay(edge))


def _is_non_delaunay(edge: QuadEdge) -> bool:
    return (is_point_inside_circumcircle(edge.start, edge.end,
                                         edge.left_from_start.end,
                                         edge.right_from_start.end)
            or is_point_inside_circumcircle(edge.end, edge.start,
                                            edge.right_from_start.end,
                                            edge.left_from_start.end))


def _set_boundary(triangulation: Triangulation,
                  *,
                  boundary: Sequence[Segment]) -> None:
    boundary = frozenset(boundary)
    non_boundary = {edge
                    for edge in triangulation.to_boundary_edges()
                    if _edge_to_segment(edge) not in boundary}
    while non_boundary:
        edge = non_boundary.pop()
        non_boundary.remove(edge.opposite)
        candidates = triangulation.to_neighbours(edge)
        triangulation.delete(edge)
        non_boundary.update(flatten(
                (candidate, candidate.opposite)
                for candidate in candidates
                if _edge_to_segment(candidate) not in boundary))


def _resolve_crossings(constraint: Segment,
                       triangulation: Triangulation,
                       *,
                       crossed_edges: Set[QuadEdge]) -> Set[QuadEdge]:
    open_constraint = to_interval(constraint.start, constraint.end,
                                  with_start=False,
                                  with_end=False)
    result = set()
    crossed_edges = deque(crossed_edges,
                          maxlen=len(crossed_edges))
    while crossed_edges:
        edge = crossed_edges.popleft()
        (first_non_edge_vertex,
         second_non_edge_vertex) = triangulation.to_non_adjacent_vertices(edge)
        if _points_form_convex_quadrilateral((edge.start, edge.end,
                                              first_non_edge_vertex,
                                              second_non_edge_vertex)):
            edge.swap()
            if (_edge_to_segment(edge).relationship_with(open_constraint)
                    is IntersectionKind.CROSS):
                crossed_edges.append(edge)
            else:
                result.add(edge)
        else:
            crossed_edges.append(edge)
    return result


def _find_crossed_edges(constraint: Segment,
                        triangulation: Triangulation) -> Set[QuadEdge]:
    open_constraint = to_interval(constraint.start, constraint.end,
                                  with_start=False,
                                  with_end=False)
    return set({_edge_to_segment(edge): edge
                for edge in triangulation.to_inner_edges()
                if _edge_to_segment(edge).relationship_with(open_constraint)
                is IntersectionKind.CROSS}
               .values())


def _points_form_convex_quadrilateral(points: Sequence[Point]) -> bool:
    vertices = to_convex_hull(points)
    return (len(vertices) == 4
            and all(vertex in points for vertex in vertices))


def _edge_to_segment(edge: QuadEdge) -> Segment:
    return to_segment(edge.start, edge.end)
