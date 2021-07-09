from hypothesis import strategies

from tests.strategies import (angles,
                              coordinates_strategies,
                              coordinates_to_points,
                              coordinates_to_vectors)
from tests.utils import (cleave_in_tuples,
                         to_pairs,
                         to_triplets)

vectors = coordinates_strategies.flatmap(coordinates_to_vectors)
vectors_strategies = coordinates_strategies.map(coordinates_to_vectors)
vectors_pairs = vectors_strategies.flatmap(to_pairs)
vectors_triplets = vectors_strategies.flatmap(to_triplets)
vectors_with_points = (coordinates_strategies
                       .flatmap(cleave_in_tuples(coordinates_to_vectors,
                                                 coordinates_to_points)))
vectors_points_with_angles = strategies.tuples(vectors_with_points, angles)
vectors_points_with_angles_pairs = strategies.tuples(vectors_with_points,
                                                     angles, angles)
