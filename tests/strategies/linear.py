from functools import partial
from itertools import repeat
from typing import (List,
                    Optional,
                    Tuple)

from hypothesis import strategies

from gon.base import (Contour,
                      Multisegment,
                      Segment)
from gon.core import vertices
from tests.utils import (Strategy,
                         lift,
                         segment_to_rotations)
from .base import (coordinates_strategies,
                   empty_sequences)
from .factories import (coordinates_to_points,
                        coordinates_to_segments)
from .primitive import (invalid_points,
                        points,
                        repeated_points)

segments = coordinates_strategies.flatmap(coordinates_to_segments)
invalid_segments = (points.map(lambda point: Segment(point, point))
                    | strategies.builds(Segment, points, invalid_points)
                    | strategies.builds(Segment, invalid_points, points))


def to_pythagorean_triplets(*,
                            min_value: int = 1,
                            max_value: Optional[int] = None
                            ) -> Strategy[Tuple[int, int, int]]:
    if min_value < 1:
        raise ValueError('`min_value` should be positive.')

    def to_increasing_integers_pairs(value: int) -> Strategy[Tuple[int, int]]:
        return strategies.tuples(strategies.just(value),
                                 strategies.integers(min_value=value + 1,
                                                     max_value=max_value))

    def to_pythagorean_triplet(increasing_integers_pair: Tuple[int, int]
                               ) -> Tuple[int, int, int]:
        first, second = increasing_integers_pair
        first_squared = first ** 2
        second_squared = second ** 2
        return (second_squared - first_squared,
                2 * first * second,
                first_squared + second_squared)

    return (strategies.integers(min_value=min_value,
                                max_value=(max_value - 1
                                           if max_value is not None
                                           else max_value))
            .flatmap(to_increasing_integers_pairs)
            .map(to_pythagorean_triplet))


pythagorean_triplets = to_pythagorean_triplets(max_value=1000)


def to_segments_rotations(segments: Strategy[Segment]
                          ) -> Strategy[List[Segment]]:
    return strategies.builds(segment_to_rotations,
                             segments,
                             strategies.lists(to_pythagorean_triplets(),
                                              min_size=1))


def to_repeated_segments(segments: Strategy[Segment]
                         ) -> Strategy[List[Segment]]:
    return (strategies.builds(repeat,
                              segments,
                              times=strategies.integers(2, 100))
            .map(list))


invalid_multisegments = ((empty_sequences
                          | segments.map(lift)
                          | strategies.lists(invalid_segments,
                                             min_size=1)
                          | to_segments_rotations(segments)
                          | to_repeated_segments(segments))
                         .map(Multisegment))
invalid_linear_geometries = invalid_segments | invalid_multisegments
small_contours = (
    strategies.builds(Contour,
                      coordinates_strategies
                      .map(coordinates_to_points)
                      .flatmap(partial(strategies.lists,
                                       min_size=1,
                                       max_size=vertices.MIN_COUNT - 1)))
)
invalid_vertices_contours = strategies.builds(
        Contour,
        strategies.lists(invalid_points,
                         min_size=vertices.MIN_COUNT)
)
contours_with_repeated_points = repeated_points.map(Contour)
invalid_contours = (small_contours
                    | invalid_vertices_contours
                    | contours_with_repeated_points)
