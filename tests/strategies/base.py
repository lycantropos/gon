import sys
from decimal import Decimal
from fractions import Fraction
from typing import (Optional,
                    SupportsFloat)

from hypothesis import strategies

from gon.base import Point
from gon.hints import Coordinate
from tests.utils import Strategy


def to_floats(*,
              min_value: Optional[Coordinate] = None,
              max_value: Optional[Coordinate] = None,
              allow_nan: bool = False,
              allow_infinity: bool = False) -> Strategy:
    return (strategies.floats(min_value=min_value,
                              max_value=max_value,
                              allow_nan=allow_nan,
                              allow_infinity=allow_infinity)
            .map(to_digits_count))


def to_fractions(*,
                 min_value: Optional[Coordinate] = None,
                 max_value: Optional[Coordinate] = None,
                 max_denominator: Optional[Coordinate] = None) -> Strategy:
    return (strategies.fractions(min_value=min_value,
                                 max_value=max_value,
                                 max_denominator=max_denominator)
            .map(to_digits_count))


def to_integers(*,
                min_value: Optional[Coordinate] = None,
                max_value: Optional[Coordinate] = None) -> Strategy:
    return (strategies.integers(min_value=min_value,
                                max_value=max_value)
            .map(to_digits_count))


def to_digits_count(number: Coordinate,
                    *,
                    max_digits_count: int = sys.float_info.dig) -> Coordinate:
    decimal = to_decimal(number).normalize()
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
    decimal = round(decimal, max(max_digits_count - whole_digits_count, 0))
    return type(number)(str(decimal))


def to_decimal(number: SupportsFloat) -> Decimal:
    if isinstance(number, Decimal):
        return number
    elif not isinstance(number, (int, float)):
        number = float(number)
    return Decimal(number)


scalars_strategies_factories = {float: to_floats,
                                Fraction: to_fractions,
                                int: to_integers}
scalars_strategies = strategies.sampled_from(
        [factory() for factory in scalars_strategies_factories.values()])


def scalars_to_points(scalars: Strategy[Coordinate]) -> Strategy[Point]:
    return strategies.builds(Point, scalars, scalars)


points_strategies = scalars_strategies.map(scalars_to_points)
points = scalars_strategies.flatmap(scalars_to_points)
