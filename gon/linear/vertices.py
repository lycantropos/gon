from fractions import Fraction
from functools import reduce
from itertools import chain
from typing import (Iterable,
                    Iterator)

from robust.hints import Expansion
from robust.utils import (sum_expansions,
                          two_product,
                          two_two_diff)

from gon.angular import (Orientation,
                         to_orientation as to_angle_orientation)
from gon.compound import Compound
from gon.discrete import Multipoint
from gon.hints import Coordinate
from gon.primitive import Point
from gon.primitive.point import scale_point
from .hints import Vertices
from .segment import Segment

MIN_COUNT = 3


def rotate_positions(vertices: Vertices) -> Vertices:
    return vertices[:1] + vertices[:0:-1]


def length(vertices: Vertices) -> Coordinate:
    return sum(vertices[index].distance_to(vertices[index - 1])
               for index in range(len(vertices)))


def form_convex_polygon(vertices: Vertices) -> bool:
    if len(vertices) == 3:
        return True
    orientations = to_orientations(vertices)
    base_orientation = next(orientations)
    # orientation change means that internal angle is greater than 180 degrees
    return all(orientation is base_orientation for orientation in orientations)


def region_signed_area(vertices: Vertices) -> Coordinate:
    double_area = reduce(sum_expansions,
                         (_to_endpoints_cross_product_z(vertices[index - 1],
                                                        vertices[index])
                          for index in range(len(vertices))))[-1]
    return (Fraction(double_area, 2)
            if isinstance(double_area, int)
            else double_area / 2)


def _to_endpoints_cross_product_z(start: Point, end: Point) -> Expansion:
    minuend, minuend_tail = two_product(start.x, end.y)
    subtrahend, subtrahend_tail = two_product(start.y, end.x)
    return (two_two_diff(minuend, minuend_tail, subtrahend, subtrahend_tail)
            if minuend_tail or subtrahend_tail
            else (minuend - subtrahend,))


def to_orientations(vertices: Vertices) -> Iterator[Orientation]:
    vertices_count = len(vertices)
    return (to_angle_orientation(vertices[index - 1], vertices[index],
                                 vertices[(index + 1) % vertices_count])
            for index in range(vertices_count))


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
                    zip(range(size - index
                              if same_oriented
                              else index + 1,
                              size),
                        range(index)
                        if same_oriented
                        else range(size - 1, index - 1, right_step)))
    return all(left[left_index] == right[right_index]
               for left_index, right_index in indices)


def scale(vertices: Vertices,
          factor_x: Coordinate,
          factor_y: Coordinate) -> Vertices:
    return [scale_point(vertex, factor_x, factor_y) for vertex in vertices]


def scale_degenerate(vertices: Iterable[Point],
                     factor_x: Coordinate,
                     factor_y: Coordinate) -> Compound:
    return (scale_projecting_on_ox(vertices, factor_x, factor_y)
            if factor_x
            else (scale_projecting_on_oy(vertices, factor_x, factor_y)
                  if factor_y
                  else Multipoint(Point(factor_x, factor_y))))


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
