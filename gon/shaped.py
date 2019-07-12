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

from lz.hints import Sortable
from lz.iterating import (first,
                          pairwise)
from lz.sorting import Key
from memoir import cached
from reprit import seekers
from reprit.base import generate_repr

from .base import (Orientation,
                   Point,
                   Vector,
                   to_orientation)
from .utils import (to_index_min,
                    triplewise)

Angle = Tuple[Point, Point, Point]


def normalize_vertices(vertices: Sequence[Point]) -> Sequence[Point]:
    result = sort_vertices(vertices,
                           # lowest-leftmost point
                           # is required by Graham scan
                           key=attrgetter('y', 'x'))
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

    @cached.property_
    def convex_hull(self) -> Polygon:
        if len(self._vertices) == 3:
            return self
        anchor_point, *rest_points = self._vertices
        return Polygon(_to_convex_hull(anchor_point, rest_points))

    @cached.property_
    def is_convex(self) -> bool:
        if len(self._vertices) == 3:
            return True
        orientations = iter(to_orientations(self._vertices))
        base_orientation = next(orientations)
        return all(orientation == base_orientation
                   for orientation in orientations)


def _validate_polygon_vertices(vertices: Sequence[Point]) -> None:
    if len(vertices) < 3:
        raise ValueError('Polygon should have at least 3 vertices.')
    if not vertices_forms_angles(vertices):
        raise ValueError('Consecutive vertices triplets '
                         'should not be on the same line.')


def _to_convex_hull(anchor_point: Point,
                    rest_points: Sequence[Point]) -> Sequence[Point]:
    def sorting_key(vertex: Point,
                    *,
                    anchor_point: Point = anchor_point) -> Sortable:
        vector = Vector.from_points(anchor_point, vertex)
        return vector.pseudoangle, vector.squared_magnitude

    next_point, *rest_points = sorted(rest_points,
                                      key=sorting_key)
    result = [anchor_point, next_point]
    for point in rest_points:
        while (to_orientation(result[-2], result[-1], point)
               != Orientation.COUNTERCLOCKWISE):
            del result[-1]
            if len(result) < 2:
                break
        result.append(point)
    return result


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
