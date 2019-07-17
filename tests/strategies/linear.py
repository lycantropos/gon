from gon.hints import Scalar
from gon.linear import Segment
from tests.utils import Strategy
from .base import scalars_strategies_factories


def segment_to_scalars(segment: Segment) -> Strategy[Scalar]:
    coordinates = [segment.start.x, segment.start.y,
                   segment.end.x, segment.end.y]
    coordinates_type, = set(map(type, coordinates))
    strategy_factory = scalars_strategies_factories[coordinates_type]
    return strategy_factory(min_value=min(coordinates),
                            max_value=max(coordinates))
