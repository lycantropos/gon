import sys
from decimal import Decimal
from functools import partial
from typing import (Optional,
                    Tuple)

from cfractions import Fraction
from hypothesis import strategies

from gon.base import Angle
from gon.hints import Scalar
from tests.utils import (MAX_COORDINATE,
                         MIN_COORDINATE,
                         Strategy)
from .factories import coordinates_to_angles


def to_floats(min_value: Optional[Scalar] = None,
              max_value: Optional[Scalar] = None) -> Strategy:
    return (strategies.floats(min_value=min_value,
                              max_value=max_value,
                              allow_nan=False,
                              allow_infinity=False)
            .map(to_digits_count))


def to_digits_count(number: float,
                    *,
                    max_digits_count: int = sys.float_info.dig) -> float:
    decimal = Decimal(number).normalize()
    _, significant_digits, exponent = decimal.as_tuple()
    significant_digits_count = len(significant_digits)
    if exponent < 0:
        fixed_digits_count = (1 - exponent
                              if exponent <= -significant_digits_count
                              else significant_digits_count)
    else:
        fixed_digits_count = exponent + significant_digits_count
    if fixed_digits_count <= max_digits_count:
        return number
    whole_digits_count = max(significant_digits_count + exponent, 0)
    if whole_digits_count:
        whole_digits_offset = max(whole_digits_count - max_digits_count, 0)
        decimal /= 10 ** whole_digits_offset
        whole_digits_count -= whole_digits_offset
    else:
        decimal *= 10 ** (-exponent - significant_digits_count)
        whole_digits_count = 1
    decimal = round(decimal, min(max(max_digits_count - whole_digits_count, 0),
                                 significant_digits_count))
    return float(str(decimal))


coordinates_strategies = strategies.sampled_from(
        [factory(MIN_COORDINATE, MAX_COORDINATE)
         for factory in [to_floats,
                         partial(strategies.fractions,
                                 max_denominator=MAX_COORDINATE),
                         strategies.integers]]
)


def to_pythagorean_triplets(*,
                            min_value: int = 1,
                            max_value: Optional[int] = None
                            ) -> Strategy[Tuple[int, int, int]]:
    if min_value < 1:
        raise ValueError('`min_value` should be positive.')

    def to_increasing_integers_pairs(value: int) -> Strategy[Tuple[int, int]]:
        return strategies.tuples(strategies.just(value),
                                 strategies.integers(min_value=value + 1,
                                                     max_value=max_value))

    def to_pythagorean_triplet(increasing_integers_pair: Tuple[int, int]
                               ) -> Tuple[int, int, int]:
        first, second = increasing_integers_pair
        first_squared = first ** 2
        second_squared = second ** 2
        return (second_squared - first_squared,
                2 * first * second,
                first_squared + second_squared)

    return (strategies.integers(min_value=min_value,
                                max_value=(max_value - 1
                                           if max_value is not None
                                           else max_value))
            .flatmap(to_increasing_integers_pairs)
            .map(to_pythagorean_triplet))


def pythagorean_triplet_to_rational_cosine_sine(triplet
                                                : Tuple[Scalar, Scalar, Scalar]
                                                ) -> Angle:
    area_cosine, area_sine, area = triplet
    return Angle(Fraction(area_cosine, area), Fraction(area_sine, area))


angles = ((to_pythagorean_triplets(max_value=MAX_COORDINATE)
           .map(pythagorean_triplet_to_rational_cosine_sine))
          | coordinates_strategies.flatmap(coordinates_to_angles))
empty_sequences = strategies.builds(list) | strategies.builds(tuple)
