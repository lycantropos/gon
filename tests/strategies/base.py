import sys
from decimal import Decimal
from operator import (methodcaller,
                      ne)

from hypothesis import strategies
from lz.functional import (compose,
                           pack)
from lz.replication import duplicate

from gon.base import Point
from gon.hints import Scalar
from gon.shaped import Segment
from tests.utils import Strategy

decimals = strategies.decimals(allow_nan=False,
                               allow_infinity=False)


def has_recoverable_significant_digits_count(number: float) -> bool:
    sign, digits, exponent = Decimal(number).as_tuple()
    return len(digits) <= sys.float_info.dig


floats = (strategies.floats(allow_nan=False,
                            allow_infinity=False)
          .filter(has_recoverable_significant_digits_count))
fractions = strategies.fractions()
integers = strategies.integers()
scalars_strategies = strategies.sampled_from([decimals, floats,
                                              fractions, integers])


def scalars_to_points(scalars: Strategy[Scalar]) -> Strategy[Point]:
    return strategies.builds(Point, scalars, scalars)


points_strategies = scalars_strategies.map(scalars_to_points)
points = scalars_strategies.flatmap(scalars_to_points)
scalars_to_segments = compose(methodcaller(Strategy.map.__name__,
                                           pack(Segment)),
                              methodcaller(Strategy.filter.__name__,
                                           pack(ne)),
                              pack(strategies.tuples),
                              duplicate)
segments = points_strategies.flatmap(scalars_to_segments)
segments_pairs = points_strategies.flatmap(compose(pack(strategies.tuples),
                                                   duplicate,
                                                   scalars_to_segments))
