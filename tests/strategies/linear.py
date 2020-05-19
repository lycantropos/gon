from functools import partial

from hypothesis import strategies

from gon.linear import (Contour,
                        vertices)
from .base import coordinates_strategies
from .factories import coordinates_to_points
from .primitive import (invalid_points,
                        repeated_raw_points)

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
contours_with_repeated_points = (repeated_raw_points.map(Contour.from_raw))
