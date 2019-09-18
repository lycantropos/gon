from gon.hints import Scalar
from gon.linear import Interval
from tests.utils import Strategy
from .base import scalars_strategies_factories


def interval_to_scalars(interval: Interval) -> Strategy[Scalar]:
    coordinates = [interval.start.x, interval.start.y,
                   interval.end.x, interval.end.y]
    coordinates_type, = set(map(type, coordinates))
    strategy_factory = scalars_strategies_factories[coordinates_type]
    return strategy_factory(min_value=min(coordinates),
                            max_value=max(coordinates))
