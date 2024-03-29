from tests.strategies import (coordinates_strategies,
                              coordinates_to_points,
                              coordinates_to_segments,
                              invalid_segments)
from tests.utils import (cleave_in_tuples,
                         to_pairs,
                         to_triplets)

segments = coordinates_strategies.flatmap(coordinates_to_segments)
invalid_segments = invalid_segments
segments_strategies = coordinates_strategies.map(coordinates_to_segments)
segments_with_points = (coordinates_strategies
                        .flatmap(cleave_in_tuples(coordinates_to_segments,
                                                  coordinates_to_points)))
segments_pairs = segments_strategies.flatmap(to_pairs)
segments_triplets = segments_strategies.flatmap(to_triplets)
