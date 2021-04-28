from collections import OrderedDict
from contextlib import contextmanager
from fractions import Fraction
from functools import partial
from itertools import (chain,
                       repeat)
from numbers import Real
from operator import getitem
from typing import (Any,
                    Callable,
                    Iterable,
                    List,
                    Optional,
                    Sequence,
                    Tuple,
                    Type,
                    TypeVar)

import pytest
from ground.base import get_context
from hypothesis import strategies
from hypothesis.strategies import SearchStrategy
from symba.base import Expression

from gon.base import (EMPTY,
                      Compound,
                      Contour,
                      Mix,
                      Multipoint,
                      Multipolygon,
                      Multisegment,
                      Point,
                      Polygon,
                      Relation,
                      Segment)
from gon.core.iterable import shift_sequence
from gon.hints import Coordinate

Domain = TypeVar('Domain')
Range = TypeVar('Range')
Strategy = SearchStrategy

MAX_COORDINATE_EXPONENT = 15
MAX_COORDINATE = 10 ** MAX_COORDINATE_EXPONENT
MIN_COORDINATE = -MAX_COORDINATE
context = get_context()


@contextmanager
def not_raises(*exceptions: Type[BaseException],
               format_error: Callable[[BaseException], str]
               = 'DID RAISE {}'.format) -> None:
    try:
        yield
    except exceptions as error:
        raise pytest.fail(format_error(error))


def equivalence(left_statement: bool, right_statement: bool) -> bool:
    return left_statement is right_statement


def implication(antecedent: bool, consequent: bool) -> bool:
    return not antecedent or consequent


flatten = chain.from_iterable
to_unique_ever_seen = OrderedDict.fromkeys


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


def sub_lists(sequence: Sequence[Domain],
              *,
              min_size: int = 0,
              max_size: Optional[int] = None) -> SearchStrategy[List[Domain]]:
    if max_size is None:
        max_size = len(sequence)
    return strategies.builds(getitem,
                             strategies.permutations(sequence),
                             strategies.builds(slice,
                                               strategies.integers(min_size,
                                                                   max_size)))


def pack(function: Callable[..., Range]
         ) -> Callable[[Iterable[Domain]], Range]:
    return partial(apply, function)


def apply(function: Callable[..., Range], args: Tuple[Domain, ...]) -> Range:
    return function(*args)


def call(function: Callable[..., Range],
         *args: Domain,
         **kwargs: Domain) -> Range:
    return function(*args, **kwargs)


def lift(value: Domain) -> List[Domain]:
    return [value]


def are_compounds_equivalent(left: Compound, right: Compound) -> bool:
    return left == right or left.relate(right) is Relation.EQUAL


def is_scalar(value: Any) -> bool:
    return isinstance(value, (Real, Expression))


def robust_invert(value: Coordinate) -> Coordinate:
    return 1 / Fraction(value)


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
    return Multipoint(multipoint.points[::-1])


def reverse_multisegment(multisegment: Multisegment) -> Multisegment:
    return Multisegment(multisegment.segments[::-1])


def reverse_multisegment_segments(multisegment: Multisegment) -> Multisegment:
    return Multisegment([reverse_segment(segment)
                         for segment in multisegment.segments])


def shift_contour(contour: Contour, step: int) -> Contour:
    return Contour(shift_sequence(contour.vertices, step))


def shift_multipoint(multipoint: Multipoint, step: int) -> Multipoint:
    return Multipoint(shift_sequence(multipoint.points, step))


def shift_multisegment(multisegment: Multisegment, step: int) -> Multisegment:
    return Multisegment(shift_sequence(multisegment.segments, step))


def divide_by_int(dividend: Coordinate, divisor: int) -> Coordinate:
    return (Fraction(dividend, divisor)
            if isinstance(dividend, int)
            else dividend / divisor)


def compound_to_compound_with_multipoint(compound: Compound
                                         ) -> Tuple[Compound, Multipoint]:
    return (compound, Multipoint(list(to_unique_ever_seen(compound_to_points(
            compound)))))


def compound_to_points(compound: Compound) -> Iterable[Point]:
    if isinstance(compound, Multipoint):
        return compound.points
    elif isinstance(compound, Segment):
        return [compound.start, compound.end]
    elif isinstance(compound, Multisegment):
        return flatten((segment.start, segment.end)
                       for segment in compound.segments)
    elif isinstance(compound, Contour):
        return compound.vertices
    elif isinstance(compound, Polygon):
        return chain(compound.border.vertices,
                     flatten(hole.vertices for hole in compound.holes))
    elif isinstance(compound, Multipolygon):
        return flatten(compound_to_points(polygon)
                       for polygon in compound.polygons)
    elif isinstance(compound, Mix):
        return chain([]
                     if compound.discrete is EMPTY
                     else compound_to_points(compound.discrete),
                     []
                     if compound.linear is EMPTY
                     else compound_to_points(compound.linear),
                     []
                     if compound.shaped is EMPTY
                     else compound_to_points(compound.shaped))
    else:
        raise TypeError('Unsupported geometry type: {type}.'
                        .format(type=type(compound)))


def mix_to_components(mix: Mix
                      ) -> Tuple[Multipoint, Multisegment, Multipolygon]:
    return mix.discrete, mix.linear, mix.shaped


def mix_to_points(mix: Mix) -> Sequence[Point]:
    discrete = mix.discrete
    return [] if discrete is EMPTY else discrete.points


def mix_to_polygons(mix: Mix) -> Sequence[Polygon]:
    shaped = mix.shaped
    return ([]
            if shaped is EMPTY
            else (shaped.polygons
                  if isinstance(shaped, Multipolygon)
                  else [shaped]))


def mix_to_segments(mix: Mix) -> Sequence[Segment]:
    linear = mix.linear
    return ([]
            if linear is EMPTY
            else (linear.segments
                  if isinstance(linear, Multisegment)
                  else (linear.edges
                        if isinstance(linear, Contour)
                        else [linear])))


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


to_points_convex_hull = context.points_convex_hull
