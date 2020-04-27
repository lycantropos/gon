import math
from fractions import Fraction
from functools import reduce
from typing import Iterator

from robust.hints import Expansion
from robust.utils import (sum_expansions,
                          two_product,
                          two_two_diff)

from gon.angular import (Orientation,
                         to_orientation as to_angle_orientation)
from gon.hints import Coordinate
from gon.primitive import Point
from .hints import Vertices
from .utils import squared_points_distance

MIN_COUNT = 3


def shift(vertices: Vertices, step: int) -> Vertices:
    return (vertices[step:] + vertices[:step]
            if step
            else vertices)


def rotate(vertices: Vertices) -> Vertices:
    return vertices[:1] + vertices[:0:-1]


def length(vertices: Vertices) -> Coordinate:
    return sum(math.sqrt(squared_points_distance(vertices[index - 1],
                                                 vertices[index]))
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


def equal(left: Vertices, right: Vertices) -> bool:
    if len(left) != len(right):
        return False
    right_step = (1
                  if to_orientation(left) is to_orientation(right)
                  else -1)
    size = len(left)
    try:
        index = right.index(left[0])
    except ValueError:
        return False
    else:
        left_index = 0
        for left_index, right_index in zip(range(size),
                                           range(index, size)
                                           if right_step == 1
                                           else range(index, -1,
                                                      right_step)):
            if left[left_index] != right[right_index]:
                return False
        else:
            for left_index, right_index in zip(range(left_index + 1, size),
                                               range(index)
                                               if right_step == 1
                                               else range(size - 1, index - 1,
                                                          right_step)):
                if left[left_index] != right[right_index]:
                    return False
            else:
                return True


def to_orientation(vertices: Vertices) -> Orientation:
    index = min(range(len(vertices)),
                key=vertices.__getitem__)
    return to_angle_orientation(vertices[index], vertices[index - 1],
                                vertices[(index + 1) % len(vertices)])
