import sys
from operator import (methodcaller,
                      ne)

from hypothesis import strategies
from lz.functional import (compose,
                           pack)
from lz.replication import duplicate

from gon.base import Point
from gon.hints import Scalar
from tests.utils import Strategy

decimals = strategies.decimals(allow_nan=False,
                               allow_infinity=False)


def has_recoverable_significant_digits_count(number: float) -> bool:
    significant_digits_str = str(number).rstrip('0').rstrip('.').lstrip('-')
    return len(significant_digits_str) <= sys.float_info.dig


floats = (strategies.floats(allow_nan=False,
                            allow_infinity=False)
          .filter(has_recoverable_significant_digits_count))
fractions = strategies.fractions()
scalars_strategies = strategies.sampled_from([decimals, floats, fractions])


def scalars_to_points(scalars: Strategy[Scalar]) -> Strategy[Point]:
    return strategies.builds(Point, scalars, scalars)


points = scalars_strategies.flatmap(scalars_to_points)
scalars_to_segments = compose(methodcaller(Strategy.filter.__name__, pack(ne)),
                              pack(strategies.tuples),
                              duplicate,
                              scalars_to_points)
segments = scalars_strategies.flatmap(scalars_to_segments)
segments_pairs = scalars_strategies.flatmap(compose(pack(strategies.tuples),
                                                    duplicate,
                                                    scalars_to_segments))
