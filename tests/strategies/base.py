import sys
from decimal import Decimal
from fractions import Fraction
from typing import (Optional,
                    SupportsFloat)

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
            .map(to_recoverable_significant_digits_count))


def to_floats(*,
              min_value: Optional[Scalar] = None,
              max_value: Optional[Scalar] = None,
              allow_nan: bool = False,
              allow_infinity: bool = False) -> Strategy:
    return (strategies.floats(min_value=min_value,
                              max_value=max_value,
                              allow_nan=allow_nan,
                              allow_infinity=allow_infinity)
            .map(to_recoverable_significant_digits_count))


def to_fractions(*,
                 min_value: Optional[Scalar] = None,
                 max_value: Optional[Scalar] = None,
                 max_denominator: Optional[Scalar] = None) -> Strategy:
    return (strategies.fractions(min_value=min_value,
                                 max_value=max_value,
                                 max_denominator=max_denominator)
            .map(to_recoverable_significant_digits_count))


def to_integers(*,
                min_value: Optional[Scalar] = None,
                max_value: Optional[Scalar] = None) -> Strategy:
    return (strategies.integers(min_value=min_value,
                                max_value=max_value)
            .map(to_recoverable_significant_digits_count))


def to_recoverable_significant_digits_count(
        number: SupportsFloat,
        *,
        max_digits_count: int = sys.float_info.dig) -> SupportsFloat:
    decimal = to_decimal(number)
    sign, digits, exponent = decimal.as_tuple()
    if len(digits) <= max_digits_count:
        return number
    whole_digits_count = len(digits) + exponent
    whole_digits_offset = max(whole_digits_count - max_digits_count, 0)
    decimal /= 10 ** whole_digits_offset
    decimal_digits_count = -exponent + whole_digits_offset
    decimal_digits_limit = max(min(max_digits_count, decimal_digits_count)
                               - whole_digits_offset,
                               0)
    decimal = round(decimal, decimal_digits_limit)
    return type(number)(str(decimal))


def to_decimal(number: SupportsFloat) -> Decimal:
    if not isinstance(number, (int, float)):
        number = float(number)
    return Decimal(number)


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
