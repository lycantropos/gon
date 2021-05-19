import math
from functools import partial
from operator import (itemgetter,
                      mul)
from typing import (List,
                    Optional,
                    Sequence)

from hypothesis import strategies
from hypothesis_geometry import planar

from gon.base import Point
from gon.core.vertices import MIN_COUNT
from gon.hints import Scalar
from tests.utils import (Strategy,
                         identity,
                         not_all_unique)
from .base import coordinates_strategies
from .factories import coordinates_to_points

points_strategies = coordinates_strategies.map(coordinates_to_points)
points = coordinates_strategies.flatmap(coordinates_to_points)
valid_coordinates = coordinates_strategies.flatmap(identity)
invalid_coordinates = strategies.sampled_from([math.nan, math.inf, -math.inf])
invalid_points = (strategies.builds(Point, valid_coordinates,
                                    invalid_coordinates)
                  | strategies.builds(Point, invalid_coordinates,
                                      valid_coordinates))


def to_repeated_points(coordinates: Strategy[Scalar],
                       *,
                       min_size: int = MIN_COUNT,
                       max_size: Optional[int] = None
                       ) -> Strategy[List[Point]]:
    return (strategies.lists(planar.points(coordinates),
                             min_size=min_size,
                             max_size=max_size)
            .map(partial(mul, 2))
            .flatmap(strategies.permutations)
            .map(itemgetter(slice(max_size)))
            .filter(not_all_unique))


repeated_points = coordinates_strategies.flatmap(to_repeated_points)
