import sys
from decimal import Decimal
from fractions import Fraction
from typing import (Optional,
                    Union)

from hypothesis import strategies

from gon.base import Point
from gon.hints import Scalar
from tests.utils import Strategy


def to_decimals(*,
                min_value: Optional[Scalar] = None,
                max_value: Optional[Scalar] = None,
                allow_nan: bool = False,
                allow_infinity: bool = False) -> Strategy:
    return (strategies.floats(min_value=min_value,
                              max_value=max_value,
                              allow_nan=allow_nan,
                              allow_infinity=allow_infinity)
            .filter(has_recoverable_significant_digits_count))


def to_floats(*,
              min_value: Optional[Scalar] = None,
              max_value: Optional[Scalar] = None,
              allow_nan: bool = False,
              allow_infinity: bool = False) -> Strategy:
    return (strategies.floats(min_value=min_value,
                              max_value=max_value,
                              allow_nan=allow_nan,
                              allow_infinity=allow_infinity)
            .filter(has_recoverable_significant_digits_count))


def to_fractions(*,
                 min_value: Optional[Scalar] = None,
                 max_value: Optional[Scalar] = None,
                 max_denominator: Optional[Scalar] = None) -> Strategy:
    def fraction_has_recoverable_significant_digits_count(fraction: Fraction
                                                          ) -> bool:
        return (has_recoverable_significant_digits_count(fraction.numerator)
                and has_recoverable_significant_digits_count(fraction
                                                             .denominator))

    return (strategies.fractions(min_value=min_value,
                                 max_value=max_value,
                                 max_denominator=max_denominator)
            .filter(fraction_has_recoverable_significant_digits_count))


def to_integers(*,
                min_value: Optional[Scalar] = None,
                max_value: Optional[Scalar] = None) -> Strategy:
    return (strategies.integers(min_value=min_value,
                                max_value=max_value)
            .filter(has_recoverable_significant_digits_count))


def has_recoverable_significant_digits_count(number: Union[Decimal, float]
                                             ) -> bool:
    sign, digits, exponent = Decimal(number).as_tuple()
    return len(digits) <= sys.float_info.dig


scalars_strategies_factories = {Decimal: to_decimals,
                                float: to_floats,
                                Fraction: to_fractions,
                                int: to_integers}
scalars_strategies = strategies.sampled_from(
        [factory() for factory in scalars_strategies_factories.values()])


def scalars_to_points(scalars: Strategy[Scalar]) -> Strategy[Point]:
    return strategies.builds(Point, scalars, scalars)


points_strategies = scalars_strategies.map(scalars_to_points)
points = scalars_strategies.flatmap(scalars_to_points)
