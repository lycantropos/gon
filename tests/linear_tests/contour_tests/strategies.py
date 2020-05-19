from functools import partial
from typing import Tuple

from hypothesis import strategies
from hypothesis_geometry import planar

from gon.hints import Coordinate
from gon.linear import (Contour,
                        vertices)
from gon.primitive import Point
from tests.strategies import (coordinates_strategies,
                              coordinates_to_contours,
                              coordinates_to_points,
                              invalid_points,
                              repeated_raw_points)
from tests.utils import (Strategy,
                         to_pairs,
                         to_triplets)

raw_contours = coordinates_strategies.flatmap(planar.contours)
contours = coordinates_strategies.flatmap(coordinates_to_contours)


def coordinates_to_contours_with_points(coordinates: Strategy[Coordinate]
                                        ) -> Strategy[Tuple[Contour, Point]]:
    return strategies.tuples(coordinates_to_contours(coordinates),
                             coordinates_to_points(coordinates))


contours_with_points = (coordinates_strategies
                        .flatmap(coordinates_to_contours_with_points))
small_contours = (
    strategies.builds(Contour,
                      coordinates_strategies
                      .map(coordinates_to_points)
                      .flatmap(partial(strategies.lists,
                                       min_size=1,
                                       max_size=vertices.MIN_COUNT - 1))))
invalid_vertices_contours = strategies.builds(
        Contour,
        strategies.lists(invalid_points,
                         min_size=vertices.MIN_COUNT))
contours_with_repeated_points = repeated_raw_points.map(Contour.from_raw)
invalid_contours = (small_contours
                    | invalid_vertices_contours
                    | contours_with_repeated_points)
contours_strategies = coordinates_strategies.map(coordinates_to_contours)
contours_pairs = contours_strategies.flatmap(to_pairs)
contours_triplets = contours_strategies.flatmap(to_triplets)
