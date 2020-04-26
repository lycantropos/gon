from functools import partial
from operator import (itemgetter,
                      mul)
from typing import (List,
                    Optional)

from hypothesis import strategies
from hypothesis_geometry import planar

from gon.hints import Coordinate
from gon.linear import (Contour,
                        vertices)
from gon.linear.hints import Vertices
from gon.primitive import Point
from tests.utils import Strategy
from .base import coordinates_strategies
from .factories import coordinates_to_points
from .primitive import invalid_points


def to_repeated_points(coordinates: Strategy[Coordinate],
                       min_size: int = vertices.MIN_COUNT,
                       max_size: Optional[int] = None
                       ) -> Strategy[List[Point]]:
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
contours_with_repeated_points = (coordinates_strategies
                                 .flatmap(to_repeated_points)
                                 .map(Contour.from_raw))
