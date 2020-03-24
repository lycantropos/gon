from tests.strategies import points_strategies
from tests.utils import to_triplets

unique_points_triplets = points_strategies.flatmap(to_triplets)
