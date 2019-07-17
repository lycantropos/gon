from abc import (ABC,
                 abstractmethod)
from enum import IntEnum
from itertools import (cycle,
                       islice,
                       starmap)
from operator import (attrgetter,
                      itemgetter,
                      le,
                      lt)
from types import MappingProxyType
from typing import (Callable,
                    Iterable,
                    Mapping,
                    Sequence,
                    Tuple)

from lz.functional import compose
from lz.hints import Domain
from lz.iterating import pairwise
from lz.sorting import Key
from memoir import cached
from reprit.base import generate_repr

from .base import (Point,
                   Vector)
from .hints import (Permutation,
                    Scalar)
from .utils import (inverse_permutation,
                    is_odd,
                    to_index_min,
                    to_sign,
                    triplewise)


def _normalize_vertices(vertices: Sequence[Point]) -> Tuple[Permutation,
                                                            Sequence[Point]]:
    order, vertices = zip(*_shift_sequence(tuple(enumerate(vertices)),
                                           key=compose(attrgetter('x', 'y'),
                                                       itemgetter(1))))
    first_angle = Angle(vertices[0], vertices[1], vertices[2])
    if first_angle.orientation != Orientation.COUNTERCLOCKWISE:
        order, vertices = (order[:1] + order[1:][::-1],
                           vertices[:1] + vertices[1:][::-1])
    return order, vertices


def _shift_sequence(sequence: Sequence[Domain],
                    *,
                    key: Key = None) -> Sequence[Domain]:
    index_min = to_index_min(sequence,
                             key=key)
    return sequence[index_min:] + sequence[:index_min]


class Polygon(ABC):
    def __new__(cls, vertices: Sequence[Point]) -> 'Polygon':
        if cls is not __class__:
            return super().__new__(cls)
        _validate_polygon_vertices(vertices)
        return SimplePolygon(vertices)

    @abstractmethod
    def __hash__(self) -> int:
        pass

    @abstractmethod
    def __eq__(self, other: 'Polygon') -> bool:
        pass

    @abstractmethod
    def __contains__(self, point: Point) -> bool:
        pass

    @property
    @abstractmethod
    def vertices(self) -> Sequence[Point]:
        pass

    @property
    @abstractmethod
    def area(self) -> Scalar:
        pass

    @property
    @abstractmethod
    def convex_hull(self) -> 'Polygon':
        pass

    @property
    @abstractmethod
    def is_convex(self) -> bool:
        pass


class SimplePolygon(Polygon):
    __slots__ = ('_order', '_vertices')

    def __new__(cls, vertices: Sequence[Point]) -> Polygon:
        if self_intersects(vertices):
            raise ValueError('Simple polygon should not be self-intersecting.')
        return super().__new__(cls, vertices)

    def __init__(self, vertices: Sequence[Point]) -> None:
        self._order, self._vertices = _normalize_vertices(tuple(vertices))

    __repr__ = generate_repr(__init__)

    def __hash__(self) -> int:
        return hash(self._vertices)

    def __eq__(self, other: Polygon) -> bool:
        if not isinstance(other, Polygon):
            return NotImplemented
        if not isinstance(other, SimplePolygon):
            return False
        return self._vertices == other._vertices

    def __contains__(self, point: Point) -> bool:
        leftmost_bottom_vertex = self._vertices[0]
        if (point.x < leftmost_bottom_vertex.x
                or point.x == leftmost_bottom_vertex.x
                and point.y < leftmost_bottom_vertex.y):
            return False
        try:
            segment = Segment(leftmost_bottom_vertex, point)
        except ValueError:
            # degenerate segment, point is a leftmost vertex
            return True
        edges_intersections = 0
        for edge in to_edges(self._vertices):
            intersects_with_edge = segment.intersects_with(edge)
            if intersects_with_edge and point in edge:
                return True
            edges_intersections += intersects_with_edge
        return is_odd(edges_intersections)

    @cached.property_
    def vertices(self) -> Sequence[Point]:
        return itemgetter(*inverse_permutation(self._order))(self._vertices)

    @cached.property_
    def area(self) -> Scalar:
        return abs(sum(edge.start.x * edge.end.y - edge.start.y * edge.end.x
                       for edge in to_edges(self._vertices))) / 2

    @cached.property_
    def convex_hull(self) -> Polygon:
        if len(self._vertices) == 3:
            return self
        return Polygon(to_convex_hull(self._vertices))

    @cached.property_
    def is_convex(self) -> bool:
        if len(self._vertices) == 3:
            return True
        orientations = (angle.orientation
                        for angle in to_angles(self._vertices))
        base_orientation = next(orientations)
        return all(orientation == base_orientation
                   for orientation in orientations)



def to_convex_hull(points: Sequence[Point]) -> Sequence[Point]:
    points = sorted(points,
                    key=attrgetter('x', 'y'))
    lower = _to_sub_hull(points)
    upper = _to_sub_hull(reversed(points))
    return lower[:-1] + upper[:-1]


def _to_sub_hull(points: Iterable[Point]) -> Sequence[Point]:
    result = []
    for point in points:
        while len(result) >= 2:
            if (Angle(result[-2], result[-1], point).orientation
                    != Orientation.COUNTERCLOCKWISE):
                del result[-1]
            else:
                break
        result.append(point)
    return result


def _validate_polygon_vertices(vertices: Sequence[Point]) -> None:
    if len(vertices) < 3:
        raise ValueError('Polygon should have at least 3 vertices.')
    if not vertices_forms_angles(vertices):
        raise ValueError('Consecutive vertices triplets '
                         'should not be on the same line.')


def vertices_forms_angles(vertices: Sequence[Point]) -> bool:
    return all(angle.orientation != Orientation.COLLINEAR
               for angle in to_angles(vertices))


class Angle:
    def __init__(self,
                 vertex: Point,
                 first_ray_point: Point,
                 second_ray_point: Point) -> None:
        self._vertex = vertex
        self._first_ray_point = first_ray_point
        self._second_ray_point = second_ray_point

    @property
    def vertex(self) -> Point:
        return self._vertex

    @property
    def first_ray_point(self) -> Point:
        return self._first_ray_point

    @property
    def second_ray_point(self) -> Point:
        return self._second_ray_point

    __repr__ = generate_repr(__init__)

    @property
    def orientation(self) -> int:
        first_ray_vector = Vector.from_points(self.vertex,
                                              self._first_ray_point)
        second_ray_vector = Vector.from_points(self.vertex,
                                               self._second_ray_point)
        return to_sign(first_ray_vector.cross_z(second_ray_vector))

    @property
    def is_acute(self) -> bool:
        return self.kind == AngleKind.ACUTE

    @property
    def is_right(self) -> bool:
        return self.kind == AngleKind.RIGHT

    @property
    def is_obtuse(self) -> bool:
        return self.kind == AngleKind.OBTUSE

    @property
    def kind(self) -> int:
        return to_sign(
                self.vertex.squared_distance_to(self._first_ray_point)
                - self._first_ray_point.squared_distance_to(
                        self._second_ray_point)
                + self.vertex.squared_distance_to(
                        self._second_ray_point))


class AngleKind(IntEnum):
    OBTUSE = -1
    RIGHT = 0
    ACUTE = 1


class Orientation(IntEnum):
    CLOCKWISE = -1
    COLLINEAR = 0
    COUNTERCLOCKWISE = 1


def to_angles(vertices: Sequence[Point]) -> Iterable[Angle]:
    return starmap(Angle,
                   triplewise(islice(cycle(vertices), len(vertices) + 2)))


class Interval:
    __slots__ = ('_start', '_end', '_start_inclusive', '_end_inclusive')

    def __new__(cls, start: Point, end: Point,
                *,
                start_inclusive: bool,
                end_inclusive: bool) -> 'Interval':
        if cls is not __class__:
            return super().__new__(cls)
        if start == end:
            raise ValueError('Degenerate interval found.')
        return super().__new__(cls)

    def __init__(self,
                 start: Point,
                 end: Point,
                 *,
                 start_inclusive: bool,
                 end_inclusive: bool) -> None:
        self._start = start
        self._end = end
        self._start_inclusive = start_inclusive
        self._end_inclusive = end_inclusive

    @property
    def start(self) -> Point:
        return self._start

    @property
    def end(self) -> Point:
        return self._end

    @property
    def start_inclusive(self) -> bool:
        return self._start_inclusive

    @property
    def end_inclusive(self) -> bool:
        return self._end_inclusive

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'Interval') -> bool:
        return (self._start_inclusive is other._start_inclusive
                and self._end_inclusive is other._end_inclusive
                and self._start == other._start
                and self._end == other._end
                or self._start_inclusive is other._end_inclusive
                and self._end_inclusive is other._start_inclusive
                and self._start == other._end
                and self._end == other._start)

    def __hash__(self) -> int:
        return hash((self._start, self._end,
                     self.start_inclusive, self.end_inclusive))

    def __contains__(self, point: Point) -> bool:
        return (self.orientation_with(point) == Orientation.COLLINEAR
                and _in_interval(point, self))

    def intersects_with(self, other: 'Interval') -> bool:
        self_start_orientation = other.orientation_with(self.start)
        if (self.start_inclusive
                and self_start_orientation == Orientation.COLLINEAR
                and _in_interval(self.start, other)):
            return True
        self_end_orientation = other.orientation_with(self.end)
        if (self.end_inclusive
                and self_end_orientation == Orientation.COLLINEAR
                and _in_interval(self.end, other)):
            return True
        other_start_orientation = self.orientation_with(other.start)
        if (other.start_inclusive
                and other_start_orientation == Orientation.COLLINEAR
                and _in_interval(other.start, self)):
            return True
        other_end_orientation = self.orientation_with(other.end)
        return (self_start_orientation * self_end_orientation < 0
                and other_start_orientation * other_end_orientation < 0
                or other.end_inclusive
                and other_end_orientation == Orientation.COLLINEAR
                and _in_interval(other.end, self))

    def orientation_with(self, point: Point) -> int:
        return Angle(self.start, self.end, point).orientation


class Segment(Interval):
    def __new__(cls, start: Point, end: Point) -> 'Interval':
        return super().__new__(cls, start, end,
                               start_inclusive=True,
                               end_inclusive=True)

    def __init__(self, start: Point, end: Point) -> None:
        super().__init__(start, end,
                         start_inclusive=True,
                         end_inclusive=True)

    __repr__ = generate_repr(__init__)


def self_intersects(vertices: Sequence[Point]) -> bool:
    if len(vertices) == 3:
        return False
    edges = tuple(to_edges(vertices))
    for index, edge in enumerate(edges):
        # skipping neighbours because they always intersect
        # NOTE: first & last edges are neighbours
        if any(edge.intersects_with(non_neighbour)
               for non_neighbour in _to_non_neighbours(index, edges)):
            return True
    return False


def _to_non_neighbours(edge_index: int,
                       edges: Sequence[Segment]) -> Sequence[Segment]:
    return (edges[max(edge_index + 2 - len(edges), 0):max(edge_index - 1, 0)]
            + edges[edge_index + 2:edge_index - 1 + len(edges)])


def _in_interval(point: Point, interval: Interval,
                 *,
                 flags_predicates: Mapping[bool,
                                           Callable[[Scalar, Scalar], bool]]
                 = MappingProxyType({False: lt,
                                     True: le})
                 ) -> bool:
    start_predicate = flags_predicates[interval.start_inclusive]
    end_predicate = flags_predicates[interval.end_inclusive]
    ((left_x, left_x_predicate),
     (right_x, right_x_predicate)) = sorted([(interval.start.x,
                                              start_predicate),
                                             (interval.end.x,
                                              end_predicate)])
    ((bottom_y, bottom_y_predicate),
     (top_y, top_y_predicate)) = sorted([(interval.start.y, start_predicate),
                                         (interval.end.y, end_predicate)])
    return (left_x_predicate(left_x, point.x)
            and right_x_predicate(point.x, right_x)
            and bottom_y_predicate(bottom_y, point.y)
            and top_y_predicate(point.y, top_y))


def to_edges(vertices: Sequence[Point]) -> Iterable[Segment]:
    return (Segment(start, end)
            for start, end in pairwise(islice(cycle(vertices),
                                              len(vertices) + 1)))
