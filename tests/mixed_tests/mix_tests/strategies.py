from tests.strategies import (coordinates_strategies,
                              coordinates_to_mixes,
                              coordinates_to_points,
                              coordinates_to_raw_mixes)
from tests.utils import (cleave_in_tuples,
                         to_pairs,
                         to_triplets)

raw_mixes = coordinates_strategies.flatmap(coordinates_to_raw_mixes)
mixes = coordinates_strategies.flatmap(coordinates_to_mixes)
mixes_with_points = (coordinates_strategies
                     .flatmap(cleave_in_tuples(coordinates_to_mixes,
                                               coordinates_to_points)))
mixes_strategies = coordinates_strategies.map(coordinates_to_mixes)
mixes_pairs = mixes_strategies.flatmap(to_pairs)
mixes_triplets = mixes_strategies.flatmap(to_triplets)
