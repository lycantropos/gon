from functools import partial
from itertools import repeat
from typing import (List,
                    Optional,
                    Tuple)

from hypothesis import strategies
from hypothesis_geometry import planar
from lz.functional import pack

from gon.linear import (Multisegment,
                        Segment)
from gon.primitive import Point
from tests.strategies import (coordinates_strategies,
                              coordinates_to_multisegments,
                              coordinates_to_points,
                              coordinates_to_segments,
                              invalid_segments)
from tests.utils import (Strategy,
                         cleave_in_tuples,
                         divide_by_int,
                         to_pairs,
                         to_triplets)

raw_multisegments = (coordinates_strategies
                     .flatmap(partial(planar.multisegments,
                                      min_size=1)))
multisegments = raw_multisegments.map(Multisegment.from_raw)


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


def rotate_segment(segment: Segment,
                   pythagorean_triplet: Tuple[int, int, int]) -> Segment:
    area_sine, area_cosine, area = pythagorean_triplet
    center_x, center_y = (divide_by_int(segment.start.x + segment.end.x, 2),
                          divide_by_int(segment.start.y + segment.end.y, 2))
    start_dx, start_dy = segment.start.x - center_x, segment.start.y - center_y
    end_dx, end_dy = segment.end.x - center_x, segment.end.y - center_y
    return Segment(Point(center_x + divide_by_int(area_cosine * start_dx
                                                  - area_sine * start_dy,
                                                  area),
                         center_y + divide_by_int(area_sine * start_dx
                                                  + area_cosine * start_dy,
                                                  area)),
                   Point(center_x + divide_by_int(area_cosine * end_dx
                                                  - area_sine * end_dy,
                                                  area),
                         center_y + divide_by_int(area_sine * end_dx
                                                  + area_cosine * end_dy,
                                                  area)))


def segment_to_rotations(segment: Segment,
                         pythagorean_triplets: List[Tuple[int, int, int]]
                         ) -> List[Segment]:
    return [segment] + [rotate_segment(segment, pythagorean_triplet)
                        for pythagorean_triplet in pythagorean_triplets]


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


segments = coordinates_strategies.flatmap(coordinates_to_segments)
invalid_multisegments = ((strategies.lists(invalid_segments)
                          | to_segments_rotations(segments)
                          | to_repeated_segments(segments))
                         .map(pack(Multisegment)))
multisegments_strategies = (coordinates_strategies
                            .map(coordinates_to_multisegments))
multisegments_with_points = coordinates_strategies.flatmap(
        cleave_in_tuples(coordinates_to_multisegments,
                         coordinates_to_points))
multisegments_pairs = multisegments_strategies.flatmap(to_pairs)
multisegments_triplets = multisegments_strategies.flatmap(to_triplets)
