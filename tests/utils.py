from fractions import Fraction
from functools import partial
from itertools import (chain,
                       repeat)
from operator import getitem
from typing import (Any,
                    Callable,
                    Iterable,
                    List,
                    Sequence,
                    Tuple,
                    TypeVar)

from hypothesis import strategies
from hypothesis.strategies import SearchStrategy

from gon.discrete import Multipoint
from gon.hints import Coordinate
from gon.linear import (Contour,
                        Multisegment,
                        Segment)
from gon.linear.utils import shift_sequence
from gon.mixed import Mix
from gon.primitive import Point
from gon.shaped import Multipolygon

Domain = TypeVar('Domain')
Range = TypeVar('Range')
Strategy = SearchStrategy

MAX_COORDINATE_EXPONENT = 15


def equivalence(left_statement: bool, right_statement: bool) -> bool:
    return left_statement is right_statement


def implication(antecedent: bool, consequent: bool) -> bool:
    return not antecedent or consequent


flatten = chain.from_iterable


def identity(argument: Domain) -> Domain:
    return argument


def to_constant(value: Domain) -> Callable[..., Domain]:
    def constant(*_: Any, **__: Any) -> Domain:
        return value

    return constant


def to_tuples(elements: Strategy[Domain],
              *,
              size: int) -> Strategy[Tuple[Domain, ...]]:
    return strategies.tuples(*repeat(elements,
                                     times=size))


to_pairs = partial(to_tuples,
                   size=2)
to_triplets = partial(to_tuples,
                      size=3)


def cleave_in_tuples(*functions: Callable[[Strategy[Domain]], Strategy[Range]]
                     ) -> Callable[[Strategy[Domain]],
                                   Strategy[Tuple[Range, ...]]]:
    def cleaved(base: Strategy[Domain]) -> Strategy[Tuple[Range, ...]]:
        return strategies.tuples(*[function(base) for function in functions])

    return cleaved


def sub_lists(sequence: Sequence[Domain]) -> SearchStrategy[List[Domain]]:
    return strategies.builds(getitem,
                             strategies.permutations(sequence),
                             strategies.slices(max(len(sequence), 1)))


def pack(function: Callable[..., Range]
         ) -> Callable[[Iterable[Domain]], Range]:
    return partial(apply, function)


def apply(function: Callable[..., Range], args: Tuple[Domain, ...]) -> Range:
    return function(*args)


def scale_segment(segment: Segment,
                  *,
                  scale: Coordinate) -> Segment:
    return Segment(segment.start,
                   Point(segment.start.x
                         + scale * (segment.end.x - segment.start.x),
                         segment.start.y
                         + scale * (segment.end.y - segment.start.y)))


def reflect_segment(segment: Segment) -> Segment:
    return scale_segment(segment,
                         scale=-1)


def reverse_segment(segment: Segment) -> Segment:
    return Segment(segment.end, segment.start)


def reverse_multipoint(multipoint: Multipoint) -> Multipoint:
    return Multipoint(*multipoint.points[::-1])


def reverse_multisegment(multisegment: Multisegment) -> Multisegment:
    return Multisegment(*multisegment.segments[::-1])


def reverse_multisegment_segments(multisegment: Multisegment) -> Multisegment:
    return Multisegment(*map(reverse_segment, multisegment.segments))


def shift_contour(contour: Contour, step: int) -> Contour:
    return Contour(shift_sequence(contour.vertices, step))


def shift_multipoint(multipoint: Multipoint, step: int) -> Multipoint:
    return Multipoint(*shift_sequence(multipoint.points, step))


def shift_multisegment(multisegment: Multisegment,
                       step: int) -> Multisegment:
    return Multisegment(*shift_sequence(multisegment.segments, step))


def divide_by_int(dividend: Coordinate, divisor: int) -> Coordinate:
    return (Fraction(dividend, divisor)
            if isinstance(dividend, int)
            else dividend / divisor)


def mix_to_components(mix: Mix
                      ) -> Tuple[Multipoint, Multisegment, Multipolygon]:
    return mix.multipoint, mix.multisegment, mix.multipolygon


def segment_to_rotations(segment: Segment,
                         pythagorean_triplets: List[Tuple[int, int, int]]
                         ) -> List[Segment]:
    return [segment] + [rotate_segment(segment, pythagorean_triplet)
                        for pythagorean_triplet in pythagorean_triplets]


def rotate_segment(segment: Segment,
                   pythagorean_triplet: Tuple[int, int, int]) -> Segment:
    area_sine, area_cosine, area = pythagorean_triplet
    center_x, center_y = (divide_by_int(segment.start.x + segment.end.x, 2),
                          divide_by_int(segment.start.y + segment.end.y, 2))
    start_dx, start_dy = segment.start.x - center_x, segment.start.y - center_y
    end_dx, end_dy = segment.end.x - center_x, segment.end.y - center_y
    return Segment(Point(center_x + divide_by_int(area_cosine * start_dx
                                                  - area_sine * start_dy,
                                                  area),
                         center_y + divide_by_int(area_sine * start_dx
                                                  + area_cosine * start_dy,
                                                  area)),
                   Point(center_x + divide_by_int(area_cosine * end_dx
                                                  - area_sine * end_dy,
                                                  area),
                         center_y + divide_by_int(area_sine * end_dx
                                                  + area_cosine * end_dy,
                                                  area)))
