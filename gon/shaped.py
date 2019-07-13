from abc import (ABC,
                 abstractmethod)
from itertools import (chain,
                       cycle,
                       islice,
                       starmap)
from operator import attrgetter
from typing import (Iterable,
                    Sequence,
                    Tuple)

from lz.iterating import (first,
                          pairwise)
from lz.sorting import Key
from reprit import seekers
from reprit.base import generate_repr

from .base import (Orientation,
                   Point,
                   Vector,
                   to_orientation)
from .hints import Scalar
from .utils import (to_index_min,
                    triplewise)

Angle = Tuple[Point, Point, Point]


def normalize_vertices(vertices: Sequence[Point]) -> Sequence[Point]:
    result = sort_vertices(vertices,
                           key=attrgetter('x', 'y'))
    if first(to_orientations(result)) != Orientation.COUNTERCLOCKWISE:
        result = result[:1] + result[1:][::-1]
    return result


def sort_vertices(vertices: Sequence[Point],
                  *,
                  key: Key = None) -> Sequence[Point]:
    index_min = to_index_min(vertices,
                             key=key)
    return vertices[index_min:] + vertices[:index_min]


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

    @property
    @abstractmethod
    def convex_hull(self) -> 'Polygon':
        pass

    @property
    @abstractmethod
    def is_convex(self) -> bool:
        pass


class SimplePolygon(Polygon):
    __slots__ = ('_vertices',)

    def __new__(cls, vertices: Sequence[Point]) -> Polygon:
        if cls is not __class__:
            return super().__new__(cls, vertices)
        if self_intersects(vertices):
            raise ValueError('Simple polygon should not be self-intersecting.')
        return super().__new__(cls, vertices)

    def __init__(self, vertices: Sequence[Point]) -> None:
        self._vertices = tuple(normalize_vertices(vertices))

    __repr__ = generate_repr(__init__,
                             field_seeker=seekers.complex_)

    def __hash__(self) -> int:
        return hash(self._vertices)

    def __eq__(self, other: Polygon) -> bool:
        if not isinstance(other, Polygon):
            return NotImplemented
        if not isinstance(other, SimplePolygon):
            return False
        return self._vertices == other._vertices

    @property
    def convex_hull(self) -> Polygon:
        if len(self._vertices) == 3:
            return self
        return Polygon(_to_convex_hull(self._vertices))

    @property
    def is_convex(self) -> bool:
        if len(self._vertices) == 3:
            return True
        orientations = iter(to_orientations(self._vertices))
        base_orientation = next(orientations)
        return all(orientation == base_orientation
                   for orientation in orientations)


def _to_convex_hull(points: Sequence[Point]) -> Sequence[Point]:
    next_index = index = 0
    result = [points[0]]

    def to_squared_vector_length(start: Point, end: Point) -> Scalar:
        return Vector.from_points(start, end).squared_length

    while True:
        candidate_index = (next_index + 1) % len(points)
        for index, point in enumerate(points):
            if index == next_index:
                continue
            orientation = to_orientation(points[next_index], point,
                                         points[candidate_index])
            if (orientation == Orientation.COUNTERCLOCKWISE
                    or (orientation == Orientation.COLLINEAR
                        and to_squared_vector_length(point,
                                                     points[next_index])
                        > to_squared_vector_length(points[candidate_index],
                                                   points[next_index]))):
                candidate_index = index
        next_index = candidate_index
        if next_index == index:
            break
        result.append(points[next_index])
    return result


def _validate_polygon_vertices(vertices: Sequence[Point]) -> None:
    if len(vertices) < 3:
        raise ValueError('Polygon should have at least 3 vertices.')
    if not vertices_forms_angles(vertices):
        raise ValueError('Consecutive vertices triplets '
                         'should not be on the same line.')


def vertices_forms_angles(vertices: Sequence[Point]) -> bool:
    return all(orientation != Orientation.COLLINEAR
               for orientation in to_orientations(vertices))


def to_orientations(vertices: Sequence[Point]) -> Iterable[int]:
    return starmap(to_orientation, to_angles(vertices))


def to_angles(vertices: Sequence[Point]) -> Iterable[Angle]:
    return triplewise(islice(cycle(vertices), len(vertices) + 2))


def self_intersects(vertices: Sequence[Point]) -> bool:
    if len(vertices) == 3:
        return False
    edges = tuple(to_edges(vertices))
    for index, edge in enumerate(edges):
        # skipping neighbours because they always intersect
        # NOTE: first & last edges are neighbours
        non_neighbours = chain(edges[max(index + 2 - len(edges), 0):
                                     max(index - 1, 0)],
                               edges[index + 2:index - 1 + len(edges)])
        if any(edge.intersects_with(non_neighbour)
               for non_neighbour in non_neighbours):
            return True
    return False


class Segment:
    __slots__ = ('_start', '_end')

    def __new__(cls, start: Point, end: Point) -> 'Segment':
        if start == end:
            raise ValueError('Degenerate segment found.')
        return super().__new__(cls)

    def __init__(self, start: Point, end: Point) -> None:
        self._start = start
        self._end = end

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'Segment') -> bool:
        return (self._start == other._start
                and self._end == other._end
                or self._start == other._end
                and self._end == other._start)

    def __hash__(self) -> int:
        return hash((self._start, self._end))

    @property
    def start(self) -> Point:
        return self._start

    @property
    def end(self) -> Point:
        return self._end

    def intersects_with(self, other: 'Segment') -> bool:
        def on_segment(point: Point, segment: Segment) -> bool:
            left_x, right_x = sorted([segment.start.x, segment.end.x])
            bottom_y, top_y = sorted([segment.start.y, segment.end.y])
            return (left_x <= point.x <= right_x
                    and bottom_y <= point.y <= top_y)

        self_start_orientation = to_orientation(other.start, other.end,
                                                self.start)
        if (self_start_orientation == Orientation.COLLINEAR
                and on_segment(self.start, other)):
            return True
        self_end_orientation = to_orientation(other.start, other.end,
                                              self.end)
        if (self_end_orientation == Orientation.COLLINEAR
                and on_segment(self.end, other)):
            return True
        other_start_orientation = to_orientation(self.start, self.end,
                                                 other.start)
        if (other_start_orientation == Orientation.COLLINEAR
                and on_segment(other.start, self)):
            return True
        other_end_orientation = to_orientation(self.start, self.end,
                                               other.end)
        return (self_start_orientation * self_end_orientation < 0
                and other_start_orientation * other_end_orientation < 0
                or other_end_orientation == Orientation.COLLINEAR
                and on_segment(other.end, self))


def to_edges(vertices: Sequence[Point]) -> Iterable[Segment]:
    return (Segment(start, end)
            for start, end in pairwise(islice(cycle(vertices),
                                              len(vertices) + 1)))
