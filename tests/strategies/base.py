import sys
from decimal import (Decimal,
                     getcontext)
from fractions import Fraction
from functools import partial
from typing import Optional

from hypothesis import strategies

from gon.base import Point
from gon.hints import Scalar
from tests.utils import Strategy


def to_floats(*,
              min_value: Optional[Scalar] = None,
              max_value: Optional[Scalar] = None,
              allow_nan: bool = False,
              allow_infinity: bool = False) -> Strategy:
    def has_recoverable_significant_digits_count(number: float) -> bool:
        sign, digits, exponent = Decimal(number).as_tuple()
        return len(digits) <= sys.float_info.dig

    return (strategies.floats(min_value=min_value,
                              max_value=max_value,
                              allow_nan=allow_nan,
                              allow_infinity=allow_infinity)
            .filter(has_recoverable_significant_digits_count))


scalars_strategies_factories = {
    Decimal: partial(strategies.decimals,
                     allow_nan=False,
                     allow_infinity=False,
                     places=max(getcontext().prec // 3, 1)),
    float: to_floats,
    Fraction: strategies.fractions,
    int: strategies.integers,
}
scalars_strategies = strategies.sampled_from(
        [factory() for factory in scalars_strategies_factories.values()])


def scalars_to_points(scalars: Strategy[Scalar]) -> Strategy[Point]:
    return strategies.builds(Point, scalars, scalars)


points_strategies = scalars_strategies.map(scalars_to_points)
points = scalars_strategies.flatmap(scalars_to_points)
