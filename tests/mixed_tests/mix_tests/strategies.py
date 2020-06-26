from tests.strategies import (coordinates_strategies,
                              coordinates_to_mixes,
                              coordinates_to_raw_mixes)
from tests.utils import (to_pairs,
                         to_triplets)

raw_mixes = coordinates_strategies.flatmap(coordinates_to_raw_mixes)
mixes = coordinates_strategies.flatmap(coordinates_to_mixes)
mixes_strategies = coordinates_strategies.map(coordinates_to_mixes)
mixes_pairs = mixes_strategies.flatmap(to_pairs)
mixes_triplets = mixes_strategies.flatmap(to_triplets)
