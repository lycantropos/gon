from collections import deque
from itertools import chain
from operator import attrgetter
from typing import (Iterable,
                    List,
                    Optional,
                    Sequence,
                    Set)

from lz.hints import Domain
from lz.iterating import flatten
from reprit.base import generate_repr

from gon.angular import (Angle,
                         Orientation)
from gon.base import Point
from gon.linear import (IntersectionKind,
                        Segment,
                        to_interval,
                        to_segment)
from .contracts import is_point_inside_circumcircle
from .hints import Vertices
from .utils import to_convex_hull


class QuadEdge:
    __slots__ = ('_start', '_rotated', '_left_from_start')

    def __init__(self,
                 start: Optional[Point] = None,
                 left_from_start: Optional['QuadEdge'] = None,
                 rotated: Optional['QuadEdge'] = None) -> None:
        self._start = start
        self._left_from_start = left_from_start
        self._rotated = rotated

    def __repr__(self) -> str:
        return (type(self).__qualname__
                + '(' + 'start=' + repr(self.start) + ', '
                + 'end=' + repr(self.end) + ')')

    @property
    def start(self) -> Point:
        """
        aka "Org" in L. Guibas and J. Stolfi notation.
        """
        return self._start

    @property
    def end(self) -> Point:
        """
        aka "Dest" in L. Guibas and J. Stolfi notation.
        """
        return self.opposite.start

    @property
    def rotated(self) -> 'QuadEdge':
        """
        aka "Rot" in L. Guibas and J. Stolfi notation.
        """
        return self._rotated

    @rotated.setter
    def rotated(self, value: 'QuadEdge') -> None:
        self._rotated = value

    @property
    def opposite(self) -> 'QuadEdge':
        """
        aka "Sym" in L. Guibas and J. Stolfi notation.
        """
        return self.rotated.rotated

    @property
    def left_from_start(self) -> 'QuadEdge':
        """
        aka "Onext" in L. Guibas and J. Stolfi notation.
        """
        return self._left_from_start

    @left_from_start.setter
    def left_from_start(self, value: 'QuadEdge') -> None:
        self._left_from_start = value

    @property
    def right_from_start(self) -> 'QuadEdge':
        """
        aka "Oprev" in L. Guibas and J. Stolfi notation.
        """
        return self.rotated.left_from_start.rotated

    @property
    def left_in_start(self) -> 'QuadEdge':
        """
        aka "Lprev" in L. Guibas and J. Stolfi notation.
        """
        return self.left_from_start.opposite

    @property
    def right_in_start(self) -> 'QuadEdge':
        """
        aka "Rprev" in L. Guibas and J. Stolfi notation.
        """
        return self.right_from_start.opposite

    @property
    def right_from_end(self) -> 'QuadEdge':
        """
        aka "Rprev" in L. Guibas and J. Stolfi notation.
        """
        return self.opposite.left_from_start

    @property
    def left_from_end(self) -> 'QuadEdge':
        """
        aka "Lnext" in L. Guibas and J. Stolfi notation.
        """
        return self.rotated.opposite.left_from_start.rotated

    @classmethod
    def factory(cls, start: Point, end: Point) -> 'QuadEdge':
        result, opposite = cls(start), cls(end)
        rotated, triple_rotated = cls(), cls()
        result.left_from_start = result
        opposite.left_from_start = opposite
        rotated.left_from_start = triple_rotated
        triple_rotated.left_from_start = rotated
        result.rotated = rotated
        rotated.rotated = opposite
        opposite.rotated = triple_rotated
        triple_rotated.rotated = result
        return result

    def splice(self, other: 'QuadEdge') -> None:
        alpha = self.left_from_start.rotated
        beta = other.left_from_start.rotated
        self.left_from_start, other.left_from_start = (other.left_from_start,
                                                       self.left_from_start)
        alpha.left_from_start, beta.left_from_start = (beta.left_from_start,
                                                       alpha.left_from_start)

    def swap(self) -> None:
        side = self.right_from_start
        opposite = self.opposite
        opposite_side = opposite.right_from_start
        self.splice(side)
        opposite.splice(opposite_side)
        self.splice(side.left_from_end)
        opposite.splice(opposite_side.left_from_end)
        self._start = side.end
        opposite._start = opposite_side.end

    def connect(self, other: 'QuadEdge') -> 'QuadEdge':
        result = QuadEdge.factory(self.end, other.start)
        result.splice(self.left_from_end)
        result.opposite.splice(other)
        return result

    def delete(self) -> None:
        self.splice(self.right_from_start)
        self.opposite.splice(self.opposite.right_from_start)

    def angle_with(self, point: Point) -> Angle:
        return Angle(self.end, self.start, point)

    def orientation_with(self, point: Point) -> Orientation:
        return self.angle_with(point).orientation


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

    def to_triangles_vertices(self) -> List[Vertices]:
        return list(self._to_triangles_vertices())

    def _to_triangles_vertices(self) -> Iterable[Vertices]:
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
        result = set()
        start = self.right_edge
        edge = start
        while True:
            result.update((edge, edge.opposite))
            if edge.left_in_start is start:
                break
            edge = edge.left_in_start
        return result

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
        elif edge is self.left_edge or edge.opposite is self.left_edge:
            self._left_edge = self._left_edge.left_from_start
        edge.delete()


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
    try:
        initializer = _initializers[len(points)]
    except KeyError:
        expected_counts = ', '.join(map(str, _initializers))
        raise ValueError('Unsupported points count: '
                         'should be one of {expected_counts}, '
                         'but found {actual_count}.'
                         .format(expected_counts=expected_counts,
                                 actual_count=len(points)))
    else:
        return initializer(points)


def _merge(base_edge: QuadEdge) -> None:
    while True:
        left_candidate = _to_left_candidate(base_edge)
        right_candidate = _to_right_candidate(base_edge)
        left_candidate_is_on_the_right = (
                base_edge.orientation_with(left_candidate.end)
                is Orientation.CLOCKWISE)
        right_candidate_is_on_the_right = (
                base_edge.orientation_with(right_candidate.end)
                is Orientation.CLOCKWISE)
        if not (left_candidate_is_on_the_right
                or right_candidate_is_on_the_right):
            break
        left_triangle_vertices = (left_candidate.end, base_edge.end,
                                  base_edge.start)
        right_triangle_vertices = (base_edge.end, base_edge.start,
                                   right_candidate.end)
        if not left_candidate_is_on_the_right:
            if (is_point_inside_circumcircle(right_triangle_vertices,
                                             right_candidate.left_from_end.end)
                    and (right_candidate.left_from_end.end
                         not in right_triangle_vertices)):
                base_edge = right_candidate.connect(base_edge.opposite)
                base_edge.delete()
            else:
                base_edge = right_candidate.connect(base_edge.opposite)
        elif not right_candidate_is_on_the_right:
            if (is_point_inside_circumcircle(left_triangle_vertices,
                                             left_candidate.right_from_end.end)
                    and left_candidate.right_from_end.end
                    not in left_triangle_vertices):
                base_edge = base_edge.opposite.connect(left_candidate.opposite)
                base_edge.delete()
            else:
                base_edge = base_edge.opposite.connect(left_candidate.opposite)
        elif is_point_inside_circumcircle(right_triangle_vertices,
                                          left_candidate.end):
            if (is_point_inside_circumcircle(left_triangle_vertices,
                                             right_candidate.end)
                    or (is_point_inside_circumcircle(
                            left_triangle_vertices,
                            left_candidate.right_from_end.end)
                        and (left_candidate.right_from_end.end
                             not in left_triangle_vertices))):
                base_edge = base_edge.opposite.connect(left_candidate.opposite)
                base_edge.delete()
            else:
                base_edge = base_edge.opposite.connect(left_candidate.opposite)
        else:
            if (is_point_inside_circumcircle(right_triangle_vertices,
                                             right_candidate.left_from_end.end)
                    and (right_candidate.left_from_end.end
                         not in right_triangle_vertices)):
                base_edge = right_candidate.connect(base_edge.opposite)
                base_edge.delete()
            else:
                base_edge = right_candidate.connect(base_edge.opposite)


def _to_left_candidate(base_edge: QuadEdge) -> QuadEdge:
    result = base_edge.opposite.left_from_start
    if base_edge.orientation_with(result.end) is Orientation.CLOCKWISE:
        while (is_point_inside_circumcircle((base_edge.end, base_edge.start,
                                             result.end),
                                            result.left_from_start.end)
               and result.left_from_start.end not in (base_edge.end,
                                                      base_edge.start,
                                                      result.end)
               and (base_edge.orientation_with(result.left_from_start.end)
                    is Orientation.CLOCKWISE)):
            next_left_candidate = result.left_from_start
            result.delete()
            result = next_left_candidate
    return result


def _to_right_candidate(base_edge: QuadEdge) -> QuadEdge:
    result = base_edge.right_from_start
    if base_edge.orientation_with(result.end) is Orientation.CLOCKWISE:
        while (is_point_inside_circumcircle((base_edge.end, base_edge.start,
                                             result.end),
                                            result.right_from_start.end)
               and result.right_from_start.end not in (base_edge.end,
                                                       base_edge.start,
                                                       result.end)
               and base_edge.orientation_with(result.right_from_start.end)
               is Orientation.CLOCKWISE):
            next_right_candidate = result.right_from_start
            result.delete()
            result = next_right_candidate
    return result


def delaunay(points: Sequence[Point]) -> List[Vertices]:
    return (_delaunay(sorted(points,
                             key=attrgetter('x', 'y')))
            .to_triangles_vertices())


def constrained_delaunay(points: Sequence[Point],
                         *,
                         boundary: Sequence[Segment],
                         extra_constraints: Optional[Iterable[Segment]] = None
                         ) -> List[Vertices]:
    result = _delaunay(points)
    initial_boundary_segments = frozenset(map(_edge_to_segment,
                                              result.to_boundary_edges()))
    if not extra_constraints and all(edge in initial_boundary_segments
                                     for edge in boundary):
        return result.to_triangles_vertices()
    _set_constraints(result,
                     constraints=(boundary if extra_constraints is None
                                  else chain(boundary, extra_constraints)))
    _set_boundary(result,
                  boundary_segments=boundary)
    return result.to_triangles_vertices()


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
        _set_delaunay_criterion(triangulation,
                                target_edges=new_edges - {constraint})


def _set_delaunay_criterion(triangulation: Triangulation,
                            *,
                            target_edges: Optional[Set[QuadEdge]] = None
                            ) -> None:
    """
    Straightforward flip algorithm.

    Time complexity:
        O(n^2), where
        n -- points count.
    """
    if target_edges is None:
        target_edges = set(triangulation.to_inner_edges())
    while True:
        swapped_edges = set()
        for edge in target_edges:
            if not _points_form_convex_quadrilateral(
                    (edge.start, edge.end,
                     edge.left_from_start.end,
                     edge.right_from_start.end)):
                continue
            if not (is_point_inside_circumcircle(
                    (edge.start, edge.end, edge.left_from_start.end),
                    edge.right_from_start.end)
                    or is_point_inside_circumcircle(
                            (edge.end, edge.start,
                             edge.right_from_start.end),
                            edge.left_from_start.end)):
                continue
            edge.swap()
            swapped_edges.add(edge)
        if not swapped_edges:
            break
        target_edges.difference_update(swapped_edges)


def _set_boundary(triangulation: Triangulation,
                  *,
                  boundary_segments: Sequence[Segment]) -> None:
    boundary_segments = frozenset(boundary_segments)
    non_boundary = {edge
                    for edge in triangulation.to_boundary_edges()
                    if _edge_to_segment(edge) not in boundary_segments}
    while non_boundary:
        edge = non_boundary.pop()
        candidates = triangulation.to_neighbours(edge)
        triangulation.delete(edge)
        non_boundary.update(candidate
                            for candidate in candidates
                            if _edge_to_segment(candidate)
                            not in boundary_segments)


def _resolve_crossings(constraint: Segment,
                       triangulation: Triangulation,
                       *,
                       crossed_edges: Set[QuadEdge]) -> Set[QuadEdge]:
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
        edge.swap()
        if (_edge_to_segment(edge).relationship_with(open_constraint)
                is IntersectionKind.CROSS):
            crossed_edges.append(edge)
        else:
            result.add(edge)
    return result


def _find_crossed_edges(constraint: Segment,
                        triangulation: Triangulation) -> Set[QuadEdge]:
    open_constraint = to_interval(constraint.start, constraint.end,
                                  start_inclusive=False,
                                  end_inclusive=False)
    return {edge
            for edge in triangulation.to_inner_edges()
            if _edge_to_segment(edge).relationship_with(open_constraint)
            is IntersectionKind.CROSS}


def _points_form_convex_quadrilateral(points: Sequence[Point]) -> bool:
    vertices = to_convex_hull(points)
    return (len(vertices) == 4
            and all(vertex in points for vertex in vertices))


def _edge_to_segment(edge: QuadEdge) -> Segment:
    return to_segment(edge.start, edge.end)
