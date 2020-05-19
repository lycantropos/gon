from functools import partial
from typing import Tuple

from hypothesis import strategies
from hypothesis_geometry import planar
from lz.functional import pack

from gon.discrete import Multipoint
from gon.hints import Coordinate
from gon.primitive import Point
from tests.strategies import (coordinates_strategies,
                              coordinates_to_multipoints,
                              coordinates_to_points, invalid_points,
                              repeated_raw_points)
from tests.utils import (Strategy,
                         to_pairs,
                         to_triplets)

raw_multipoints = (coordinates_strategies.map(planar.points)
                   .flatmap(partial(strategies.lists,
                                    min_size=1,
                                    unique=True)))
multipoints = coordinates_strategies.flatmap(coordinates_to_multipoints)


def coordinates_to_multipoints_with_points(coordinates: Strategy[Coordinate]
                                           ) -> Strategy[Tuple[Multipoint,
                                                               Point]]:
    return strategies.tuples(coordinates_to_multipoints(coordinates),
                             coordinates_to_points(coordinates))


multipoints_with_points = (coordinates_strategies
                           .flatmap(coordinates_to_multipoints_with_points))
empty_multipoints = strategies.builds(Multipoint)
invalid_points_multipoints = (strategies.lists(invalid_points,
                                               min_size=1)
                              .map(pack(Multipoint)))
multipoints_with_repeated_points = repeated_raw_points.map(Multipoint.from_raw)
invalid_multipoints = (empty_multipoints
                       | invalid_points_multipoints
                       | multipoints_with_repeated_points)
multipoints_strategies = coordinates_strategies.map(coordinates_to_multipoints)
multipoints_pairs = multipoints_strategies.flatmap(to_pairs)
multipoints_triplets = multipoints_strategies.flatmap(to_triplets)
