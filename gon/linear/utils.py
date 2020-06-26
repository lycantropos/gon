from decimal import Decimal
from fractions import Fraction
from typing import (List,
                    Sequence,
                    Tuple)

from gon.compound import (Compound,
                          Relation)
from gon.degenerate import EMPTY
from gon.discrete import (Multipoint,
                          RawMultipoint)
from gon.hints import (Coordinate,
                       Domain)
from gon.primitive import (Point,
                           RawPoint)
from .hints import RawMultisegment


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
    return Fraction.from_decimal(to_decimal(value).sqrt())


def to_decimal(value: Coordinate) -> Decimal:
    return (Decimal(value.numerator) / value.denominator
            if isinstance(value, Fraction)
            else Decimal(value))


def to_pairs_chain(sequence: Sequence[Domain]) -> List[Tuple[Domain, Domain]]:
    return [(sequence[index - 1], sequence[index])
            for index in range(len(sequence))]


def from_raw_mix_components(raw_multipoint: RawMultipoint,
                            raw_multisegment: RawMultisegment) -> Compound:
    # importing here to avoid cyclic imports
    from gon.mixed.mix import from_mix_components
    return from_mix_components(from_raw_multipoint(raw_multipoint),
                               from_raw_multisegment(raw_multisegment),
                               EMPTY)


def from_raw_multipoint(raw_multipoint: RawMultipoint) -> Multipoint:
    return (Multipoint.from_raw(raw_multipoint)
            if raw_multipoint
            else EMPTY)


def from_raw_multisegment(raw: RawMultisegment) -> Compound:
    # importing here to avoid cyclic imports
    from .segment import Segment
    from .multisegment import Multisegment
    return ((Segment.from_raw(raw[0])
             if len(raw) == 1
             else Multisegment.from_raw(raw))
            if raw
            else EMPTY)
