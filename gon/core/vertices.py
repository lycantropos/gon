from itertools import chain
from typing import (Iterable,
                    Sequence)

from .compound import Compound
from .hints import Coordinate
from .multipoint import Multipoint
from .point import Point
from .segment import Segment

Vertices = Sequence[Point]

MIN_COUNT = 3


def rotate_positions(vertices: Vertices) -> Vertices:
    return vertices[:1] + vertices[:0:-1]


def length(vertices: Vertices) -> Coordinate:
    return sum(vertices[index].distance_to(vertices[index - 1])
               for index in range(len(vertices)))


def equal(left: Vertices, right: Vertices, same_oriented: bool) -> bool:
    if len(left) != len(right):
        return False
    try:
        index = right.index(left[0])
    except ValueError:
        return False
    right_step = 1 if same_oriented else -1
    size = len(left)
    indices = chain(zip(range(size),
                        range(index, size)
                        if same_oriented
                        else range(index, -1, right_step)),
                    zip(range(size - index if same_oriented else index + 1,
                              size),
                        range(index)
                        if same_oriented
                        else range(size - 1, index - 1, right_step)))
    return all(left[left_index] == right[right_index]
               for left_index, right_index in indices)


def scale_degenerate(vertices: Iterable[Point],
                     factor_x: Coordinate,
                     factor_y: Coordinate) -> Compound:
    return (scale_projecting_on_ox(vertices, factor_x, factor_y)
            if factor_x
            else (scale_projecting_on_oy(vertices, factor_x, factor_y)
                  if factor_y
                  else Multipoint([Point(factor_x, factor_y)])))


def scale_projecting_on_ox(vertices: Iterable[Point],
                           factor_x: Coordinate,
                           factor_y: Coordinate) -> Segment:
    vertices = iter(vertices)
    min_x = max_x = next(vertices).x
    for vertex in vertices:
        if min_x > vertex.x:
            min_x = vertex.x
        elif max_x < vertex.x:
            max_x = vertex.x
    return Segment(Point(min_x * factor_x, factor_y),
                   Point(max_x * factor_x, factor_y))


def scale_projecting_on_oy(vertices: Iterable[Point],
                           factor_x: Coordinate,
                           factor_y: Coordinate) -> Segment:
    vertices = iter(vertices)
    min_y = max_y = next(vertices).y
    for vertex in vertices:
        if min_y > vertex.y:
            min_y = vertex.y
        elif max_y < vertex.y:
            max_y = vertex.y
    return Segment(Point(factor_x, min_y * factor_y),
                   Point(factor_x, max_y * factor_y))
