from tests.strategies import (coordinates_strategies,
                              coordinates_to_multisegments,
                              coordinates_to_points,
                              coordinates_to_segments,
                              invalid_multisegments)
from tests.utils import (cleave_in_tuples,
                         to_pairs,
                         to_triplets)

multisegments = coordinates_strategies.flatmap(coordinates_to_multisegments)
segments = coordinates_strategies.flatmap(coordinates_to_segments)
invalid_multisegments = invalid_multisegments
multisegments_strategies = (coordinates_strategies
                            .map(coordinates_to_multisegments))
multisegments_with_points = coordinates_strategies.flatmap(
        cleave_in_tuples(coordinates_to_multisegments,
                         coordinates_to_points))
multisegments_pairs = multisegments_strategies.flatmap(to_pairs)
multisegments_triplets = multisegments_strategies.flatmap(to_triplets)
