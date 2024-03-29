from tests.strategies import (coordinates_strategies,
                              coordinates_to_multipoints,
                              coordinates_to_points,
                              invalid_multipoints)
from tests.utils import (cleave_in_tuples,
                         to_pairs,
                         to_triplets)

multipoints = coordinates_strategies.flatmap(coordinates_to_multipoints)
invalid_multipoints = invalid_multipoints
multipoints_with_points = (
    coordinates_strategies.flatmap(cleave_in_tuples(coordinates_to_multipoints,
                                                    coordinates_to_points))
)
multipoints_strategies = coordinates_strategies.map(coordinates_to_multipoints)
multipoints_pairs = multipoints_strategies.flatmap(to_pairs)
multipoints_triplets = multipoints_strategies.flatmap(to_triplets)
