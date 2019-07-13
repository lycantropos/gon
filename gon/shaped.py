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


def self_intersects(points: Sequence[Point]) -> bool:
    if len(points) == 3:
        return False
    segments = tuple(to_segments(points))
    for segment_index, segment in enumerate(segments):
        # skipping neighbours because they always intersect
        # NOTE: first & last segments are neighbours
        candidates = chain(segments[max(segment_index + 2 - len(segments), 0):
                                    max(segment_index - 1, 0)],
                           segments[segment_index + 2:
                                    segment_index - 1 + len(segments)])
        if any(segment.intersects_with(candidate)
               for candidate in candidates):
            return True
    return False


class Segment:
    __slots__ = ('_first_end', '_second_end')

    def __new__(cls, first_end: Point, second_end: Point) -> 'Segment':
        if first_end == second_end:
            raise ValueError('Degenerate segment found.')
        return super().__new__(cls)

    def __init__(self, left_end: Point, right_end: Point) -> None:
        self._first_end = left_end
        self._second_end = right_end

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'Segment') -> bool:
        return (self._first_end == other._first_end
                and self._second_end == other._second_end
                or self._first_end == other._second_end
                and self._second_end == other._first_end)

    def __hash__(self) -> int:
        return hash((self._first_end, self._second_end))

    @property
    def first_end(self) -> Point:
        return self._first_end

    @property
    def second_end(self) -> Point:
        return self._second_end

    def intersects_with(self, other: 'Segment') -> bool:
        def on_segment(point: Point, segment: Segment) -> bool:
            left_x, right_x = sorted([segment.first_end.x,
                                      segment.second_end.x])
            bottom_y, top_y = sorted([segment.first_end.y,
                                      segment.second_end.y])
            return (left_x <= point.x <= right_x
                    and bottom_y <= point.y <= top_y)

        self_first_orientation = to_orientation(other.first_end,
                                                other.second_end,
                                                self.first_end)
        if (self_first_orientation == Orientation.COLLINEAR
                and on_segment(self.first_end, other)):
            return True
        self_second_orientation = to_orientation(other.first_end,
                                                 other.second_end,
                                                 self.second_end)
        if (self_second_orientation == Orientation.COLLINEAR
                and on_segment(self.second_end, other)):
            return True
        other_first_orientation = to_orientation(self.first_end,
                                                 self.second_end,
                                                 other.first_end)
        if (other_first_orientation == Orientation.COLLINEAR
                and on_segment(other.first_end, self)):
            return True
        other_second_orientation = to_orientation(self.first_end,
                                                  self.second_end,
                                                  other.second_end)
        return (self_first_orientation * self_second_orientation < 0
                and other_first_orientation * other_second_orientation < 0
                or other_second_orientation == Orientation.COLLINEAR
                and on_segment(other.second_end, self))


def to_segments(points: Sequence[Point]) -> Iterable[Segment]:
    return (Segment(left_end, right_end)
            for left_end, right_end in pairwise(islice(cycle(points),
                                                       len(points) + 1)))
