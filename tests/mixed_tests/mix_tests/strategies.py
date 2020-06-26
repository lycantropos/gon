from tests.strategies import (coordinates_strategies,
                              coordinates_to_mixes)
from tests.utils import to_pairs

mixes = coordinates_strategies.flatmap(coordinates_to_mixes)
mixes_strategies = coordinates_strategies.map(coordinates_to_mixes)
mixes_pairs = mixes_strategies.flatmap(to_pairs)
