from functools import partial

from hypothesis import strategies
from lz.functional import compose

from tests.strategies import (coordinates_strategies,
                              coordinates_to_points,
                              triangular_contours)
from tests.utils import points_do_not_lie_on_the_same_line

coordinates_to_points_lists = partial(strategies.lists,
                                      unique=True)
points_lists = (coordinates_strategies
                .flatmap(compose(partial(coordinates_to_points_lists,
                                         min_size=3),
                                 coordinates_to_points))
                .filter(points_do_not_lie_on_the_same_line))
non_triangle_points_lists = (
    coordinates_strategies.flatmap(compose(partial(coordinates_to_points_lists,
                                                   min_size=4),
                                           coordinates_to_points)))
triangular_contours = triangular_contours
