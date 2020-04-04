import math

from hypothesis import strategies
from lz.functional import identity

from gon.hints import Coordinate
from gon.primitive import Point
from tests.utils import Strategy
from .base import coordinates_strategies


def coordinates_to_points(coordinates: Strategy[Coordinate]
                          ) -> Strategy[Point]:
    return strategies.builds(Point, coordinates, coordinates)


points_strategies = coordinates_strategies.map(coordinates_to_points)
points = coordinates_strategies.flatmap(coordinates_to_points)
valid_coordinates = coordinates_strategies.flatmap(identity)
invalid_coordinates = strategies.sampled_from([math.nan, math.inf, -math.inf])
invalid_points = (strategies.builds(Point, valid_coordinates,
                                    invalid_coordinates)
                  | strategies.builds(Point, invalid_coordinates,
                                      valid_coordinates))
