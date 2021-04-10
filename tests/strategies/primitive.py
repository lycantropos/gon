import math
from functools import partial
from operator import (itemgetter,
                      mul)
from typing import (List,
                    Optional)

from hypothesis import strategies
from hypothesis_geometry import planar

from gon.base import Point
from gon.raw import RawPoint
from gon.hints import Coordinate
from gon.linear import vertices
from gon.linear.hints import Vertices
from tests.utils import (Strategy,
                         identity)
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


def to_repeated_raw_points(coordinates: Strategy[Coordinate],
                           min_size: int = vertices.MIN_COUNT,
                           max_size: Optional[int] = None
                           ) -> Strategy[List[RawPoint]]:
    return (strategies.lists(planar.points(coordinates),
                             min_size=min_size,
                             max_size=max_size)
            .map(partial(mul, 2))
            .flatmap(strategies.permutations)
            .map(itemgetter(slice(max_size)))
            .filter(not_all_unique))


def not_all_unique(vertices: Vertices) -> bool:
    seen = set()
    seen_add = seen.add
    for value in vertices:
        if value in seen:
            return True
        else:
            seen_add(value)
    return False


repeated_raw_points = coordinates_strategies.flatmap(to_repeated_raw_points)
