from tests.strategies import (coordinates_strategies,
                              coordinates_to_vectors)
from tests.utils import (to_pairs,
                         to_triplets)

vectors = coordinates_strategies.flatmap(coordinates_to_vectors)
vectors_strategies = coordinates_strategies.map(coordinates_to_vectors)
vectors_pairs = vectors_strategies.flatmap(to_pairs)
vectors_triplets = vectors_strategies.flatmap(to_triplets)
