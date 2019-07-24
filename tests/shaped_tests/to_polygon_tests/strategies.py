from functools import partial
from itertools import repeat
from typing import Sequence

from hypothesis import strategies
from lz.logical import negate

from gon.base import Point
from gon.shaped import (self_intersects,
                        vertices_forms_angles)
from tests.strategies import (points_strategies,
                              to_non_triangle_vertices_base)
from tests.utils import Strategy

invalid_vertices = points_strategies.flatmap(to_non_triangle_vertices_base)


def to_same_points(points: Strategy[Point]) -> Strategy[Sequence[Point]]:
    return (strategies.builds(repeat, points,
                              times=strategies.integers(min_value=3,
                                                        max_value=1000))
            .map(list))


invalid_vertices = (points_strategies.flatmap(partial(strategies.lists,
                                                      max_size=2))
                    | points_strategies.flatmap(to_same_points)
                    | invalid_vertices.filter(self_intersects)
                    | invalid_vertices.filter(negate(vertices_forms_angles)))
