from functools import partial
from operator import (itemgetter,
                      mul)
from typing import Optional

from hypothesis import strategies
from hypothesis_geometry import planar

from gon.hints import Coordinate
from gon.linear import (MIN_VERTICES_COUNT,
                        Contour,
                        Vertices)
from tests.utils import Strategy
from .base import coordinates_strategies
from .primitive import (coordinates_to_points,
                        invalid_points)


def to_contours_with_repeated_points(coordinates: Strategy[Coordinate],
                                     min_size: int = MIN_VERTICES_COUNT,
                                     max_size: Optional[int] = None
                                     ) -> Strategy[Vertices]:
    return (strategies.lists(planar.points(coordinates),
                             min_size=min_size,
                             max_size=max_size)
            .map(partial(mul, 2))
            .flatmap(strategies.permutations)
            .map(itemgetter(slice(max_size)))
            .filter(not_all_unique)
            .map(Contour.from_raw))


def not_all_unique(vertices: Vertices) -> bool:
    seen = set()
    seen_add = seen.add
    for value in vertices:
        if value in seen:
            return True
        else:
            seen_add(value)
    return False


invalid_contours = (
        strategies.builds(Contour,
                          coordinates_strategies
                          .map(coordinates_to_points)
                          .flatmap(partial(strategies.lists,
                                           max_size=MIN_VERTICES_COUNT - 1)))
        | strategies.builds(Contour,
                            strategies.lists(invalid_points))
        | coordinates_strategies.flatmap(to_contours_with_repeated_points))


def coordinates_to_contours(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Contour]:
    return planar.contours(coordinates).map(Contour.from_raw)