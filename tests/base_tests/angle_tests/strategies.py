from tests.strategies import (coordinates_strategies,
                              coordinates_to_angles)
from tests.utils import (to_pairs,
                         to_triplets)

angles = coordinates_strategies.flatmap(coordinates_to_angles)
angles_strategies = coordinates_strategies.map(coordinates_to_angles)
angles_pairs = angles_strategies.flatmap(to_pairs)
angles_triplets = angles_strategies.flatmap(to_triplets)
