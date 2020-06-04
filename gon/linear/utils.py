import math
from fractions import Fraction
from typing import Sequence

from gon.compound import (Compound,
                          Relation)
from gon.discrete import Multipoint
from gon.hints import (Coordinate,
                       Domain)
from gon.primitive import (Point,
                           RawPoint)


def squared_points_distance(left: Point, right: Point) -> Coordinate:
    return squared_raw_points_distance(left.raw(), right.raw())


def squared_raw_points_distance(left: RawPoint, right: RawPoint) -> Coordinate:
    (left_x, left_y), (right_x, right_y) = left, right
    return (left_x - right_x) ** 2 + (left_y - right_y) ** 2


def relate_multipoint_to_linear_compound(multipoint: Multipoint,
                                         compound: Compound) -> Relation:
    disjoint = is_subset = True
    for point in multipoint.points:
        if point in compound:
            if disjoint:
                disjoint = False
        elif is_subset:
            is_subset = False
    return (Relation.DISJOINT
            if disjoint
            else (Relation.COMPONENT
                  if is_subset
                  else Relation.TOUCH))


def shift_sequence(sequence: Sequence[Domain], step: int) -> Sequence[Domain]:
    return (sequence[step:] + sequence[:step]
            if step
            else sequence)


def robust_sqrt(value: Coordinate) -> Coordinate:
    value = Fraction(value)
    return (Fraction(math.sqrt(value.numerator))
            / Fraction(math.sqrt(value.denominator)))
